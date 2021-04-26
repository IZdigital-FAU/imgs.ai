from .. import db

from .reducer import Reducer


class Embedder(db.EmbeddedDocument):
    name = db.StringField()
    params = db.DictField()
    reducer = db.EmbeddedDocumentField(Reducer)

    def hasReducer(self):
        return bool(self.reducer)