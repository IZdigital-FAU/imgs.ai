from app.controllers.api.ImagesController import ImagesController
from flask import Blueprint, request, session, send_from_directory, redirect, url_for
from flask_login import fresh_login_required, current_user

from os.path import join
from os import listdir
import os

from pymongo import MongoClient

import hashlib
import re

import json
import csv

from env import Environment as env

from ..scripts.embeddingCreator import EmbeddingCreator
from ..scripts.embedderFactory import EmbedderFactory

from ..models.project import Project
from ..models.imagemetadata import ImageMetadata
from ..models.embedder import Embedder
from ..models.task import Task

from ..queue import q, redis_conn
from rq.job import Job
from rq import get_current_job

from ..scripts.reducer import Reducer

from ..scripts.querySelection import QuerySelection


from ..controllers.api.EmbedderController import EmbedderController


api = Blueprint('api', __name__)


@api.route('/metadata', methods=['GET'])
@fresh_login_required
def get_metadata():
    return {
            'projects': [project.name for project in Project.objects()],
            'orderings': env.MODES,
            'distance_metrics': env.ANNOY_DISTANCE_METRICS
        }

@api.route('/<pid>/<img>')
@fresh_login_required
def fetch_img(pid, img):
    project = Project.objects(pk=pid).as_pymongo()[0]
    PATH = join(env.PROJECT_DATA_DIR, project['name'])

    return send_from_directory(PATH, img)


@api.route('/images', methods=["GET", "POST"])
@fresh_login_required
def fetch_imgs():
    controller = ImagesController(request)
    payload = controller.index()

    if request.method == 'POST':
        payload = controller.store()

    return payload


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
    job = Job.fetch(pid, redis_conn)
    task = Task.objects(job_id=pid)

    fields = {
        'status': job.get_status(),
        'started_at': job.started_at
    }

    if job.exc_info: fields['error'] = job.exc_info

    if fields['status'] == 'finished': fields['ended_at'] = job.ended_at

    task.update(**fields)

    return job.meta


@api.route('/<pid>/embedders', methods=["GET", "POST"])
@fresh_login_required
def fetch_embedders(pid):
    controller = EmbedderController(request)

    payload = controller.show(pid)

    if request.method == 'POST': payload = controller.store(pid, current_user)

    return payload


@api.route('/', methods=["GET", "POST"])
@fresh_login_required
def handle_projects():
    projects = [
                    {
                        'id': str(project['_id']),
                        'name': project['name'],
                        'nimgs': len(project['data']) if 'data' in project else 0,
                        'features': list(map(lambda x: x['name'], project['embedders']))
                    }
                for project in Project.objects.as_pymongo()]

    return json.dumps(projects)


@api.route('/<pid>', methods=["GET", "POST"])
@fresh_login_required
def get_project_data(pid):
    project = Project.objects(pk=pid).as_pymongo()[0]

    total = len(project['data']) if 'data' in project else 0

    per_page = 10
    start = (int(request.args.get('page')) - 1) * per_page
    end = min(start + per_page, total)

    return {'data': [img for img in project['data'][start:end]], 'name': project['name'], 'total': total, 'per_page': per_page}



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