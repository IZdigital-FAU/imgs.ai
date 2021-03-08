from flask import render_template, flash, redirect, request, url_for, send_from_directory, get_flashed_messages
from flask import Response
from flask import session as flask_session
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import SignupForm, LoginForm, EmbedderForm
from app import app, log, db, login_manager, models
from model import EmbeddingModel
from app.user import User, create_user
from app.session import Session
from config import Config
import time
import os

from .controllers.embedder import Embedder
from .controllers.embedderFactory import EmbedderFactory
from .controllers.reducer import ReducerFactory
from .controllers.embeddingCreator import EmbeddingCreator

from util import new_dir

import json


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html", title="imgs.ai")


@app.route("/help")
@login_required
def help():
    return render_template("help.html", title="imgs.ai")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("User name already exists; please choose another one.", 'warning')
        else:
            user = create_user(form)
            if user.access:
                login_user(user)  # Log in as newly created user
                return redirect(f"{url_for('interface')}")
            flash("Thank you for requesting beta access, you will hear from us in the next 24 hours.", 'info')
    return render_template("signup.html", title="imgs.ai - Sign up for alpha", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("interface"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(password=form.password.data):
            if user.access:
                log.info(f"{user.username} logged in")
                login_user(user)
                return redirect(url_for("interface"))
            flash("Access not granted yet!")
        else:
            flash("Invalid username/password combination", 'danger')
        return redirect(url_for("login"))
    return render_template("login.html", title="Log in", form=form)


@app.route("/users", methods=["GET", "POST"])
@login_required
def users():
    if request.method == "POST":
        for i, access in request.form.items():
            user = User.query.get(int(i))
            user.access = bool(int(access))
            db.session.commit()
    return render_template("users.html", users=User.query.all(), title="Users")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flask_session.clear()
    return redirect(url_for("index"))


@app.route("/settings")
@login_required
def settings():
    session = Session(flask_session)
    return render_template("settings.html", title="imgs.ai", session=session, Config=Config)


@app.route("/cdn/<idx>")
@login_required
def cdn(idx):
    session = Session(flask_session)
    root, path, _, _ = session.get_data(idx)
    return send_from_directory(root, path)


@app.route('/api/images', methods=["GET", "POST"])
@login_required
def fetch_imgs():
    session = Session(flask_session)

    print('session dict', session.__dict__)

    if request.method == "POST":
        data = request.get_json()
        print('DATA', data)

        session.model = data['model']
        session.n = data['n']

        session.emb_type = data["emb_type"]
        session.metric = data["metric"]
        session.mode = data["mode"]

        session.pos_idxs = data['pos_idxs']
        session.neg_idxs = data['neg_idxs']

    session.get_nns()
    popovers, links, images = session.render_nns()

    session.store(flask_session)

    data = [{'id': idx, 'url': url} for idx, url in images.items()]

    return {'data': data, 'querySelection': session.__dict__}


@app.route('/api/embedders', methods=["GET", "POST"])
@login_required
def fetch_embedders():
    session = Session(flask_session)

    embedders = {name: EmbedderFactory.create(name) for name in EmbedderFactory.names}

    if request.method == 'POST':
        data = request.form
        print('name', data['name'])

        project_name = data['name']
        model_folder = os.path.join(Config.MODELS_PATH, project_name)

        new_dir(model_folder)

        # Handle url file
        url_fpath = os.path.join(model_folder, project_name) + ".csv"
        url_file = request.files['file']
        url_file.save(url_fpath)
        url_file.close()
        
        print('embedders', json.loads(data['embedders']))

        for embedder in json.loads(data['embedders']):
            for param in embedder['params']:
                embedders[embedder['name'].lower()].set_param(param, embedder['params'][param])

            if embedder['reducer']:
                embedders[embedder['name'].lower()].reducer.active = True
                embedders[embedder['name'].lower()].reducer = ReducerFactory.create(embedder['reducer']['name'], embedder['reducer']['params'])

        embedding_creator = EmbeddingCreator(
            model_folder=model_folder,
            embedders={embedder['name'].lower() : embedders[embedder['name'].lower()] for embedder in json.loads(data['embedders'])},
            data_location=url_fpath
        )
        
        embedding_creator.train(n_trees=10)

        Config.MODELS.append(project_name)
        models[project_name] = EmbeddingModel()
        models[project_name].load(model_folder)
        session.load_model(project_name)

    payload = {
        'data': [embedder.make_payload() for embedder in embedders.values()]
    }

    return payload


@app.route('/test')
@login_required
def test():
    return render_template('test.html')