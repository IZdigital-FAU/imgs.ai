import numpy as np
import PIL.Image
import torch as t
from uuid import uuid4
import os
from math import ceil
from random import sample, shuffle
import h5py
from io import BytesIO
import requests
import time
import pybase64
from functools import lru_cache
import csv


@lru_cache(maxsize=100)  # Cache up to 100 images
def fast_base64img(path, load_urls=False):
    if path.startswith("http"):
        if load_urls:
            img = image_from_url(path)
        else:
            return path
    try:
        img = load_img(path)
    except:
        return ""
    out = BytesIO()
    img.save(out, "jpeg")
    img_str = "data:image/jpeg;base64, " + pybase64.b64encode(out.getvalue()).decode("utf-8")

    return img_str


def image_from_url(url, max_tries=10):
    tries = 0
    while tries < max_tries:
        try:
            response = requests.get(url, timeout=30)
            image_bytes = BytesIO(response.content)
            img = PIL.Image.open(image_bytes).convert("RGB")
            return img
        except:
            tries += 1
        time.sleep(1)


def upload_imgs_to(files, folder):
    new_dir(folder)
    idxs = []
    paths = []
    for file in files:
        if isinstance(file, str): # URL or file path
            if file.startswith("http"):
                img = image_from_url(file)
            else:
                img = PIL.Image.open(file).convert("RGB")
        else: # Data stream
            stream = BytesIO(file.read())
            img = PIL.Image.open(stream).convert("RGB")
        idx = f"upload_{str(uuid4())}"
        path = str(os.path.join(folder, f"{idx}.jpg"))
        img.save(path)
        idxs.append(idx)
        paths.append(path)
    return paths, idxs


def sample_range(n, k):
    return sample(list(range(n)), k=k)


def load_img(path):
    return PIL.Image.open(path).convert("RGB")


def sort_dict(d):
    return {k: v for k, v in sorted(d.items(), key=lambda item: item[1])}


def from_device(tensor):
    return tensor.detach().cpu().numpy()


def new_dir(folder):
    os.makedirs(folder, exist_ok=True)
    return folder


def set_cuda():
    device = "cuda" if t.cuda.is_available() else "cpu"
    return device


def arrange_data(X, shuffle=0, max_data=0):
    # log.info('Arrange data')
    if shuffle: shuffle(X)
    if max_data: X = X[:max_data]
    return X


def read_csv(fpath):
    img_metadata = []
    with open(fpath) as csv_file:
        data_table = csv.reader(csv_file)
        for row in data_table:
            if len(row) == 1: img_metadata.append(row); continue
            # else:
            fname = row[0]
            url = row[1]
            img_metadata.append([fname, url] + [field for field in row[2:]])
    
    return img_metadata


def get_img_paths(folder):
    image_data = []
    for root, dirs, files in os.walk(folder):
        for fname in files:
            image_data.append([os.path.abspath(os.path.join(root, fname)), "", None])
    
    return image_data