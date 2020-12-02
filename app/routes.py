from flask import render_template, flash, redirect, request, url_for, send_from_directory, get_flashed_messages
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
from embedders import EmbedderFactory, ReducerFactory, Embedder
from train import make_model
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE


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
            flash("Invalid username/password combination")
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
    return render_template(
        "settings.html", title="imgs.ai", session=session, Config=Config
    )


@app.route("/cdn/<idx>")
@login_required
def cdn(idx):
    session = Session(flask_session)
    root, path, _, _ = session.get_data(idx)
    return send_from_directory(root, path)


@app.route("/interface", methods=["GET", "POST"])
@login_required
def interface():
    # Load from cookie
    session = Session(flask_session)

    # Uploads
    if request.files:
        session.extend(request.files.getlist("file"))

    # Settings
    if "n" in request.form:
        session.n = request.form["n"]
    if "emb_type" in request.form:
        session.emb_type = request.form["emb_type"]
    if "metric" in request.form:
        session.metric = request.form["metric"]
    if "mode" in request.form:
        session.mode = request.form["mode"]
    if "size" in request.form:
        session.size = request.form["size"]

    # Actions
    if "btn" in request.form:
        if request.form["btn"] == "Positive":
            new_pos = set(request.form.getlist("add-pos"))
            session.pos_idxs = list(set(session.pos_idxs) | new_pos) # Union of sets
            session.neg_idxs = list(set(session.neg_idxs) - new_pos)  # Difference of sets
            log.debug(f'{current_user} added {len(new_pos)} positives')

        elif request.form["btn"] == "Remove":
            removables = set(request.form.getlist("remove"))
            session.pos_idxs = list(set(session.pos_idxs) - removables)  # Difference of sets
            session.neg_idxs = list(set(session.neg_idxs) - removables)  # Difference of sets
            log.debug(f'{current_user} removed {removables} from search')

        elif request.form["btn"] == "Negative":
            session.neg_idxs = list(set(session.neg_idxs) | set(request.form.getlist("add-neg")))  # Union of sets
            session.pos_idxs = list(set(session.pos_idxs) - set(request.form.getlist("add-neg")))  # Difference of sets

        elif request.form["btn"] == "Clear":
            session.neg_idxs = []
            session.pos_idxs = []

    # Handle single drag&drops
    if 'add-pos' in request.form:
        new_pos = set(request.form.getlist("add-pos"))
        session.pos_idxs = list(set(session.pos_idxs) | new_pos) # Union of sets
        session.neg_idxs = list(set(session.neg_idxs) - set(request.form.getlist("add-pos")))  # Difference of sets
        log.debug(f'{current_user} added {len(new_pos)} positives')

    if 'add-neg' in request.form:
        session.neg_idxs = list(set(session.neg_idxs) | set(request.form.getlist("add-neg")))  # Union of sets
        session.pos_idxs = list(set(session.pos_idxs) - set(request.form.getlist("add-neg")))  # Difference of sets

    # Model
    if "model" in request.form:
        if session.model != request.form["model"]: # Only reload and reset if model changed
            session.load_model(request.form["model"], pin_idxs=session.pos_idxs) # Keep all positive queries

    # Search
    start = time.process_time()
    session.get_nns()
    log.info(
        f"Search by {current_user} in {session.model} completed in {time.process_time() - start}, returning {len(session.res_idxs)} results"
    )

    # Render data
    popovers, links, images = session.render_nns()

    # Store in cookie
    session.store(flask_session)

    log.debug(f'Positive indices: {session.pos_idxs}')
    log.debug(f'Negative indices: {session.neg_idxs}')

    return render_template(
        "interface.html",
        title="imgs.ai",
        session=session,
        Config=Config,
        popovers=popovers,
        links=links,
        images=images
    )


@app.route("/pipeline", methods=["GET", "POST"])
@login_required
def pipeline():
    loading = False
    embedders = ['Raw', 'VGG19', 'Face', 'Poses']
    reducers = ['PCA', 'TSNE']

    # Load from cookie
    session = Session(flask_session)

    embedder_data = {}
    form = EmbedderForm()
    
    embedder_factory = EmbedderFactory()
    reducer_factory = ReducerFactory()

    for embedder in embedders:
        if embedder not in embedder_data:
            embedder_data[embedder] = {'data': embedder_factory.create(embedder, {}), 'active': False}
        for reducer in reducers:
            embedder_data[embedder][reducer] = False

    if request.method == "POST":
        log.debug(request.form)

        project_name = request.form['projectName']
        model_folder = os.path.join('/home/oleg/olegsModels', project_name)

        if not os.path.isdir(model_folder):
            os.mkdir(model_folder)

        # Handle url file
        url_fpath = os.path.join(model_folder, project_name) + ".csv"
        log.debug(request.files)
        url_file = request.files['urlPerLineFile']
        url_file.save(url_fpath)
        url_file.close()

        for key, value in request.form.items():
            if key in ('csrf_token', 'projectName', 'urlPerLineFile', 'submit'):
                continue

            if ':' not in key: #includes setting
                log.debug(key)
                embedder, setting = key.split('.')
                if setting.endswith('min_score'):
                    digitize = lambda s: float(s)
                else:
                    digitize = lambda s: int(s)
                embedder_factory.set_params(embedder_data[embedder]['data'], setting, digitize(value))
                embedder_data[embedder]['active'] = True

            else: #includes reducer
                embedder, reducer = key.split(':')
                reducer = reducer.split('.')[0]

                n_samples = len(open(url_fpath).read().split('\n')) - 1
                if n_samples < int(value):
                    value = n_samples

                reducer_object = reducer_factory.create(reducer, {'n_components': int(value)})
                embedder_factory.set_params(embedder_data[embedder]['data'], 'reducer', reducer_object)
                embedder_data[embedder][reducer] = reducer_object
                # Handle front-end active elements
                print(embedder_data[embedder])
        
        try:
            make_model(model_folder=model_folder, embedders=embedder_data, data_root=url_fpath)
        except KeyError as error:
            flash(error, 'danger')
            return render_template('pipeline_composition.html', embedders=embedder_data, reducers=reducers, form=form)

        models[project_name] = EmbeddingModel()
        models[project_name].load(model_folder)
        session.load_model(project_name)

        flash('Successfully created image vectors', 'success')

    return render_template('pipeline_composition.html', embedders=embedder_data, reducers=reducers, form=form)