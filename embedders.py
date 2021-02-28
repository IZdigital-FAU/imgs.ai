from util import from_device
import numpy as np
import PIL.Image
import torch as t
import torchvision as tv
import torch.nn as nn
import face_recognition
from copy import deepcopy
from collections import defaultdict
from app import log
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


class Parameter:
    def __init__(self, input_type, value, **kwargs):
        self.input_type = input_type # text, password, email, number, url, tel, search, date, datetime, datetime-local, month, week, time, range, color
        self.value = value
        self.meta = kwargs
        
        print(self.__dict__)

class ParameterCollection:
    params = {
        'resolution': Parameter('range', 32, minVal=0, maxVal=100),
        'expected_people': Parameter('range', 2, minVal=1, maxVal=10),
        'minConf': Parameter('range', .9, minVal=0, maxVal=1, step=.1)
    }

    @staticmethod
    def get(*keys):
        return {key: ParameterCollection.params[key] for key in keys}


class Embedder:
    def __init__(self, params):
        self.params = params

    def set_param(self, param, value):
        self.params[param].value = value

    def __str__(self):
        return self.__class__.__name__ + '(' + ', '.join([f'{key}={val}' for key, val in self.__dict__.items()]) + ')'


class Embedder_Raw(Embedder):

    model = None

    def __init__(self, params=ParameterCollection.get('resolution'),
                reducer=None, keep=False):
        super().__init__(params)

        self.feature_length = self.params['resolution'].value * self.params['resolution'].value * 3
        self.reducer = reducer
        self.keep = keep


    def transform(self, img, device="cpu"):
        img = img.resize((self.params['resolution'].value, self.params['resolution'].value), PIL.Image.ANTIALIAS)
        output = np.array(img).flatten()
        return output.astype(np.uint8).flatten()

class Embedder_Face(Embedder):

    feature_length = 128
    model = None

    def __init__(self, params=ParameterCollection.get('expected_people'), reducer=None, keep=False):
        super().__init__(params)
        self.reducer = reducer
        self.keep = keep

    def transform(self, img, device="cpu"):
        faces = face_recognition.face_encodings(np.array(img))
        output = np.mean(faces[: self.params['expected_people'].value], axis=0)  # Average
        return output.astype(np.float32).flatten()


class Embedder_VGG19(Embedder):

    feature_length = 4096
    model = None

    def __init__(self, params={}, reducer=None, keep=False):
        super().__init__(params)
        self.reducer = reducer
        self.keep = keep

    def transform(self, img, device="cpu"):
        if self.model is None:
            # Construct model only on demand
            self.model = tv.models.vgg19(pretrained=True).to(device)
            self.model.classifier = nn.Sequential(
                *list(self.model.classifier.children())[:5]
            )  # VGG19 fc1
            self.model.eval()
            self.transforms = tv.transforms.Compose(
                [tv.transforms.Resize((224, 224)), tv.transforms.ToTensor()]
            )

        with t.no_grad():
            output = self.model(self.transforms(img).unsqueeze(0).to(device))
            return from_device(output).astype(np.float32).flatten()


class Embedder_Poses(Embedder):
    # FIXED BUG: Memory leak when run on CPU (https://github.com/pytorch/pytorch/issues/29809)
    # due to variable input shapes not playing well with Intel MLK,
    # temp. fix: https://github.com/pytorch/pytorch/issues/27971 (and run with jemalloc),
    # see also: https://github.com/pytorch/pytorch/issues/25267

    model = None

    def __init__(self, params=ParameterCollection.get('expected_people', 'minConf'),
                reducer=None, keep=False):

        super().__init__(params)
        self.feature_length = 17 * 2
        self.reducer = reducer
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



class EmbedderFactory:
    
    @staticmethod
    def create(embedder):
        result = False

        if embedder.lower() == 'raw':
            result = Embedder_Raw()
        elif embedder.lower() == 'vgg19':
            result = Embedder_VGG19()
        elif embedder.lower() == 'face':
            result = Embedder_Face()
        elif embedder.lower() == 'poses':
            result = Embedder_Poses()

        return result


class ReducerFactory:
    def create(self, reducer, params):
        result = False

        if reducer.lower() == 'pca':
            result = PCA(**params)
        elif reducer.lower() == 'tsne':
            result = TSNE(**params)

        return result

    def set_params(self, reducer, param, value):
        setattr(reducer, param, value)