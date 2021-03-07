from util import new_dir, set_cuda, image_from_url, load_img, get_img_paths, arrange_data, read_csv
import h5py
from model import EmbeddingModel
from tqdm import tqdm
from os.path import isfile, join
import os
import csv
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import pickle
import json
import signal
import sys
import random
import numpy as np
from annoy import AnnoyIndex
from app import log


class ModelConfig:

    def __init__(self):
        self.data_location = None
        self.distance_metrics = ["angular", "euclidean", "manhattan"]
        self.dims = {}
        self.embs_file = ''
        self.model_len = None
        self.hood_files = {}
        self.meta_file = 'metadata.csv'
        self.embedder_serialization_file = 'embedders.pickle'
        self.embs_file = "embeddings.hdf5"
        self.emb_types = []

    def save(self, path):
        with open(path, "w") as config_file: json.dump(self.__dict__, config_file)


class ModelMetadata:

    def __init__(self):
        self.rows = []

    def build(self, valid_idxs, img_locations):
        for idx in valid_idxs:
            self.rows.append([img_locations[idx]])

    def save(self, path):
        csv.writer(open(path, "w")).writerows(self.rows)


class EmbeddingCreator:

    def __init__(self, model_folder, embedders, data_location, num_workers=64, shuffle=False, max_data=None):
        self.device = set_cuda()
        
        self.embedders = embedders
        self.emb_store = {}

        self.model_folder = model_folder
        
        log.info(f'Checking {self.model_folder}')
        new_dir(self.model_folder)

        self.num_workers = num_workers

        self.data_location = data_location
        self.img_locations = []

        if data_location.endswith(".csv"):
            log.info('Reading url metadata')
            self.img_locations, _sources, _metadata = read_csv(data_location)
        else:
            log.info('Reading local img file paths')
            self.img_locations = get_img_paths(data_location)

        self.img_locations = arrange_data(self.img_locations, shuffle, max_data)
        self.n_imgs = len(self.img_locations)

        log.info(f'Setting up project config')
        self.config = ModelConfig()
        self.config.data_location = self.data_location

        self.embs_file = join(self.model_folder, self.config.embs_file)

        self.fresh = 0

        if not isfile(self.embs_file):
            self.fresh = 1
            log.info("Creating embedding store + allocating space")
            self.emb_store = h5py.File(self.embs_file, "w")

            for emb_name, embedder in self.embedders.items():
                data = np.zeros((self.n_imgs, embedder.feature_length))
                self.emb_store.create_dataset(emb_name.lower(), compression="lzf", data=data)


    def train(self, n_trees):
        if self.fresh: self.tqdm_wrap()

        self.emb_store = h5py.File(self.embs_file) # read embedding store
        valid_idxs = list(self.emb_store["valid_idxs"])
        self.config.model_len = len(valid_idxs)

        # Allocate cache
        log.info(f'Allocating cache')
        cache_file = join(self.model_folder, "cache.hdf5")
        cache = h5py.File(cache_file, "w")

        # Reduce if reducer given
        log.info(f'Applying dimensionality reduction')
        for emb_type, embedder in self.embedders.items():
            data = self.emb_store[emb_type.lower()]
            if embedder.reducer:
                data = embedder.reducer.fit_transform(self.emb_store[emb_type.lower()])
            cache.create_dataset(emb_type.lower(), data=data, compression="lzf")

        # Build and save neighborhoods
        log.info(f'Building neighborhoods')
        for emb_type, embedder in self.embedders.items():
            self.config.hood_files[emb_type.lower()] = {}
            self.config.dims[emb_type.lower()] = {}
            self.config.emb_types.append(emb_type.lower())

            if embedder.reducer:
                dims = embedder.reducer.n_components
            else: dims = embedder.feature_length

            self.config.dims[emb_type.lower()] = dims

            for metric in self.config.distance_metrics:
                ann = AnnoyIndex(dims, metric)
                for i, idx in enumerate(valid_idxs):
                    ann.add_item(i, cache[emb_type.lower()][idx])
                ann.build(n_trees)

                hood_fname = f"{emb_type.lower()}_{metric}.ann"
                hood_file = join(self.model_folder, hood_fname)
                ann.save(hood_file)
                self.config.hood_files[emb_type.lower()][metric] = hood_fname

        # Align and write metadata
        log.info(f'Aligning metadata')
        metadata = ModelMetadata()
        metadata.build(valid_idxs, self.img_locations)
        metadata.save(join(self.model_folder, "metadata.csv"))

        self.serialize_embedders()

        # Save config
        self.config.save(join(self.model_folder, "config.json"))

        # Cleanup
        self.emb_store.close()
        cache.close()
        os.remove(cache_file)


    def tqdm_wrap(self):
        # Set up threading
        pbar_success = tqdm(total=self.n_imgs, desc="Embedded")
        pbar_failure = tqdm(total=self.n_imgs, desc="Failed")

        lock = Lock()
        valid_idxs = []

        # Catch interruptions to be able to close file
        def signal_handler(sig, frame):
            log.info("Shutting down gracefully...")
            self.emb_store.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
            self.emb_store.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # img I/O multithreading
        def _worker(item):
            i, img_url = item
            img = image_from_url(img_url)

            with lock:
                if img:
                    valid_idxs.append(i)
                    pbar_success.update(1)
                
                    for emb_type, embedder in self.embedders.items():
                        self.emb_store[emb_type.lower()][i] = embedder.transform(img, self.device)
    
                else: pbar_failure.update(1)


        with ThreadPoolExecutor(self.num_workers) as executor:
            log.debug(f'Multithreading on {executor._max_workers} workers')
            executor.map(_worker, enumerate(self.img_locations))

        # Cleanup
        pbar_success.close()
        pbar_failure.close()
        self.emb_store.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
        self.emb_store.close()


    def serialize_embedders(self):
        # Save fitted embedders
        log.info("Writing additional data")
        for embedder in self.embedders.values():
            embedder.model = None  # Delete pretrained pytorch models to save memory

        embedders_file = join(self.model_folder, self.config.embedder_serialization_file)
        with open(embedders_file, "wb") as f:
            pickle.dump(self.embedders, f)