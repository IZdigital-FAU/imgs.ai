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


def run_embedders(img_locations, embedders, num_workers, embs_file):
    device = set_cuda()

    # Allocate space
    log.info("Allocating space")
    embs = h5py.File(embs_file, "w")
    for emb_type, embedder in embedders.items():
        log.debug(embedder['data'].feature_length)
        data = np.zeros((len(img_locations), embedder['data'].feature_length))
        log.debug(f'DATA: {data.shape}')
        embs.create_dataset(emb_type.lower(), compression="lzf", data=data)

    # Set up threading
    pbar_success = tqdm(total=len(img_locations), desc="Embedded")
    pbar_failure = tqdm(total=len(img_locations), desc="Failed")
    q = Queue()
    l = Lock()
    valid_idxs = []

    # Catch interruptions to be able to close file
    def signal_handler(sig, frame):
        log.info("Shutting down gracefully...")
        embs.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
        embs.close()
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

            if path.startswith("http"):
                img = image_from_url(path)
            else:
                img = load_img(img_locations[i])

            if img:
                with l:
                    for emb_type, embedder in embedders.items():
                        embs[emb_type.lower()][i] = embedder['data'].transform(img, device)
                    valid_idxs.append(i)
                    success = True
            with l:
                if success: pbar_success.update(1)
                else: pbar_failure.update(1)
            q.task_done()

    for i in range(num_workers):
        t = Thread(target=_worker)
        t.daemon = True
        t.start()

    for i, path in enumerate(img_locations):
        q.put((i, path))

    # Cleanup
    q.join()
    pbar_success.close()
    pbar_failure.close()
    embs.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
    embs.close()


def train(data_location, img_locations, model_folder, embedders, num_workers, distance_metrics=["angular", "euclidean", "manhattan"], n_trees=10):
    log.info(f'Checking {model_folder}')
    new_dir(model_folder)

    # Set up
    log.info(f'Setting up config')
    config = {}
    config["data_location"] = data_location
    config["distance_metrics"] = distance_metrics
    config["dims"] = {}
    config["emb_types"] = []

    # Create or load raw embeddings
    embs_file = join(model_folder, "embeddings.hdf5")
    if not isfile(embs_file):
        run_embedders(img_locations, embedders, num_workers, embs_file)

    embs = h5py.File(embs_file)
    valid_idxs = list(embs["valid_idxs"])
    config["embs_file"] = "embeddings.hdf5"
    config["model_len"] = len(valid_idxs)

    # Allocate cache
    log.info(f'Allocating cache')
    cache_file = join(model_folder, "cache.hdf5")
    cache = h5py.File(cache_file, "w")

    # Reduce if reducer given
    log.info(f'Applying dimensionality reduction')
    for emb_type, embedder in embedders.items():
        data = embs[emb_type.lower()]
        if embedder['data'].reducer:
            data = embedder['data'].reducer.fit_transform(embs[emb_type.lower()])
        cache.create_dataset(emb_type.lower(), data=data, compression="lzf")

    # Build and save neighborhoods
    log.info(f'Building neighborhoods')
    config["hood_files"] = {}
    for emb_type, embedder in embedders.items():
        config["hood_files"][emb_type.lower()] = {}
        config["dims"][emb_type.lower()] = {}
        config["emb_types"].append(emb_type.lower())

        if embedder['data'].reducer:
            dims = embedder['data'].reducer.n_components
        else: dims = embedder['data'].feature_length

        config["dims"][emb_type.lower()] = dims

        for metric in distance_metrics:
            ann = AnnoyIndex(dims, metric)
            for i, idx in enumerate(valid_idxs):
                ann.add_item(i, cache[emb_type.lower()][idx])
            ann.build(n_trees)
            hood_file = join(model_folder, f"{emb_type.lower()}_{metric}.ann")
            ann.save(hood_file)
            config["hood_files"][emb_type.lower()][metric] = f"{emb_type.lower()}_{metric}.ann"

    # Align and write metadata
    log.info(f'Aligning metadata')
    meta = []
    for idx in valid_idxs:
        meta.append([img_locations[idx]])
    meta_file = join(model_folder, "metadata.csv")
    csv.writer(open(meta_file, "w")).writerows(meta)
    config["meta_file"] = "metadata.csv"

    # Save fitted embedders
    log.info("Writing additional data")
    for emb_type, embedder in embedders.items():
        embedder['data'].model = None  # Delete models to save memory
    embedders_file = join(model_folder, "embedders.pickle")
    with open(embedders_file, "wb") as f:
        pickle.dump(embedders, f)
    config["embedders_file"] = "embedders.pickle"

    # Save config
    config_file = join(model_folder, "config.json")
    with open(config_file, "w") as f:
        json.dump(config, f)

    # Cleanup
    embs.close()
    cache.close()
    os.remove(cache_file)


def make_model(model_folder, embedders, data_location, num_workers=64, shuffle=False, max_data=None):
    """Function creates models based on existing image data in the specified `model_folder`"""
    img_locations = []

    if data_location.endswith(".csv"):
        log.info('Reading url metadata')
        img_locations, _sources, _metadata = read_csv(data_location)
    else:
        log.info('Reading local img file paths')
        img_locations = get_img_paths(data_location)

    img_locations = arrange_data(img_locations, shuffle, max_data)

    print('img_locations', img_locations)

    log.info('Start image embedding process')
    train(data_location, img_locations, model_folder, embedders, num_workers)

    log.info('Done')