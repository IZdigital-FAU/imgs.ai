from flask import Blueprint
from flask import render_template

from flask_login import login_required, fresh_login_required

view = Blueprint('view', __name__)


@view.route('/')
@fresh_login_required
def index():
    return render_template('test.html')