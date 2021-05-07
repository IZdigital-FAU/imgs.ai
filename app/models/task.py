from .. import db

from .user import User


class Task(db.Document):

    job_id = db.StringField(required=True, unique=True)
    user = db.ReferenceField(User)

    func_name = db.StringField(choices=['extract_vectors', 'build_annoy'])

    status = db.StringField(choices=['queued', 'started', 'deferred', 'finished', 'stopped', 'failed'])
    error = db.StringField()

    started_at = db.DateTimeField()
    enqueued_at = db.DateTimeField()
    ended_at = db.DateTimeField()


    def setup(self, job):
        self.job_id = job.id
        self.func_name = job.func_name
        self.status = job.get_status()

        self.enqueued_at = job.enqueued_at
        self.started_at = job.started_at


    def close(self, job):
        self.error = job.exc_info
        self.status = job.get_status()
        self.ended_at = job.ended_at