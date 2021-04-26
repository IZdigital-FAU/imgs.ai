from .. import db
from env import Environment as env
from os.path import join
from util import new_dir

from .imagemetadata import ImageMetadata
from .embedder import Embedder


class Project(db.Document):
    name = db.StringField(unique=1, required=1)
    # category = db.ListField()
    data = db.EmbeddedDocumentListField(ImageMetadata)
    embedders = db.EmbeddedDocumentListField(Embedder)

    def get_path(self):
        path = join(env.PROJECT_DATA_DIR, self.name)
        new_dir(path)
        return path