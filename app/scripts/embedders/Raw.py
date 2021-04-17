from ..embedder import Embedder
from ..parameters import ParameterCollection

import numpy as np
import PIL.Image


class Raw(Embedder):

    model = None

    def __init__(self, params=ParameterCollection.get('resolution'), keep=False):
        super().__init__(params)

        self.feature_length = self.params['resolution'].value * self.params['resolution'].value * 3
        self.keep = keep


    def transform(self, img, device="cpu"):
        img = img.resize((self.params['resolution'].value, self.params['resolution'].value), PIL.Image.ANTIALIAS)
        output = np.array(img).flatten()
        return output.astype(np.uint8).flatten()