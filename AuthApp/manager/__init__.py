import os
from flask import Flask
from flask_login import current_user, login_required
from manager.models import Users
from manager.ext import csrf, db, login_manager, mail

os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

def create_app(config=None):

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_object('config.DevConfig')

    if config:
        app.config.update(config)

    with app.app_context():
        extensions(app)
        register_apps(app)
        authentication(app, Users)
        db.create_all()

    return app

def extensions(app):    
    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    return None

def register_apps(app):
    from manager.apps import users
    app.register_blueprint(users)

    return None

def authentication(app, user_model):
    login_manager.login_view = 'users.login'

    @login_manager.user_loader
    def load_user(uid):
        return user_model.query.get(uid)