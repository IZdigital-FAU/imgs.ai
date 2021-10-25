from collections import defaultdict
from util import sort_dict

import numpy as np

class NearestNeighborOperator:

    def __init__(self, ann, search_k, include_distances):
        self.ann = ann
        
        self.search_k = search_k
        self.include_distances = include_distances
        self.nns = []
        self.scores = []

        self.pos = []
        self.neg = []

    def centroid(self, pos, neg, n):
        self.pos = pos
        self.neg = neg

        vectors = np.array(self.vectors_from_idxs(pos + neg))
        centroid = vectors.mean(axis=0)
        pos_vectors = np.array(self.vectors_from_idxs(pos))
        neg_vectors = np.array(self.vectors_from_idxs(neg))

        centroid += pos_vectors.sum(axis=0)
        centroid -= neg_vectors.sum(axis=0)

        self.nns, self.scores = self.ann.get_nns_by_vector(centroid, n, search_k=self.search_k, include_distances=self.include_distances)

        return self.nns


    def ranking(self, idxs, n):
        ranking = defaultdict()
        for idx in idxs:
            vector = self.vectors_from_idxs([idx])[0]
            self.nns, self.scores = self.ann.get_nns_by_vector(vector, n, search_k=self.search_k, include_distances=self.include_distances)
            for nn, score in zip(self.nns, self.scores):
                # If the neighbor was found already, just update the score
                ranking[nn] = max(ranking[nn], score) if nn in ranking else score

        self.nns = list(sort_dict(ranking).keys())
        self._clean(n)

        return self.nns


    # Get vectors from indices
    def vectors_from_idxs(self, idxs):
        vectors = list(map(lambda idx: self.ann.get_item_vector(idx), idxs))
        return vectors


    def _clean(self, n):
        self.nns = list(set(self.nns) - set(self.pos + self.neg))  # Remove queries
        self.nns = self.nns[:n]  # Limit to n
        return self.nns