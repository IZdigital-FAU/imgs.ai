from .. import db


class Reducer(db.EmbeddedDocument):
    name = db.StringField()
    params = db.DictField()