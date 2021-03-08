import json


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