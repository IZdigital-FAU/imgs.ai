from flask import Blueprint, request, session, send_from_directory
from flask_login import fresh_login_required

from os.path import join
import os

import json
import csv

from env import Environment as env

from ..scripts.embeddingCreator import EmbeddingCreator
from ..scripts.embedderFactory import EmbedderFactory

from ..models.imagemetadata import Project, ImageMetadata, Embedder, Reducer

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


@api.route('/embedders', methods=["GET", "POST"])
@fresh_login_required
def fetch_embedders():
    if request.method == 'POST':
        data = request.form
        print('DATA', data)

        project = Project(name=data['name'])

        # Handle url file
        url_file = request.files['file']
        url_fpath = join(project.get_path(), f'{project.name}.csv')
        url_file.save(url_fpath)
        url_file.close()

        with open(url_fpath, 'r') as csvUpload:
            project.data = [ImageMetadata(**row) for row in csv.DictReader(csvUpload)]

        os.remove(url_fpath)

        project.embedders = [Embedder(**embedder) for embedder in json.loads(data['embedders'])]
        project.save()

        embedding_creator = EmbeddingCreator(projectId=project.id)
        embedding_creator.extract_vectors()
        embedding_creator.build_annoy(n_trees=10)

    embedders = [EmbedderFactory.create(name) for name in EmbedderFactory.names]

    payload = {
        'data': [embedder.make_payload() for embedder in embedders]
    }

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