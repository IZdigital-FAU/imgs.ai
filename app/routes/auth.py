from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from flask_login import current_user, login_user, logout_user, fresh_login_required

from ..models.user import User, create_user

from logger import log
from datetime import datetime


auth = Blueprint('auth', __name__)


@auth.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated: return redirect(url_for("view.index"))

    if request.method == 'POST':
        form = request.form
        print(form)
        existing_user = User.objects(email=form['email']).first()
        
        if not existing_user:
            user = create_user(form)
            login_user(user)  # Log in as newly created user
            return redirect(url_for('view.index'))

        flash("User already exists", 'warning')

    return render_template("signup.html", title="imgs.ai - Sign up")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated: return redirect(url_for("view.index"))

    if request.method == 'POST':
        form = request.form
        user = User.objects(email=form['email']).first()

        if user and user.verify(form['secret']):
            log.info(f"{user.name} logged in")
            user.last_login = datetime.now()
            user.save()

            login_user(user)
            return redirect(url_for("view.index"))
    
        else: flash("Invalid username/password combination", 'danger')

    return render_template("login.html", title="Log in")


@auth.route("/logout")
@fresh_login_required
def logout():
    logout_user()
    session.clear()
    print(session)
    return redirect(url_for("auth.login"))