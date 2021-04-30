from env import Environment as env
from util import list_imgs

from ..models.project import Project
from ..models.imagemetadata import ImageMetadata

from os.path import join
from os import listdir


def load_project():
    for project_dir in listdir(env.PROJECT_DATA_DIR):
        if project_dir in [project.name for project in Project.objects().all()] or project_dir.endswith('.zip'):
            print('SKIPPING', project_dir)
            continue

        project = Project(name=project_dir)
        print('SAVING', project_dir)
        PROJECT_PATH = join(env.PROJECT_DATA_DIR, project_dir)

        project.data = [ImageMetadata(**{'name': img}) for img in list_imgs(PROJECT_PATH)]

        project.save()


if __name__ == '__main__':
    load_project()