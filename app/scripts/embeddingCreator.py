from util import new_dir, image_from_url, load_img, get_img_paths, arrange_data
import h5py
from tqdm import tqdm
from os.path import isfile, join
import os
from os import listdir
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import pickle
import json
import signal
import sys

from rq import get_current_job

import PIL.Image

from random import sample
import numpy as np
from annoy import AnnoyIndex

from env import Environment as env

from ..models.project import Project
from ..models.imagemetadata import ImageMetadata

from ..scripts.embedderFactory import EmbedderFactory
from ..scripts.reducer import ReducerFactory

from ..scripts.NearestNeighborOperator import NearestNeighborOperator


class EmbeddingCreator:

    def __init__(self, projectId, num_workers=64):
        self.num_workers = num_workers

        self.project = Project.objects(pk=projectId).first()
        self.vectorsPath = join(env.VECTORS_DIR, self.project.name)

        new_dir(self.vectorsPath)

        self.n_imgs = self.project.data.count()

        self.embedders = instantiate_embedders(self.project)
        self.embedding_store_fpath = join(self.vectorsPath, 'embedding_store.hdf5')

        self.prepare_embedding_store()


    def prepare_embedding_store(self):
        # log.info("Creating embedding store + allocating space")
        emb_store = h5py.File(self.embedding_store_fpath, 'a')

        for name, embedder in self.embedders.items():
            if name not in emb_store.keys():
                emb_store.create_dataset(name, (self.n_imgs, embedder.feature_length), compression="lzf")

        emb_store.close()


    def extract_vectors(self):
        img_vectors = h5py.File(self.embedding_store_fpath, 'a')
        
        PATH = self.project.get_path()

        reducibles = [name for name in self.embedders]

        for i, img_fname in enumerate(listdir(PATH)):
            img = PIL.Image.open(join(PATH, img_fname)).convert("RGB")

            for name, embedder in self.embedders.items():
                vector = embedder.transform(img)
                img_vectors[name][i] = vector

            job = get_current_job()
            job.meta['progress'] = i + 1
            job.save_meta()
            
        for name in reducibles:
            img_vectors[name] = self.embedders[name].reducer.fit_transform(img_vectors[name])

        img_vectors.close()


    def build_annoy(self, n_trees):
        emb_store = h5py.File(self.embedding_store_fpath)

        # Build and save neighborhoods
        # log.info(f'Building neighborhoods')
        for name, embedder in self.embedders.items():
            if embedder.reducer:
                dims = min(embedder.reducer.n_components, embedder.feature_length)
            else: dims = embedder.feature_length

            for metric in env.ANNOY_DISTANCE_METRICS:
                ann = AnnoyIndex(dims, metric)

                for i in range(self.n_imgs):
                    ann.add_item(i, emb_store[name][i])
                
                ann.build(n_trees)

                hood_fname = f"{name}_{metric}.ann"
                hood_file = join(self.vectorsPath, hood_fname)
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
        hood_file = join(self.vectorsPath, f'{embedder}_{metric}.ann')

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

        embedders[name] = EmbedderFactory.create(name, params)

        if embedder.hasReducer():
            embedders[name].reducer = ReducerFactory.create(embedder.reducer.name, embedder.reducer.params)

    return embedders


"""
def multithread_io():
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
"""