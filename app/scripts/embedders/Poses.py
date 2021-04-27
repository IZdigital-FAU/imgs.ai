from ..embedder import Embedder
from ..parameters import ParameterCollection

from util import from_device

import torch as t
import torchvision as tv

import numpy as np

from util import set_cuda


class Poses(Embedder):
    # FIXED BUG: Memory leak when run on CPU (https://github.com/pytorch/pytorch/issues/29809)
    # due to variable input shapes not playing well with Intel MLK,
    # temp. fix: https://github.com/pytorch/pytorch/issues/27971 (and run with jemalloc),
    # see also: https://github.com/pytorch/pytorch/issues/25267

    model = None

    def __init__(self, params=ParameterCollection.get('expected_people', 'minConf'), keep=False):

        super().__init__(params)
        self.n_keypoints = 17
        self.feature_length = self.n_keypoints * 2  # KeyPoint(x, y)
        self.keep = keep

    def _normalize_keypoints(self, keypoints, scores):

        normalized_keypoints = np.zeros((scores.shape[0], self.n_keypoints, 2))

        # Exact bounding box (differs from output[0]['boxes'] !)
        min_x = keypoints.min(axis=1)[:, 0]
        max_x = keypoints.max(axis=1)[:, 0]
        min_y = keypoints.min(axis=1)[:, 1]
        max_y = keypoints.max(axis=1)[:, 1]

        normalized_keypoints[:, :, 0] = ((keypoints[:, :, 0].T - min_x) / (max_x - min_x)).T
        normalized_keypoints[:, :, 1] = ((keypoints[:, :, 1].T - min_y) / (max_y - min_y)).T

        normalized_keypoints = normalized_keypoints.reshape(scores.shape[0], self.feature_length)
        normalized_keypoints = (normalized_keypoints.T * scores).T

        weighted_average = np.mean(normalized_keypoints, axis=0)

        return weighted_average


    def build(self, device='cpu'):
        print('init model')
        self.device = device
        self.model = tv.models.detection.keypointrcnn_resnet50_fpn(pretrained=True).to(device)
        self.model.eval()
        self.transforms = tv.transforms.Compose([tv.transforms.ToTensor()])


    def transform(self, img):
        if not self.model: self.build(set_cuda())

        with t.no_grad():
            output = self.model(self.transforms(img).unsqueeze(0).to(self.device))
            scores = from_device(output[0]["scores"])
            keypoints = from_device(output[0]["keypoints"])
            normalized_keypoints = self._normalize_keypoints(keypoints, scores)
            return normalized_keypoints.astype(np.float32).flatten()