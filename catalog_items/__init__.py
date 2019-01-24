import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.serving import make_ssl_devcert

from config import config

bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

from catalog_items.main_app.errors import page_not_found, internal_server_error

def create_app(config_name):
    # Flask instance
    app = Flask(__name__)

    app.config.from_object(config[config_name])

    config[config_name].init_app(app)
    bootstrap.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    make_ssl_devcert('./ssl', host='localhost')

    from catalog_items.main_app import main_blueprint
    app.register_blueprint(main_blueprint)

    from catalog_items.auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    return app
