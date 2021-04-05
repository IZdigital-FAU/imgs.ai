from util import set_cuda, load_img, upload_imgs_to, read_csv, sample_range
import numpy as np
import PIL.Image
import os
import pickle
import json
from annoy import AnnoyIndex
from env import Environment as environment
import h5py
import csv

from .projectConfig import ProjectConfig
from .controllers.NearestNeighborOperator import NearestNeighborOperator


class EmbeddingModel:

    def __init__(self):
        self.model_folder = None
        # Load metadata
        self.metadata = {}
        self.paths = {}
        self.sources = {}
        self.config = ProjectConfig()

    def __len__(self):
        return self.config.model_len


    def load(self, model_folder):
        
        self.model_folder = model_folder

        # Load configuration
        CONFIG_FPATH = os.path.join(model_folder, "config.json")
        self.config.load(CONFIG_FPATH)

        self.paths, self.sources, self.metadata = read_csv(os.path.join(self.model_folder, self.config.meta_file), to_dict=1)


    def extend(self, files):
        # Load uploads file
        uploads_file = os.path.join(self.model_folder, "uploads.hdf5")
        uploads = h5py.File(uploads_file, "a")  # Read/write/create

        paths, idxs = upload_imgs_to(files, environment.UPLOADS_PATH)
        embs = self.transform(paths)

        for i, idx in enumerate(idxs):
            for emb_type in embs:
                uploads.create_dataset(f"{idx}/{emb_type}", compression="lzf", data=embs[emb_type][i])

        # Unload uploads file
        uploads.close()

        return idxs


    def compute_nns(self, emb_type, n, pos_idxs, neg_idxs, metric, mode="ranking", search_k=-1, limit=None):
        # If we have queries, search nearest neighbors, else display random data points
        # (ignore negative only examples, as results will be random anyway)
        n = int(n)
        
        if not pos_idxs:
            idxs = []
            k = min(int(n), self.config.model_len)
            idxs = sample_range(self.config.model_len, k)

            self.res_idxs = [str(idx) for idx in idxs]  # Indices are strings
            return self.res_idxs

        # Load neighborhood file
        hood_file = os.path.join(self.model_folder, self.config.hood_files[emb_type][metric])
        ann = AnnoyIndex(self.config.dims[emb_type], metric)
        ann.load(hood_file)

        # Load uploads file
        uploads_file = os.path.join(self.model_folder, "uploads.hdf5")
        uploads = h5py.File(uploads_file, "a")

        nns = []

        # Don't try to display more than we have
        n = min(n, len(self))

        nnop = NearestNeighborOperator(ann, search_k, uploads, include_distances=1)

        # Get nearest neighbors
        if pos_idxs and neg_idxs: nns = nnop.centroid(pos_idx, neg_idx, n)
        elif mode == "ranking": nns = nnop.ranking(pos_idxs, n)

        # Unload neighborhood file
        ann.unload()

        return nns


    def transform(self, paths):
        device = set_cuda()

        # Load embedders file
        embedders_file = os.path.join(self.model_folder, self.config["embedders_file"])
        f = open(embedders_file, "rb")
        embedders = pickle.load(f)

        # Allocate space
        embs = {}
        for emb_type, embedder in embedders.items():
            embs[emb_type] = np.zeros((len(paths), embedder['data'].feature_length))

        # Extract embeddings
        for i, path in enumerate(paths):
            for emb_type, embedder in embedders.items():
                embs[emb_type][i] = embedder['data'].transform(load_img(path), device)
                embedder['data'].model = None  # Delete models to save memory
                if embedder['data'].reducer: embs[emb_type] = embedder['data'].reducer.transform(embs[emb_type]) # Reduce if reducer given

        # Unload embedders file
        f.close()

        return embs