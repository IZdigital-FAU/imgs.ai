from flask import Blueprint, request, session, send_from_directory, redirect, url_for
from flask_login import fresh_login_required, current_user

from os.path import join
import os

import json
import csv

from env import Environment as env

from ..scripts.embeddingCreator import EmbeddingCreator
from ..scripts.embedderFactory import EmbedderFactory

from ..models.project import Project
from ..models.imagemetadata import ImageMetadata
from ..models.embedder import Embedder
from ..models.task import Task

from ..queue import q, conn
from rq.job import Job
from rq import get_current_job

from ..scripts.reducer import Reducer

from ..scripts.querySelection import QuerySelection


api = Blueprint('api', __name__)


@api.route('/metadata', methods=['GET'])
@fresh_login_required
def get_metadata():
    return {
            'projects': [project.name for project in Project.objects()],
            'embedders': EmbedderFactory.names, # TODO: Load only project-immanent embedders
            'orderings': env.MODES,
            'distance_metrics': env.ANNOY_DISTANCE_METRICS
        }

@api.route("/<pid>/<img>")
@fresh_login_required
def cdn(pid, img):
    project = Project.objects(pk=pid).first()
    PATH = join(env.PROJECT_DATA_DIR, project.name)

    print(project, PATH)

    return send_from_directory(PATH, img)


@api.route('/images', methods=["GET", "POST"])
@fresh_login_required
def fetch_imgs():
    query = QuerySelection()

    if request.method == 'POST': query.set(**request.get_json())
    
    project = Project.objects().filter(name=query.project).first()
    embedding_creator = EmbeddingCreator(project.id)

    images = embedding_creator.compute_nns(**{k:v for k,v in query.get().items() if k != 'project'})

    return {'data': images, 'querySelection': query.get()}


@api.route('/embedders', methods=['GET'])
@fresh_login_required
def generic_embedders():
    embedders = [EmbedderFactory.create(name) for name in EmbedderFactory.names]
    reducers = [Reducer(name) for name in ['PCA', 'TSNE']]

    return {
        'embedders': [embedder.make_payload() for embedder in embedders],
        'reducers': [reducer.make_payload() for reducer in reducers]
    }

@api.route('/progress/<pid>')
def get_progress(pid):
    job = Job.fetch(pid, conn)

    return job.meta


@api.route('/<pid>/embedders', methods=["GET", "POST"])
@fresh_login_required
def fetch_embedders(pid):
    project = Project.objects(pk=pid).first()

    reducers = [Reducer(name) for name in ['PCA', 'TSNE']]
    payload = {
        'reducers': [reducer.make_payload() for reducer in reducers]
    }

    if request.method == 'POST':
        embedders = request.get_json()
        print('DATA', embedders)

        project.embedders = [Embedder(**embedder) for embedder in embedders]
        project.embedders.save()

        embedding_creator = EmbeddingCreator(projectId=project.id)

        embedding_job = q.enqueue_call(embedding_creator.extract_vectors, args=(), timeout=2000, result_ttl=5000)
        indexing_job = q.enqueue_call(embedding_creator.build_annoy, kwargs={'n_trees': 10}, timeout=2000, result_ttl=5000)

        task = Task(user=current_user.id)
        task.set(embedding_job)
        task.set(indexing_job)
        task.save()

        payload['task'] = {'embeddingJob': embedding_job.id, 'indexingJob': indexing_job.id}

    embedders = [EmbedderFactory.create(embedder.name) for embedder in project.embedders]
    payload['embedders'] = [embedder.make_payload() for embedder in embedders]

    return payload



@api.route('/projects', methods=["GET", "POST"])
@fresh_login_required
def handle_projects():
    projects = [
                    {
                        'id': str(project.id),
                        'name': project.name,
                        'nimgs': project.data.count()
                    }
                
                for project in Project.objects().all()]

    return json.dumps(projects)


@api.route('/project/<pid>', methods=["GET", "POST"])
@fresh_login_required
def get_project_data(pid):
    print('PROJECT', pid)

    project = Project.objects(pk=pid).first()

    total = project.data.count()

    per_page = 10
    start = (int(request.args.get('page')) - 1) * per_page
    end = min(start + per_page, total)

    return {'data': [json.loads(img.to_json()) for img in project.data[start:end]], 'name': project.name, 'total': total, 'per_page': per_page}



"""
@api.route('/upload', methods=['POST'])
@fresh_login_required
def upload():
    data = request.form
    # Handle url file
    url_file = request.files['file']
    url_fpath = join(project.get_path(), f'{project.name}.csv')
    url_file.save(url_fpath)
    url_file.close()

    with open(url_fpath, 'r') as csvUpload:
        project.data = [ImageMetadata(**row) for row in csv.DictReader(csvUpload)]

    os.remove(url_fpath)
"""