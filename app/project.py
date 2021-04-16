from util import set_cuda, load_img, upload_imgs_to, sample_range, new_dir
import numpy as np
import PIL.Image
from os.path import join
import pickle
import json
from annoy import AnnoyIndex
from env import Environment as environment
import h5py
import csv

from .controllers.NearestNeighborOperator import NearestNeighborOperator


class Project:

    def __init__(self, name):
        self.name = name
        self.dirpath = join(environment.PROJECTS_DIR, name)
        new_dir(self.dirpath)

    def __len__(self):
        return self.config.model_len

    def load(self):
        # Load configuration
        self.config.load(join(self.dirpath, 'config.json'))

    def todict(self):
        return {'name': self.name}


    def extend(self, files):
        # Load uploads file
        uploads_file = os.path.join(self.dirpath, "uploads.hdf5")
        uploads = h5py.File(uploads_file, "a")  # Read/write/create

        paths, idxs = upload_imgs_to(files, environment.UPLOADS_PATH)
        embs = self.transform(paths)

        for i, idx in enumerate(idxs):
            for emb_type in embs:
                uploads.create_dataset(f"{idx}/{emb_type}", compression="lzf", data=embs[emb_type][i])

        # Unload uploads file
        uploads.close()

        return idxs


    def transform(self, paths):
        device = set_cuda()

        # Load embedders file
        embedders_file = os.path.join(self.dirpath, self.config["embedders_file"])
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