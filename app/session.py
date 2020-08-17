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
    res_idxs = []
    pos_idxs = []
    neg_idxs = []

    def __init__(self, model=Config.MODELS[0]):
        self.model = model
        self.load_model_params()

    def load_model_params(self):
        self.model_len = models[self.model].config["model_len"]
        self.emb_types = models[self.model].config["emb_types"]
        self.emb_type = models[self.model].config["emb_types"][0]
        self.metrics = models[self.model].config["metrics"]
        self.metric = models[self.model].config["metrics"][0]

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

    # Serialize to redis o.Ä.
    # def store():
    # def load():


session = Session()
