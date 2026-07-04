from logging.config import dictConfig

from flask import Flask
from flask.logging import default_handler

from .config import LOGGER_CONFIG


def create_app():
    dictConfig(LOGGER_CONFIG)

    app = Flask(__name__)
    app.logger.removeHandler(default_handler)

    from . import models
    models.create_tables()

    from . import views
    views.init_app(app)

    return app
