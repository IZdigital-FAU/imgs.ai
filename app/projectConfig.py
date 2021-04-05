from os import listdir
from os.path import abspath
import json

from util import get_embedder_names

class ProjectConfig:

    def __init__(self):
        self.data_location = None
        self.distance_metrics = ["angular", "euclidean", "manhattan", "hamming", "dot"] # https://github.com/spotify/annoy#full-python-api
        self.dims = {}
        self.embs_file = ''
        self.model_len = None
        self.hood_files = {}
        self.meta_file = 'metadata.csv'
        self.embedder_serialization_file = 'embedders.pickle'
        self.embs_file = "embeddings.hdf5"
        self.emb_types = get_embedder_names()

    def create(self, kwargs):
        [setattr(self, key, value) for key, value in kwargs.items()]

    def load(self, path):
        with open(path, "r") as config_file:
            data = json.load(config_file)
            print('Data laoded:', data)
            self.create(data)

    def save(self, path):
        with open(path, "w") as config_file: json.dump(self.__dict__, config_file)