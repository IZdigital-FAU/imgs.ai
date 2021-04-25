from .. import db
from env import Environment as env
from os.path import join
from util import new_dir


class ImageMetadata(db.DynamicEmbeddedDocument):
    pass

class Reducer(db.EmbeddedDocument):
    name = db.StringField()
    params = db.DictField()

class Embedder(db.EmbeddedDocument):
    name = db.StringField()
    params = db.DictField()
    reducer = db.EmbeddedDocumentField(Reducer)

    def hasReducer(self):
        return bool(self.reducer)

class Project(db.Document):
    name = db.StringField(unique=1, required=1)
    # category = db.ListField()
    data = db.EmbeddedDocumentListField(ImageMetadata)
    embedders = db.EmbeddedDocumentListField(Embedder)

    def get_path(self):
        path = join(env.PROJECT_DATA_DIR, self.name)
        new_dir(path)
        return path