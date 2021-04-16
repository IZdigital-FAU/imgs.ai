from flask import Blueprint, request, session
from os.path import join

import json
import csv

from env import Environment as env

from ..controllers.embeddingCreator import EmbeddingCreator
from ..controllers.embedderFactory import EmbedderFactory

from ..project import Project

from ..models.imagemetadata import Project as ProjectModel, ImageMetadata, Embedder, Reducer


api = Blueprint('api', __name__)


@api.route('/metadata', methods=['GET'])
def get_metadata():
    return {
        'projects': [{'text': project, 'value': project} for project in env.PROJECTS],
        'embedders': [{'text': embedder, 'value': embedder} for embedder in EmbedderFactory.names], # TODO: Load only project-immanent embedders
        'orderings': [{'text': mode, 'value': mode} for mode in env.MODES],
        'distance_metrics': [{'text': metric, 'value': metric} for metric in env.ANNOY_DISTANCE_METRICS]
    }

@api.route("/<idx>")
def cdn(idx):
    root, path, _, _ = session.get_data(idx)
    return send_from_directory(root, path)


@api.route('/images', methods=["GET", "POST"])
def fetch_imgs():
    projectModel = ProjectModel.objects().first()

    embedding_creator = EmbeddingCreator(projectModel.id)
    
    session['embedder'] = projectModel.embedders.first().name
    session['pos'] = []
    session['neg'] = []
    session['n'] = 30
    session['metric'] = env.ANNOY_DISTANCE_METRICS[0]
    session['mode'] = env.MODES[0]

    if request.method == "POST":
        data = request.get_json()
        print('POST', data)

    images = embedding_creator.compute_nns(**{k:v for k,v in session.items() if not k in ('_fresh', 'project')})

    session['project'] = projectModel.name

    return {'data': images, 'querySelection': dict(session)}


@api.route('/embedders', methods=["GET", "POST"])
def fetch_embedders():
    if request.method == 'POST':
        POST = request.form
        print('DATA', POST)

        project = Project(POST['name'])

        # Handle url file
        url_file = request.files['file']
        url_fpath = join(project.dirpath, f'{project.name}.csv')
        url_file.save(url_fpath)
        url_file.close()

        with open(url_fpath, 'r') as csvUpload:
            data = [ImageMetadata(**row) for row in csv.DictReader(csvUpload)]

        embedderConfigs = []

        for embedder in json.loads(POST['embedders']):
            embedderConfigs.append(Embedder(**embedder))

        projectModel = ProjectModel(name=project.name, data=data, embedders=embedderConfigs)
        projectModel.save()

        embedding_creator = EmbeddingCreator(projectId=projectModel.id)
        embedding_creator.extract_vectors()
        embedding_creator.build_annoy(n_trees=10)


    embedders = [EmbedderFactory.create(name) for name in EmbedderFactory.names]

    payload = {
        'data': [embedder.make_payload() for embedder in embedders]
    }

    return payload