from .. import db

from .user import User


class Job(db.EmbeddedDocument):
    id = db.StringField()

    status = db.StringField(choices=['queued', 'started', 'deferred', 'finished', 'stopped', 'failed'])
    error = db.StringField()

    started_at = db.DateTimeField()
    enqueued_at = db.DateTimeField()
    ended_at = db.DateTimeField()


class Task(db.Document):
    embedding_job = db.EmbeddedDocumentField(Job)
    indexing_job = db.EmbeddedDocumentField(Job)

    user = db.ReferenceField(User)
    
    def set(self, job):
        name = 'embedding_job' if job.func_name == 'extract_vectors' else 'indexing_job'

        print(name, self[name])

        self[name] = Job(**{
            'id': job.id,
            'status': job.get_status(),
            'error': job.exc_info,
            'started_at': job.started_at,
            'enqueued_at': job.enqueued_at,
            'ended_at': job.ended_at
        })