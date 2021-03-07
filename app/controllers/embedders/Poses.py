from ..embedder import Embedder
from ..parameters import ParameterCollection

from util import from_device

import torch as t
import torchvision as tv

import numpy as np


class Poses(Embedder):
    # FIXED BUG: Memory leak when run on CPU (https://github.com/pytorch/pytorch/issues/29809)
    # due to variable input shapes not playing well with Intel MLK,
    # temp. fix: https://github.com/pytorch/pytorch/issues/27971 (and run with jemalloc),
    # see also: https://github.com/pytorch/pytorch/issues/25267

    model = None

    def __init__(self, params=ParameterCollection.get('expected_people', 'minConf'), keep=False):

        super().__init__(params)
        self.feature_length = 17 * 2
        self.keep = keep

    def _normalize_keypoints(self, keypoints, scores):

        all_keypoints_scaled = np.zeros((self.params['expected_people'], 17 * 2))

        people_count = 0
        for person, person_keypoints in enumerate(keypoints):  # Already ranked by score
            score = scores[person].item()
            if self.params['min_score'] is None or score > self.params['min_score']:
                # Scale w.r.t exact bounding box
                min_x = min([person_keypoint[0] for person_keypoint in person_keypoints])
                max_x = max([person_keypoint[0] for person_keypoint in person_keypoints])
                min_y = min([person_keypoint[1] for person_keypoint in person_keypoints])
                max_y = max([person_keypoint[1] for person_keypoint in person_keypoints])

                person_keypoints_scaled = []
                for person_keypoint in person_keypoints:
                    if max_x > min_x > 0 and max_y > min_y > 0:  # Failsafe
                        scaled_x = (person_keypoint[0] - min_x) / (max_x - min_x)
                        scaled_y = (person_keypoint[1] - min_y) / (max_y - min_y)
                        person_keypoints_scaled.extend([scaled_x, scaled_y])
                all_keypoints_scaled[people_count] = person_keypoints_scaled
                people_count += 1
                if people_count == self.expected_people:
                    break

        return np.mean(all_keypoints_scaled, axis=0)  # Average

    def transform(self, img, device="cpu"):
        if self.model is None:
            # Construct model only on demand
            self.model = tv.models.detection.keypointrcnn_resnet50_fpn(pretrained=True).to(device)
            self.model = self.model
            self.model.eval()
            self.transforms = tv.transforms.Compose([tv.transforms.ToTensor()])

        with t.no_grad():
            output = self.model(self.transforms(img).unsqueeze(0).to(device))
            scores = from_device(output[0]["scores"])
            keypoints = from_device(output[0]["keypoints"])
            normalized_keypoints = self._normalize_keypoints(keypoints, scores)
            return normalized_keypoints.astype(np.float32).flatten()