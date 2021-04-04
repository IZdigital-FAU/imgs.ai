import os
import numpy as np
from util import sample_range
from io import BytesIO
import time
import numpy as np
import PIL.Image
from app import models, log
from env import Environment as environment
from flask import url_for, send_from_directory

# Per-user state, deals with server-side models and serialization as client session
class Session:

    size = environment.DEFAULT_SIZE
    n = environment.DEFAULT_N
    mode = environment.DEFAULT_MODE

    def __init__(self, flask_session):
        if "model" in flask_session:
            self.restore(flask_session)
        else:
            self.load_model(environment.MODELS[0])

    def store(self, flask_session):
        print('here comes the flask session as dict:', flask_session.__dict__)
        flask_session["model"] = self.model
        flask_session["size"] = self.size
        flask_session["mode"] = self.mode
        flask_session["emb_type"] = self.emb_type
        flask_session["metric"] = self.metric
        flask_session["res_idxs"] = self.res_idxs
        flask_session["pos_idxs"] = self.pos_idxs
        flask_session["neg_idxs"] = self.neg_idxs
        flask_session["n"] = self.n


    def restore(self, flask_session):
        self.model = flask_session["model"]
        self.size = flask_session["size"]
        self.mode = flask_session["mode"]
        self.emb_type = flask_session["emb_type"]
        self.metric = flask_session["metric"]
        self.res_idxs = flask_session["res_idxs"]
        self.pos_idxs = flask_session["pos_idxs"]
        self.neg_idxs = flask_session["neg_idxs"]
        self.n = flask_session["n"]
        self.load_model_params() # No need to save those

    def load_model(self, model, pin_idxs=None):

        files = []
        if pin_idxs:
            for idx in pin_idxs:
                root, path, _, _ = self.get_data(idx)
                files.append(os.path.join(root, path))
            log.info(f"Keeping pinned files: {files}")

        self.model = model
        self.load_model_params()
        self.emb_type = self.emb_types[0]
        self.metric = self.distance_metrics[0]
        self.res_idxs = []
        self.pos_idxs = []
        self.neg_idxs = []

        if files: self.extend(files)
        
    def load_model_params(self):
        self.model_len = models[self.model].config["model_len"]
        self.emb_types = models[self.model].config["emb_types"]
        self.distance_metrics = models[self.model].config["distance_metrics"]

        # Hack to always show VGG19 embeddings first, independent of model env file
        if "vgg19" in self.emb_types:
            idx = self.emb_types.index("vgg19")
            self.emb_types.insert(0, self.emb_types.pop(idx))

        # Hack to always show manhattan distance first, independent of model env file
        if "manhattan" in self.distance_metrics:
            idx = self.distance_metrics.index("manhattan")
            self.distance_metrics.insert(0, self.distance_metrics.pop(idx))

    def extend(self, files):
        self.pos_idxs += models[self.model].extend(files)

    def get_nns(self):
        # If we have queries, search nearest neighbors, else display random data points
        # (ignore negative only examples, as results will be random anyway)
        if self.pos_idxs or (self.pos_idxs and self.neg_idxs):
            self.res_idxs = models[self.model].get_nns(
                emb_type=self.emb_type,
                n=int(self.n),
                pos_idxs=self.pos_idxs,
                neg_idxs=self.neg_idxs,
                metric=self.metric,
                mode=self.mode,
            )
        else:
            idxs = []
            k = int(self.n)
            if self.model_len:
                print(self.model_len)
                k = min(k, self.model_len)
                idxs = sample_range(self.model_len, k)
            else:
                idxs = sample_range(k, k)
            self.res_idxs = [str(idx) for idx in idxs]  # Indices are strings

    def render_nns(self):
        # Get metadata and load thumbnails
        popovers = {}
        links = {}
        images = {}
        idxs = self.pos_idxs + self.neg_idxs + self.res_idxs
        for idx in idxs:
            root, path, source, metadata = self.get_data(idx)
            popovers[idx] = "\n".join(metadata) # All but path and source
            links[idx] = source if source else url_for('cdn', idx=idx) # Source or CDN
            images[idx] = path if path.startswith("http") else url_for('cdn', idx=idx) # URL or CDN
        return popovers, links, images

    def get_data(self, idx):
        if idx.startswith("upload"):
            root = environment.UPLOADS_PATH
            path = f"{idx}.jpg"
            source = ""
            metadata = []
        else:
            print('what is path:', models[self.model].paths)
            path = models[self.model].paths[idx]
            if path.startswith("http"):
                root = ""
            else:
                root = models[self.model].config["data_location"]
            source = models[self.model].sources[idx]
            metadata = models[self.model].metadata[idx]
        return root, path, source, metadata