from util import new_dir, set_cuda, image_from_url, load_img, get_img_paths, arrange_data, read_csv
import h5py
from model import EmbeddingModel
from tqdm import tqdm
from os.path import isfile, join
import os
import csv
from threading import Lock, Thread
from queue import Queue, Empty
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
        self.embedders_file = 'embedders.pickle'
        self.embs_file = "embeddings.hdf5"
        self.emb_types = []

    def save(self, path):
        with open(path, "w") as config_file: json.dump(self.__dict__, config_file)


class ModelMetadata:

    def __init__(self):
        self.rows = []

    def save(self, path):
        csv.writer(open(path, "w")).writerows(self.rows)


class EmbeddingCreator:

    def __init__(self, model_folder, embedders, data_location, num_workers=64, shuffle=False, max_data=None):
        self.device = set_cuda()
        
        self.embedders = embedders
        self.emb_store = {}
        self.embs_file = None

        self.model_folder = model_folder
        self.data_location = data_location
        self.img_locations = []
        
        log.info(f'Checking {self.model_folder}')
        new_dir(self.model_folder)

        self.num_workers = num_workers

        if data_location.endswith(".csv"):
            log.info('Reading url metadata')
            self.img_locations, _sources, _metadata = read_csv(data_location)
        else:
            log.info('Reading local img file paths')
            self.img_locations = get_img_paths(data_location)

        self.img_locations = arrange_data(self.img_locations, shuffle, max_data)

        log.info(f'Setting up config')
        self.config = ModelConfig()
        self.config.data_location = self.data_location

        self.embs_file = join(self.model_folder, "embeddings.hdf5")

        if not isfile(self.embs_file):
            log.info("Creating embedding store + allocating space")
            self.emb_store = h5py.File(self.embs_file, "w")

            for emb_type, embedder in self.embedders.items():
                data = np.zeros((len(self.img_locations), embedder['data'].feature_length))
                self.emb_store.create_dataset(emb_type.lower(), compression="lzf", data=data)


    def train(self, n_trees):
        self.tqdm_wrap()

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
            if embedder['data'].reducer:
                data = embedder['data'].reducer.fit_transform(self.emb_store[emb_type.lower()])
            cache.create_dataset(emb_type.lower(), data=data, compression="lzf")

        # Build and save neighborhoods
        log.info(f'Building neighborhoods')
        for emb_type, embedder in self.embedders.items():
            self.config.hood_files[emb_type.lower()] = {}
            self.config.dims[emb_type.lower()] = {}
            self.config.emb_types.append(emb_type.lower())

            if embedder['data'].reducer:
                dims = embedder['data'].reducer.n_components
            else: dims = embedder['data'].feature_length

            self.config.dims[emb_type.lower()] = dims

            for metric in self.config.distance_metrics:
                ann = AnnoyIndex(dims, metric)
                for i, idx in enumerate(valid_idxs):
                    ann.add_item(i, cache[emb_type.lower()][idx])
                ann.build(n_trees)
                hood_file = join(self.model_folder, f"{emb_type.lower()}_{metric}.ann")
                ann.save(hood_file)
                self.config.hood_files[emb_type.lower()][metric] = f"{emb_type.lower()}_{metric}.ann"

        # Align and write metadata
        log.info(f'Aligning metadata')
        metadata = ModelMetadata()
        for idx in valid_idxs:
            metadata.rows.append([self.img_locations[idx]])
        metadata.save(join(self.model_folder, "metadata.csv"))

        # Save fitted embedders
        log.info("Writing additional data")
        for emb_type, embedder in self.embedders.items():
            embedder['data'].model = None  # Delete models to save memory
        embedders_file = join(self.model_folder, "embedders.pickle")
        with open(embedders_file, "wb") as f:
            pickle.dump(self.embedders, f)
        self.config.embedders_file = "embedders.pickle"

        # Save config
        self.config.save(join(self.model_folder, "config.json"))

        # Cleanup
        self.emb_store.close()
        cache.close()
        os.remove(cache_file)


    def tqdm_wrap(self):
        # Set up threading
        pbar_success = tqdm(total=len(self.img_locations), desc="Embedded")
        pbar_failure = tqdm(total=len(self.img_locations), desc="Failed")
        q = Queue()
        l = Lock()
        valid_idxs = []

        # Catch interruptions to be able to close file
        def signal_handler(sig, frame):
            log.info("Shutting down gracefully...")
            self.emb_store.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
            self.emb_store.close()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Define and start queue
        def _worker():
            while True:
                try:
                    i, path = q.get(timeout=5)
                except Empty:
                    break

                success = False
                img = None

                img = image_from_url(path) if path.startswith('http') else load_img(self.img_locations[i])

                if img:
                    with l:
                        log.info('Start image embedding process')
                        for emb_type, embedder in self.embedders.items():
                            self.emb_store[emb_type.lower()][i] = embedder['data'].transform(img, self.device)

                        valid_idxs.append(i)
                        success = True
                with l:
                    pbar_success.update(1) if success else pbar_failure.update(1)

                q.task_done()

        for i in range(self.num_workers):
            t = Thread(target=_worker)
            t.daemon = True
            t.start()

        for i, path in enumerate(self.img_locations):
            q.put((i, path))

        # Cleanup
        q.join()
        pbar_success.close()
        pbar_failure.close()
        self.emb_store.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
        self.emb_store.close()
