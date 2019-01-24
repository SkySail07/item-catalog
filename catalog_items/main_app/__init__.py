from flask import Blueprint

main_blueprint = Blueprint('main_app', __name__)

from . import errors
from . import views
