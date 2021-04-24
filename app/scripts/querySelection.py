from env import Environment as env

from ..models.imagemetadata import Project


class QuerySelection:

    def __init__(self):
        project = Project.objects().first()

        self.project = project.name
        self.embedder = project.embedders.first().name
        self.pos = []
        self.neg = []
        self.n = 30
        self.metric = env.ANNOY_DISTANCE_METRICS[0]
        self.mode = env.MODES[0]

    
    def set(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get(self, *args):
        if not args: return self.__dict__
        return {key:value for key in args}