from .. import db
from env import Environment as env
from os.path import join
from util import new_dir


class ImageMetadata(db.DynamicEmbeddedDocument):
    url = db.URLField(unique=1)
    is_stored = db.BooleanField(default=False)

class Reducer(db.EmbeddedDocument):
    name = db.StringField()
    params = db.DictField()

class Embedder(db.EmbeddedDocument):
    name = db.StringField()
    params = db.DictField()
    reducer = db.EmbeddedDocumentField(Reducer)

class Project(db.Document):
    name = db.StringField(unique=1, required=1)
    data = db.EmbeddedDocumentListField(ImageMetadata)
    embedders = db.EmbeddedDocumentListField(Embedder)

    def get_path(self):
        path = join(env.PROJECTS_DIR, self.name)
        new_dir(path)
        return path