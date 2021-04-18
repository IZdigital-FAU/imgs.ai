from flask import Blueprint, request, session
from flask_login import fresh_login_required

from os.path import join
import os

import json
import csv

from env import Environment as env

from ..scripts.embeddingCreator import EmbeddingCreator
from ..scripts.embedderFactory import EmbedderFactory

from ..models.imagemetadata import Project, ImageMetadata, Embedder, Reducer


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

@api.route("/<idx>")
@fresh_login_required
def cdn(idx):
    return send_from_directory(root, path)


@api.route('/images', methods=["GET", "POST"])
@fresh_login_required
def fetch_imgs():
    project = Project.objects().filter(name=session['project']).first()
    embedding_creator = EmbeddingCreator(project.id)

    images = embedding_creator.compute_nns(**{k:v for k,v in session.items() if k != 'project'})

    return {'data': images, 'querySelection': session.read()}


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