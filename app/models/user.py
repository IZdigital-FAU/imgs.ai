from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from datetime import datetime
from logger import log

from .. import db

from .project import Project


class User(UserMixin, db.Document):
    name = db.StringField(required=True)
    email = db.EmailField(required=True)
    secret = db.StringField(required=True, min_length=80, max_length=80)
    role = db.StringField(choices=['admin', 'user'])

    projects = db.ListField(db.ReferenceField(Project))

    created = db.DateTimeField()
    last_login = db.DateTimeField()

    def set_password(self, password):
        self.secret = generate_password_hash(password, method="sha256")

    def verify(self, secret):
        return check_password_hash(self.secret, secret)

    def __repr__(self):
        return f"{self.username} ({self.email})"


def create_user(form):
    user = User(name=form['name'], email=form['email'], role='user', created=datetime.now())
    user.set_password(form['secret'])
    user.save()

    return user