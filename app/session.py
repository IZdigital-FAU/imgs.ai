import os
import numpy as np
from io import BytesIO
import time
import numpy as np
import PIL.Image
from app import models, log
from env import Environment as environment
from flask import url_for, send_from_directory

# Per-user state, deals with server-side models and serialization as client session
class Session:

    def __init__(self, flask_session):
        self.model = None
        self.size = None
        self.mode = environment.DEFAULT_MODE
        self.emb_type = None
        self.metric = None
        self.res_idxs = []
        self.pos_idxs = []
        self.neg_idxs = []
        self.n = environment.DEFAULT_N

        self.load_model(environment.MODELS[0])

    def read(self, flask_session, *keys):
        if not keys: keys = self.__dict__.keys()
        [setattr(self, key, flask_session[key]) for key in keys]
        self.load_model_params() # No need to save those

    def write(self, flask_session, *keys):
        if not keys: keys = self.__dict__.keys()
        for key in keys: flask_session[key] = getattr(self, key)

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
        self.model_len = models[self.model].config.model_len
        self.emb_types = models[self.model].config.emb_types
        self.distance_metrics = models[self.model].config.distance_metrics

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
        self.res_idxs = models[self.model].compute_nns(
            emb_type=self.emb_type,
            n=self.n,
            pos_idxs=self.pos_idxs,
            neg_idxs=self.neg_idxs,
            metric=self.metric,
            mode=self.mode,
        )

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
            path = models[self.model].paths[idx]
            if path.startswith("http"):
                root = ""
            else:
                root = models[self.model].config.data_location
            source = models[self.model].sources[idx]
            metadata = models[self.model].metadata[idx]
        return root, path, source, metadata