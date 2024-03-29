import logging
from logging.config import dictConfig

from flask.logging import default_handler
from flask import Flask

from config import LOGGER_CONFIG


dictConfig(LOGGER_CONFIG)
app = Flask(__name__)

app.logger = logging.getLogger('FlaskPractice')
app.logger.removeHandler(default_handler)

import views