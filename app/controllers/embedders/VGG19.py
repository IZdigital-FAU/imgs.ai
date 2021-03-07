from ..embedder import Embedder

import torch as t
import torchvision as tv
import torch.nn as nn
import numpy as np

from util import from_device


class VGG19(Embedder):

    feature_length = 4096
    model = None

    def __init__(self, params={}, keep=False):
        super().__init__(params)
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