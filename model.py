from util import set_cuda, load_img, sort_dict
import numpy as np
import PIL.Image
import os
import csv
import pickle
import json
from annoy import AnnoyIndex
from typing import List, Dict, Any
from nptyping import NDArray


class EmbeddingModel:
    def load(self, model_folder):
        # Load configuration if it exists
        with open(os.path.join(model_folder, "config.json"), "r") as f:
            self.config = json.load(f)
        self.model_folder = model_folder

    def __len__(self):
        return self.config["model_len"]

    def get_nearest_neighbours(
        self,
        emb_type,
        n,
        pos_idxs,
        neg_idxs,
        metric,
        mode="ranking",
        uploads=None,
        search_k=-1,
        limit=None,
    ):

        # Load neighborhood file
        hood_file = os.path.join(
            self.model_folder, self.config["hood_files"][emb_type][metric]
        )
        ann = AnnoyIndex(self.config["dims"][emb_type], metric)
        ann.load(hood_file)

        # Get vectors from indices
        # TYPE-HINTED, expects list of idxs, returns list of 1D arrays
        def vectors_from_idxs(idxs: List[int]) -> List[NDArray[Any]]:
            vectors = []
            for idx in idxs:
                # If idx is larger than model size it belongs to user uploads
                if idx >= len(self):
                    vectors.append(
                        uploads[idx - len(self)].embs[emb_type][0]
                    )  # Make it 1D
                else:
                    vectors.append(ann.get_item_vector(idx))
                return vectors

        nns = []
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
            nns = ann.get_nns_by_vector(
                centroid, n, search_k=search_k, include_distances=False
            )

        elif (
            len(pos_idxs) > 1 and len(neg_idxs) == 0 and mode == "centroid"
        ):  # Centroid
            vectors = np.array(vectors_from_idxs(pos_idxs))
            centroid = vectors.mean(axis=0)
            nns = ann.get_nns_by_vector(
                centroid, n, search_k=search_k, include_distances=False
            )

        elif len(pos_idxs) > 1 and len(neg_idxs) == 0 and mode == "ranking":  # Ranking
            ranking = {}
            for idx in pos_idxs:
                vector = vectors_from_idxs([idx])[0]
                idx_nns, idx_scores = ann.get_nns_by_vector(
                    vector, n, search_k=search_k, include_distances=True
                )
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
            nns = ann.get_nns_by_vector(
                vector, n, search_k=search_k, include_distances=False
            )

        # Unload neighborhood file
        ann.unload()

        # Remove queries from results
        nns = list(set(nns) - set(pos_idxs + neg_idxs))  # Difference of sets

        return nns[:limit] if limit else nns

    def get_metadata(self, idxs, uploads=None, fields=None):
        # Load metadata file
        meta_file = os.path.join(self.model_folder, self.config["meta_file"])
        f = open(meta_file, "r")
        meta = csv.reader(f)

        # Get metadata
        filtered_meta = {}
        for idx in idxs:
            # If idx is larger than model size it belongs to user uploads
            if idx >= len(self):
                path = uploads[idx - len(self)].path
                filtered_meta[idx] = [path, path]
            else:
                # Get remaining model indices
                for i, row in enumerate(meta):
                    if i in idxs:
                        # Always return absolute paths, except for URLs
                        if not row[0].startswith("http"):
                            row[0] = os.path.join(self.config["data_root"], row[0])
                        if fields:
                            filtered_meta[i] = [row[field] for field in fields]
                        else:
                            filtered_meta[i] = row

        # Unload metadata file
        f.close()

        return filtered_meta

    def transform(self, paths):
        device = set_cuda()

        # Load embedders file
        embedders_file = os.path.join(self.model_folder, self.config["embedders_file"])
        f = open(embedders_file, "rb")
        embedders = pickle.load(f)

        # Allocate space
        embs = {}
        for emb_type, embedder in embedders.items():
            embs[emb_type] = np.zeros((len(paths), embedder.feature_length))

        # Extract embeddings
        for i, path in enumerate(paths):
            for emb_type, embedder in embedders.items():
                embs[emb_type][i] = embedder.transform(load_img(path), device)

        # Delete models to save memory
        for emb_type, embedder in embedders.items():
            embedder.model = None  # Delete models to save memory

        # Reduce if reducer given
        for emb_type, embedder in embedders.items():
            if embedder.reducer:
                embs[emb_type] = embedder.reducer.transform(embs[emb_type])

        # Unload embedders file
        f.close()

        return embs
