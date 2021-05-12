from .. import db

from .reducer import Reducer


class Embedder(db.EmbeddedDocument):
    hash = db.StringField(min_length=64, max_length=64)
    name = db.StringField()
    params = db.DictField()
    reducer = db.EmbeddedDocumentField(Reducer)

    def hasReducer(self):
        return bool(self.reducer)