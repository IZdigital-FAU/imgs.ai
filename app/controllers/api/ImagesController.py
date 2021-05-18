from ..controller import Controller
from ...models.project import Project

from ...scripts.querySelection import QuerySelection
from ...scripts.embeddingCreator import EmbeddingCreator


class ImagesController(Controller):

    def __init__(self, request):
        super().__init__(request)
        self.query = QuerySelection()

    def index(self):
        project = Project.objects().filter(name=self.query.project).as_pymongo()[0]

        embedding_creator = EmbeddingCreator(project['_id'])
        images = embedding_creator.compute_nns(**{k:v for k,v in self.query.get().items() if k != 'project'})

        return {'data': images, 'querySelection': self.query.get(), 'embedders': self.query.get_project_embedders()}

    def store(self):
        self.query.set(**self.request.get_json())
        return self.index()