from util import new_dir, set_cuda, image_from_url, load_img
import h5py
from model import EmbeddingModel
from tqdm import tqdm
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


def collect_embed(X, embedders, data_root, num_workers, embs_file):
    device = set_cuda()

    # Allocate space
    print("Allocating space")
    embs = h5py.File(embs_file, "w")
    for emb_type, embedder in embedders.items():
        data = np.zeros((len(X), embedder.feature_length))
        embs.create_dataset(emb_type, compression="lzf", data=data)

    # Set up threading
    pbar_success = tqdm(total=len(X), desc="Embedded")
    pbar_failure = tqdm(total=len(X), desc="Failed")
    q = Queue()
    l = Lock()
    valid_idxs = []

    # Catch interruptions to be able to close file
    def signal_handler(sig, frame):
        print("Shutting down gracefully...")
        embs.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
        embs.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)

    # Define and start queue
    def _worker():
        while True:
            try:
                i, x = q.get(timeout=5)
            except Empty:
                break
            path = x[0]
            success = False
            try:
                if path.startswith("http"):
                    img = image_from_url(path)
                else:
                    img = load_img(os.path.join(data_root, path))
            except:
                img = None
            if img:
                with l:
                    for emb_type, embedder in embedders.items():
                        embs[emb_type][i] = embedder.transform(img, device)
                    valid_idxs.append(i)
                    success = True
            with l:
                if success:
                    pbar_success.update(1)
                else:
                    pbar_failure.update(1)
            q.task_done()

    for i in range(num_workers):
        t = Thread(target=_worker)
        t.daemon = True
        t.start()

    for i, x in enumerate(X):
        q.put((i, x))

    # Cleanup
    q.join()
    pbar_success.close()
    pbar_failure.close()
    embs.create_dataset("valid_idxs", compression="lzf", data=np.array(valid_idxs))
    embs.close()


def train(
    X,
    model_folder,
    embedders,
    data_root,
    num_workers,
    metrics=["angular", "euclidean", "manhattan"],
    n_trees=10,
):

    new_dir(model_folder)

    # Set up
    config = {}
    config["data_root"] = data_root
    config["metrics"] = metrics

    # Create or load raw embeddings
    embs_file = os.path.join(model_folder, "embeddings.hdf5")
    if not os.path.isfile(embs_file):
        collect_embed(X, embedders, data_root, num_workers, embs_file)
    embs = h5py.File(embs_file, "r")
    valid_idxs = list(embs["valid_idxs"])
    config["embs_file"] = "embeddings.hdf5"
    config["model_len"] = len(valid_idxs)

    # Allocate cache
    cache_file = os.path.join(model_folder, "cache.hdf5")
    cache = h5py.File(cache_file, "w")

    # Reduce if reducer given
    print("Reducing dimensions")
    for emb_type, embedder in embedders.items():
        data = embs[emb_type]
        if embedder.reducer:
            data = embedder.reducer.fit_transform(embs[emb_type])
        cache.create_dataset(emb_type, data=data, compression="lzf")

    # Build and save neighborhoods
    print("Building neighborhoods")
    config["hood_files"] = {}
    for emb_type, embedder in embedders.items():
        config["hood_files"][emb_type] = {}
        for metric in metrics:
            if embedder.reducer:
                dims = embedder.reducer.n_components
            else:
                dims = embedder.feature_length
            ann = AnnoyIndex(dims, metric)
            for i, idx in enumerate(valid_idxs):
                ann.add_item(i, cache[emb_type][idx])
            ann.build(n_trees)
            hood_file = os.path.join(model_folder, f"{emb_type}_{metric}.ann")
            ann.save(hood_file)
            config["hood_files"][emb_type][metric] = f"{emb_type}_{metric}.ann"

    # Align and write metadata
    print("Aligning metadata")
    meta = []
    for idx in valid_idxs:
        meta.append(X[idx])
    meta_file = os.path.join(model_folder, "metadata.csv")
    csv.writer(open(meta_file, "w")).writerows(meta)
    config["meta_file"] = "metadata.csv"

    # Save fitted embedders
    print("Writing additional data")
    for emb_type, embedder in embedders.items():
        embedder.model = None  # Delete models to save memory
    embedders_file = os.path.join(model_folder, "embedders.pickle")
    with open(embedders_file, "wb") as f:
        pickle.dump(embedders, f)
    config["embedders_file"] = "embedders.pickle"

    # More config
    config["dims"] = {}
    config["emb_types"] = []
    for emb_type, embedder in embedders.items():
        config["dims"][emb_type] = {}
        config["emb_types"].append(emb_type)
        if embedder.reducer:
            dims = embedder.reducer.n_components
        else:
            dims = embedder.feature_length
        config["dims"][emb_type] = dims

    # Save config
    config_file = os.path.join(model_folder, "config.json")
    with open(config_file, "w") as f:
        json.dump(config, f)

    # Cleanup
    embs.close()
    cache.close()
    os.remove(cache_file)


def make_model(
    model_folder, embedders, source, num_workers=64, shuffle=False, max_data=None
):
    X = []

    if source.endswith(".csv"):
        with open(source, "r") as f:
            meta = csv.reader(f)
            for row in meta:
                file = row[0]
                url = row[1]
                X.append([file, url] + [field for field in row[2:]])
        if shuffle:
            random.shuffle(X)
        if max_data:
            X = X[:max_data]
        train(
            X=X,
            data_root=None,
            model_folder=model_folder,
            embedders=embedders,
            num_workers=num_workers,
        )

    else:
        for root, dirs, files in os.walk(source):
            for file in files:
                X.append(
                    [os.path.relpath(os.path.join(root, file), start=source), "", None]
                )
        if shuffle:
            random.shuffle(X)
        if max_data:
            X = X[:max_data]
        train(
            X=X,
            data_root=source,
            model_folder=model_folder,
            embedders=embedders,
            num_workers=num_workers,
        )
