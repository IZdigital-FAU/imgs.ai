from ..controller import Controller
import hashlib
import json
import re

from ...models.project import Project
from ...models.embedder import Embedder
from ...models.task import Task

from ...scripts.reducer import Reducer
from ...scripts.embedderFactory import EmbedderFactory
from ...scripts.embeddingCreator import EmbeddingCreator

from ...queue import q, redis_conn

whitespace = re.compile('\s')


class EmbedderController(Controller):

    def __init__(self, request): super().__init__(request)

    def show(self, pid):
        project = Project.objects(pk=pid).first()

        reducers = [Reducer(name) for name in ['PCA', 'TSNE']]
        payload = {
            'reducers': [reducer.make_payload() for reducer in reducers]
        }

        embedders = [EmbedderFactory.create(embedder.name) for embedder in project.embedders]
        payload['embedders'] = [embedder.make_payload() for embedder in embedders]

        return payload


    def store(self, pid, current_user):
        project = Project.objects(pk=pid).first()

        embedders = self.request.get_json()
        embedder_hashes = []

        payload = {}

        for embedder in embedders:
            hash = hashlib.blake2s(whitespace.sub('', json.dumps(embedder)).encode()).hexdigest()
            
            if hash not in list(map(lambda emb: emb.hash, project.embedders)):
                embedder_hashes.append(hash)
                embedder['hash'] = hash
                project.update(push__embedders=Embedder(**embedder))


        if embedder_hashes:
            embedding_creator = EmbeddingCreator(project.id, embedder_hashes)

            embedding_job = q.enqueue_call(embedding_creator.extract_vectors, args=(), timeout=2000, result_ttl=5000)
            indexing_job = q.enqueue_call(embedding_creator.build_annoy, kwargs={'n_trees': 10}, timeout=2000, result_ttl=5000)

            emb_task = Task(user=current_user.id)
            emb_task.setup(embedding_job)
            emb_task.save()

            idx_task = Task(user=current_user.id)
            idx_task.setup(indexing_job)
            idx_task.save()

            payload = {'task': {'embeddingJob': embedding_job.id, 'indexingJob': indexing_job.id}}

        return payload