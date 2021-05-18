from env import Environment as env

from ..models.project import Project


class QuerySelection:

    def __init__(self):
        project = None

        for p in Project.objects().as_pymongo():
            if p['embedders']:
                project = p
                embedder = p['embedders'][0]
                break

        self.project = project['name']
        self.embedder = f"{embedder['name']}_{embedder['reducer']['name']}" if embedder['reducer'] else embedder['name']
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
        return {key:getattr(self, key) for key in args}

    
    def get_project_embedders(self):
        project = Project.objects(name=self.project).as_pymongo()[0]
        return [f"{emb['name']}_{emb['reducer']['name']}" if emb['reducer'] else emb.name for emb in project['embedders']]