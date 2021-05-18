from .. import db


class ImageMetadata(db.DynamicEmbeddedDocument):
    name = db.StringField()
    # project_id = db.ReferenceField(Project)
    features = db.ListField()