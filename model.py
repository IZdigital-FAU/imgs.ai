from util import set_cuda, load_img, sort_dict, upload_imgs_to, read_csv
import numpy as np
import PIL.Image
import os
import pickle
import json
from annoy import AnnoyIndex
from config import Config
import h5py
import csv


class EmbeddingModel:

    def __init__(self):
        self.model_folder = None
        # Load metadata
        self.metadata = {}
        self.paths = {}
        self.sources = {}
        self.config = {
            'data_location': None, 'distance_metrics': [], 'embs_file': None,
            'model_len': None, 'hood_files': {}, 'meta_file': None,
            'embedders_file': None, 'dims': {}, 'emb_types': []
        }

    def __len__(self):
        return self.config["model_len"]


    def load(self, model_folder):
        
        self.model_folder = model_folder

        # Load configuration
        CONFIG_FPATH = os.path.join(model_folder, "config.json")
        with open(CONFIG_FPATH) as config:
            self.config = json.load(config)

        self.paths, self.sources, self.metadata = read_csv(os.path.join(self.model_folder, self.config["meta_file"]), to_dict=1)


    def extend(self, files):
        # Load uploads file
        uploads_file = os.path.join(self.model_folder, "uploads.hdf5")
        uploads = h5py.File(uploads_file, "a")  # Read/write/create

        paths, idxs = upload_imgs_to(files, Config.UPLOADS_PATH)
        embs = self.transform(paths)

        for i, idx in enumerate(idxs):
            for emb_type in embs:
                uploads.create_dataset(f"{idx}/{emb_type}", compression="lzf", data=embs[emb_type][i])

        # Unload uploads file
        uploads.close()

        return idxs

    def get_nns(self, emb_type, n, pos_idxs, neg_idxs, metric, mode="ranking", search_k=-1, limit=None):
        # Load neighborhood file
        hood_file = os.path.join(self.model_folder, self.config["hood_files"][emb_type][metric])
        ann = AnnoyIndex(self.config["dims"][emb_type], metric)
        ann.load(hood_file)

        # Load uploads file
        uploads_file = os.path.join(self.model_folder, "uploads.hdf5")
        uploads = h5py.File(uploads_file, "a")

        # Get vectors from indices
        def vectors_from_idxs(idxs):
            vectors = []
            for idx in idxs:
                # Index for upload has UUID4 format to make it unique across models
                if idx.startswith("upload"):
                    vectors.append(uploads[idx][emb_type])
                else:
                    vectors.append(ann.get_item_vector(int(idx)))  # Indices are strings
                return vectors

        nns = []

        # Don't try to display more than we have
        n = min(n, len(self))

        # Get nearest neighbors
        if pos_idxs and neg_idxs:  # Arithmetic
            vectors = np.array(vectors_from_idxs(pos_idxs + neg_idxs))
            centroid = vectors.mean(axis=0)
            pos_vectors = np.array(vectors_from_idxs(pos_idxs))
            neg_vectors = np.array(vectors_from_idxs(neg_idxs))

            pos_sum = 0
            for vector in pos_vectors:
                pos_sum += vector
            centroid += pos_sum
            neg_sum = 0
            for vector in neg_vectors:
                neg_sum += vector
            centroid -= neg_sum

            # pos_centroid = pos_vectors.mean(axis=0)
            # neg_centroid = neg_vectors.mean(axis=0)
            # query_vector = pos_centroid - neg_centroid

            nns = ann.get_nns_by_vector(centroid, n, search_k=search_k, include_distances=False)

        elif (len(pos_idxs) > 1 and len(neg_idxs) == 0 and mode == "centroid"):  # Centroid
            vectors = np.array(vectors_from_idxs(pos_idxs))
            centroid = vectors.mean(axis=0)
            nns = ann.get_nns_by_vector(centroid, n, search_k=search_k, include_distances=False)

        elif len(pos_idxs) > 1 and len(neg_idxs) == 0 and mode == "ranking":  # Ranking
            ranking = {}
            for idx in pos_idxs:
                vector = vectors_from_idxs([idx])[0]
                idx_nns, idx_scores = ann.get_nns_by_vector(vector, n, search_k=search_k, include_distances=True)
                for nn, score in zip(idx_nns, idx_scores):
                    # If the neighbor was found already, just update the score
                    if nn in ranking:
                        if ranking[nn] > score:
                            ranking[nn] = score
                    else:
                        ranking[nn] = score
            nns = list(sort_dict(ranking).keys())

        else:  # Single
            vector = vectors_from_idxs(pos_idxs)[0]
            nns = ann.get_nns_by_vector(vector, n, search_k=search_k, include_distances=False)

        # Unload neighborhood file
        ann.unload()

        nns = [str(nn) for nn in nns]  # Indices are strings
        nns = list(set(nns) - set(pos_idxs + neg_idxs))  # Remove queries
        nns = nns[:n]  # Limit to n

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

        # Delete models to save memory
        for emb_type, embedder in embedders.items():
            embedder['data'].model = None  # Delete models to save memory

        # Reduce if reducer given
        for emb_type, embedder in embedders.items():
            if embedder['data'].reducer: embs[emb_type] = embedder['data'].reducer.transform(embs[emb_type])

        # Unload embedders file
        f.close()

        return embs