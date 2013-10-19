from flask import Flask, g, render_template, request
from app.database import db
from app.extensions import lm, api, travis, mail, heroku, bcrypt, celery
from app.assets import assets
import app.utils as utils
from app import config
from app.user import user
from app.auth import auth
import time


def create_app(config=config.base_config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.config['DEBUG'] = True

    register_extensions(app)
    register_blueprints(app)
    register_errorhandlers(app)
    register_jinja_env(app)

    @app.before_request
    def before_request():
        g.request_start_time = time.time()
        g.request_time = lambda: '%.5fs' % (time.time() - g.request_start_time)
        g.pjax = 'X-PJAX' in request.headers

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    return app


def register_extensions(app):
    heroku.init_app(app)
    travis.init_app(app)
    db.init_app(app)
    api.init_app(app)
    lm.init_app(app)
    mail.init_app(app)
    bcrypt.init_app(app)
    celery.config_from_object(app.config)
    assets.init_app(app)


def register_blueprints(app):
    app.register_blueprint(user, url_prefix='/user')
    app.register_blueprint(auth)


def register_errorhandlers(app):
    for e in [401, 404, 500]:
        app.errorhandler(e)(render_error)


def render_error(e):
    return render_template('errors/%s.html' % e.code), e.code


def register_jinja_env(app):
    app.jinja_env.globals['url_for_other_page'] = utils.url_for_other_page
    app.jinja_env.globals['timeago'] = utils.timeago
