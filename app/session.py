import os
import numpy as np
from config import Config
from util import sample_range, fast_base64thumb
from io import BytesIO
import time
import numpy as np
import PIL.Image
from app import models


# Per-user state, deals with server-side models and serialization as client session
class Session:

    size = Config.DEFAULT_SIZE
    n = Config.DEFAULT_N
    mode = Config.DEFAULT_MODE

    def __init__(self, flask_session):
        if "model" in flask_session:
            self.restore(flask_session)
        else:
            self.load_model(Config.MODELS[0])

    def store(self, flask_session):
        flask_session["model"] = self.model
        flask_session["size"] = self.size
        flask_session["mode"] = self.mode
        flask_session["emb_type"] = self.emb_type
        flask_session["metric"] = self.metric
        flask_session["res_idxs"] = self.res_idxs
        flask_session["pos_idxs"] = self.pos_idxs
        flask_session["neg_idxs"] = self.neg_idxs

    def restore(self, flask_session):
        self.model = flask_session["model"]
        self.size = flask_session["size"]
        self.mode = flask_session["mode"]
        self.emb_type = flask_session["emb_type"]
        self.metric = flask_session["metric"]
        self.res_idxs = flask_session["res_idxs"]
        self.pos_idxs = flask_session["pos_idxs"]
        self.neg_idxs = flask_session["neg_idxs"]
        self.load_model_params() # No need to save those

    def load_model(self, model):
        self.model = model
        self.emb_type = models[self.model].config["emb_types"][0]
        self.metric = models[self.model].config["metrics"][0]
        self.res_idxs = []
        self.pos_idxs = []
        self.neg_idxs = []
        self.load_model_params()

    def load_model_params(self):
        self.model_len = models[self.model].config["model_len"]
        self.emb_types = models[self.model].config["emb_types"]
        self.metrics = models[self.model].config["metrics"]

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
            idxs = sample_range(self.model_len, int(self.n))
            self.res_idxs = [str(idx) for idx in idxs]  # Indices are strings

    def render_nns(self):
        # Get metadata and load thumbnails, reset so we do not accumulate data
        metas = {}
        thumbs = {}
        idxs = self.pos_idxs + self.neg_idxs + self.res_idxs
        for idx, meta in models[self.model].get_metadata(idxs).items():
            metas[idx] = meta[1:]
            thumbs[idx] = fast_base64thumb(meta[0], size=int(self.size), axis=0)
        return metas, thumbs
