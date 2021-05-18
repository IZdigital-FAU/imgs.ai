from env import Environment as env
from util import list_imgs

from ..models.project import Project
from ..models.imagemetadata import ImageMetadata

from os.path import join
from os import listdir
import os


def load_project():
    for project_dir in listdir(env.PROJECT_DATA_DIR):
        if project_dir in [project.name for project in Project.objects().all()] or project_dir.endswith('.zip'):
            continue

        project = Project(name=project_dir)
        PROJECT_PATH = join(env.PROJECT_DATA_DIR, project_dir)

        imgs = list_imgs(PROJECT_PATH)

        if len(imgs) == 0:
            continue

        project.data = [ImageMetadata(**{'name': img}) for img in imgs]
        project.save()

        os.makedirs(join(env.VECTORS_DIR, project.name), exist_ok=True)


if __name__ == '__main__':
    load_project()