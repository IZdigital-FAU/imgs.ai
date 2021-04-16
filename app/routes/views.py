from flask import Blueprint
from flask import render_template


view = Blueprint('view', __name__)

@view.route("/")
def index():
    return render_template("index.html", title="imgs.ai")


@view.route("/help")
def help():
    return render_template("help.html", title="imgs.ai")


@view.route("/users", methods=["GET", "POST"])
def users():
    if request.method == "POST":
        for i, access in request.form.items():
            user = User.query.get(int(i))
            user.access = bool(int(access))
            db.session.commit()
    return render_template("users.html", users=User.query.all(), title="Users")


@view.route("/settings")
def settings():
    return render_template("settings.html", title="imgs.ai", session=session, Config=environment)

@view.route('/test')
def test():
    return render_template('test.html')