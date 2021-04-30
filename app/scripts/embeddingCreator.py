from util import new_dir, image_from_url, load_img, get_img_paths, arrange_data, list_imgs
from flask import url_for
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

            if embedder.hasReducer():
                name = make_reducer_name(name, embedder)
                
                if name not in emb_store.keys():
                    dims = self.getDims(embedder)
                    emb_store.create_dataset(name, (self.n_imgs, dims), compression="lzf")

        emb_store.close()


    def extract_vectors(self):
        emb_store = h5py.File(self.embedding_store_fpath, 'r+')
        
        PATH = self.project.get_path()

        reducibles = [name for name, embedder in self.embedders.items()]

        job = get_current_job()

        for i, img_fname in list_imgs(PATH, enum=1):
            print(img_fname)
            img = PIL.Image.open(join(PATH, img_fname)).convert("RGB")

            for name, embedder in self.embedders.items():
                vector = embedder.transform(img)
                emb_store[name][i] = vector

            job.meta['progress'] = i + 1
            job.save_meta()
            
        for name in reducibles:
            reducer_name = make_reducer_name(name, embedder)

            print(name, emb_store[name])
            print(not np.any(emb_store[name][:]))

            emb_store[reducer_name][:] = self.embedders[name].reducer.fit_transform(emb_store[name])

        emb_store.close()



    def build_annoy(self, n_trees):
        emb_store = h5py.File(self.embedding_store_fpath, 'r')

        # Build and save neighborhoods
        # log.info(f'Building neighborhoods')
        for name, embedder in self.embedders.items():
            if embedder.hasReducer():
                name = make_reducer_name(name, embedder)

            dims = emb_store[name].shape[1] 

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
        
        n = int(n)
        k = min(n, self.n_imgs)

        if not pos:
            return sample([{'id': i, 'url': make_img_url(self.project.id, img.name)} for i, img in enumerate(self.project.data)], k)

        # Load neighborhood file
        hood_file = join(self.vectorsPath, f'{embedder}_{metric}.ann')

        embedder_name, reducer_name = embedder.split('_')
        print('EMBEDDERS', self.embedders)
        dim = self.embedders[embedder_name].reducer.n_components if self.embedders[embedder_name].hasReducer() else self.embedders[embedder_name].feature_length

        ann = AnnoyIndex(dim, metric)
        ann.load(hood_file)

        nns = []

        nnop = NearestNeighborOperator(ann, search_k=-1, include_distances=1)

        # Get nearest neighbors
        if pos and neg: nns = nnop.centroid(pos, neg, k)
        elif mode == "ranking": nns = nnop.ranking(pos, k)

        # Unload neighborhood file
        ann.unload()

        return [{'id': i, 'url': make_img_url(self.project.id, img.name)} for i, img in enumerate(self.project.data) if i in nns]


    def getDims(self, embedder):
        return min(embedder.reducer.n_components, embedder.feature_length, self.n_imgs) if embedder.reducer else embedder.feature_length


def instantiate_embedders(project):
    embedders = {}

    for embedder in project.embedders:
        name = embedder['name']
        params = embedder['params']

        embedders[name] = EmbedderFactory.create(name, params)

        if embedder.hasReducer():
            embedder.reducer.params['n_components'] = min(embedder.reducer.params['n_components'], project.data.count())
            embedders[name].reducer = ReducerFactory.create(embedder.reducer.name, embedder.reducer.params)

    return embedders


def make_reducer_name(name, embedder):
    return f'{name}_{embedder.reducer.__class__.__name__}'


def make_img_url(id, name):
    return url_for('api.fetch_img', pid=id, img=name)

"""
def multithread_io():
    emb_store = h5py.File(self.embedding_store_fpath, 'a')

    # Set up threading
    pbar_success = tqdm(total=self.n_imgs, desc="Embedded")
    pbar_failure = tqdm(total=self.n_imgs, desc="Failed")

    lock = Lock()

    # Catch interruptions to be able to close file
    def signal_handler(sig, frame):
        log.info("Shutting down gracefully...")
        emb_store.close()
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

                    emb_store[name][i] = vector

            else:
                print('FAILED IMG', item['url'])
                pbar_failure.update(1)

    with ThreadPoolExecutor(self.num_workers) as executor:
        # log.debug(f'Multithreading on {executor._max_workers} workers')
        executor.map(_worker, enumerate(self.project.data))

    # Cleanup
    pbar_success.close()
    pbar_failure.close()
    emb_store.close()
"""