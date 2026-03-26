import os
from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_babel import Babel
from config import config

db = SQLAlchemy()
babel = Babel()

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_locale():
    return session.get('lang', 'ru')


def create_app(config_name='default'):
    app = Flask(
        __name__,
        template_folder=os.path.join(_BASE_DIR, 'templates'),
        static_folder=os.path.join(_BASE_DIR, 'static')
    )
    app.config.from_object(config[config_name])
    # Flask-Babel busca translations/ relativo a app.root_path (= app/).
    # Como la carpeta real está en la raíz del proyecto, la indicamos explícitamente.
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = os.path.join(_BASE_DIR, 'translations')

    db.init_app(app)
    babel.init_app(app, locale_selector=get_locale)

    with app.app_context():
        from app import routes, models
        db.create_all()

        app.register_blueprint(routes.bp)

    return app
