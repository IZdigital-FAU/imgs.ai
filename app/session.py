from flask.sessions import SecureCookieSession, SecureCookieSessionInterface
from .models.imagemetadata import Project
from env import Environment as env

from .scripts.embedderFactory import EmbedderFactory


class Session(SecureCookieSession):
    def __init__(self):
        super().__init__()

        project = Project.objects().first()

        self['project'] = project.name if project else ''
        self['embedder'] = project.embedders.first().name if project else ''
        self['pos'] = []
        self['neg'] = []
        self['n'] = 30
        self['metric'] = env.ANNOY_DISTANCE_METRICS[0]
        self['mode'] = env.MODES[0]

    def write(self, **kwargs):
        for key, value in kwargs.items():
            self[key] = value

    def read(self, *keys):
        if not keys: return self
        return {key:self.get(key) for key in keys}


class CustomSessionInterface(SecureCookieSessionInterface):

    def open_session(self, app, request):
        super().open_session(app, request)
        session = Session()
        
        data = request.get_json()
        if request.path == '/api/images' and data:
            session.write(**data)
        return session

    def save_session(self, app, session, response):
        super().save_session(app, session, response)