from .. import db

class ImageMetadata(db.DynamicEmbeddedDocument):
    features = db.ListField()
    pass