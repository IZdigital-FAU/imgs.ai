from ..embedder import Embedder
from ..parameters import ParameterCollection

import face_recognition
import numpy as np


class Face(Embedder):

    feature_length = 128
    model = None

    def __init__(self, params=ParameterCollection.get('expected_people'), keep=False):
        super().__init__(params)
        self.keep = keep

    def transform(self, img, device="cpu"):
        faces = face_recognition.face_encodings(np.array(img))
        output = np.mean(faces[: self.params['expected_people'].value], axis=0)  # Average
        return output.astype(np.float32).flatten()