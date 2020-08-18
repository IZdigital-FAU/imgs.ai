from flask import render_template, flash, redirect, request, url_for
from flask import session as flask_session
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import SignupForm, LoginForm
from app import app, log, db, login_manager
from app.user import User, create_user
from app.session import Session
from config import Config
import time


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def index():
    return render_template("index.html", title="imgs.ai")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("User name already exists; please choose another one.")
        else:
            user = create_user(form)
            if user.access:
                login_user(user)  # Log in as newly created user
                return redirect(f"{url_for('interface')}")
            flash(
                "Thank you for requesting beta access, you will hear from us in the next 24 hours."
            )
    return render_template(
        "signup.html", title="imgs.ai - Sign up for alpha", form=form
    )


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


@app.route("/image/<idx>")
@login_required
def image(idx):
    session = Session(flask_session)
    img = session.get_img(idx)
    return render_template(
        "image.html", title="imgs.ai", img=img
    )


@app.route("/interface", methods=["GET", "POST"])
@login_required
def interface():
    # Load from cookie
    session = Session(flask_session)

    # Uploads
    if request.files:
        session.extend(request.files.getlist("file"))

    # Model
    if "model" in request.form:
        if session.model != request.form["model"]: # Only reload and reset if model changed
            session.load_model(request.form["model"], pin_idxs=session.pos_idxs) # Keep all positive queries

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
            session.pos_idxs = list(
                set(session.pos_idxs) | set(request.form.getlist("add-pos"))
            )  # Union of sets
            session.neg_idxs = list(
                set(session.neg_idxs) - set(request.form.getlist("add-pos"))
            )  # Difference of sets
        elif request.form["btn"] == "Remove":
            session.pos_idxs = list(
                set(session.pos_idxs) - set(request.form.getlist("remove"))
            )  # Difference of sets
            session.neg_idxs = list(
                set(session.neg_idxs) - set(request.form.getlist("remove"))
            )  # Difference of sets
        elif request.form["btn"] == "Negative":
            session.neg_idxs = list(
                set(session.neg_idxs) | set(request.form.getlist("add-neg"))
            )  # Union of sets
            session.pos_idxs = list(
                set(session.pos_idxs) - set(request.form.getlist("add-neg"))
            )  # Difference of sets

    # Search
    start = time.process_time()
    session.get_nns()
    log.info(
        f"Search by {current_user} in {session.model} completed in {time.process_time() - start}, returning {len(session.res_idxs)} results"
    )

    # Render data
    metas, thumbs, links = session.render_nns()

    # Store in cookie
    session.store(flask_session)

    return render_template(
        "interface.html",
        title="imgs.ai",
        session=session,
        Config=Config,
        metas=metas,
        thumbs=thumbs,
        links=links
    )