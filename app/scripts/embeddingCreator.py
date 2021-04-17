from util import new_dir, set_cuda, image_from_url, load_img, get_img_paths, arrange_data
import h5py
from tqdm import tqdm
from os.path import isfile, join
import os
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import pickle
import json
import signal
import sys

from random import sample
import numpy as np
from annoy import AnnoyIndex

from env import Environment as env
from ..models.imagemetadata import Project, ImageMetadata

from ..scripts.embedderFactory import EmbedderFactory
from ..scripts.NearestNeighborOperator import NearestNeighborOperator


class EmbeddingCreator:

    def __init__(self, projectId, num_workers=64):
        self.device = set_cuda()

        self.num_workers = num_workers

        self.project = Project.objects(id=projectId).first()
        self.projectPath = join(env.PROJECTS_DIR, self.project.name)

        self.n_imgs = len(self.project.data)

        self.embedders = instantiate_embedders(self.project)
        self.embedding_store_fpath = join(self.projectPath, 'embedding_store.hdf5')

        if not isfile(self.embedding_store_fpath):
            self.create_embedding_store()


    def create_embedding_store(self):
        # log.info("Creating embedding store + allocating space")
        emb_store = h5py.File(self.embedding_store_fpath, 'w')

        for name, embedder in self.embedders.items():
            emb_store.create_dataset(name, (self.n_imgs, embedder.feature_length), compression="lzf")

        emb_store.close()


    def extract_vectors(self):
        img_vectors = h5py.File(self.embedding_store_fpath, 'a')

        # Set up threading
        pbar_success = tqdm(total=self.n_imgs, desc="Embedded")
        pbar_failure = tqdm(total=self.n_imgs, desc="Failed")

        lock = Lock()

        # Catch interruptions to be able to close file
        def signal_handler(sig, frame):
            log.info("Shutting down gracefully...")
            img_vectors.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # img I/O multithreading
        def _worker(item):
            i, item = item
            img = image_from_url(item.url)

            with lock:
                if img:
                    pbar_success.update(1)

                    self.project.update(**{f'set__data__{i}__is_stored': True})

                    for name, embedder in self.embedders.items():
                        vector = embedder.transform(img, self.device)

                        if embedder.reducer:
                            vector = embedder.reducer.obj.fit_transform(vector)

                        img_vectors[name][i] = vector

                else:
                    print('FAILED IMG', item['url'])
                    pbar_failure.update(1)

        with ThreadPoolExecutor(self.num_workers) as executor:
            # log.debug(f'Multithreading on {executor._max_workers} workers')
            executor.map(_worker, enumerate(self.project.data))

        # Cleanup
        pbar_success.close()
        pbar_failure.close()
        img_vectors.close()


    def build_annoy(self, n_trees):
        emb_store = h5py.File(self.embedding_store_fpath)

        # Build and save neighborhoods
        # log.info(f'Building neighborhoods')
        for name, embedder in self.embedders.items():
            if embedder.reducer:
                dims = embedder.reducer.n_components
            else: dims = embedder.feature_length

            self.project.reload()

            stored = self.project.data.filter(is_stored=True)

            for metric in env.ANNOY_DISTANCE_METRICS:
                ann = AnnoyIndex(dims, metric)

                for i, item in enumerate(stored):
                    ann.add_item(i, emb_store[name][i])
                
                ann.build(n_trees)

                hood_fname = f"{name}_{metric}.ann"
                hood_file = join(self.projectPath, hood_fname)
                ann.save(hood_file)

        # Cleanup
        emb_store.close()


    def compute_nns(self, embedder, pos, neg, n, metric, mode="ranking"):
        # If we have queries, search nearest neighbors, else display random data points
        # (ignore negative only examples, as results will be random anyway)
        
        stored = self.project.data.filter(is_stored=True)
        
        n = int(n)
        k = min(n, self.n_imgs, len(stored))

        if not pos:
            return sample([{'id': i, 'url': img.url} for i, img in enumerate(stored)], k)

        # Load neighborhood file
        hood_file = join(self.projectPath, f'{embedder}_{metric}.ann')

        dim = self.embedders[embedder].reducer.n_components if self.embedders[embedder].reducer else self.embedders[embedder].feature_length

        ann = AnnoyIndex(dim, metric)
        ann.load(hood_file)

        nns = []

        nnop = NearestNeighborOperator(ann, search_k=-1, include_distances=1)

        # Get nearest neighbors
        if pos and neg: nns = nnop.centroid(pos, neg, k)
        elif mode == "ranking": nns = nnop.ranking(pos, k)

        # Unload neighborhood file
        ann.unload()

        return [{'id': i, 'url': img.url} for i, img in enumerate(stored) if i in nns]


def instantiate_embedders(project):
    embedders = {}

    for embedder in project.embedders:
        name = embedder['name']
        params = embedder['params']

        embedders[embedder.name] = EmbedderFactory.create(embedder.name)

        for param in params:
            embedders[name].set_param(param, params[param])

        if embedder['reducer']:
            embedders[name].reducer.active = True
            embedders[name].reducer.be(embedder['reducer']['name'], embedder['reducer']['params'])

    return embedders