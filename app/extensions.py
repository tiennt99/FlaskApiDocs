import logging
import os
# from flask_socketio import SocketIO

from flask_jwt_extended import JWTManager
from webargs.flaskparser import FlaskParser
from flask_sqlalchemy import SQLAlchemy
from logging.handlers import RotatingFileHandler

parser = FlaskParser()

os.makedirs("logs", exist_ok=True)
db = SQLAlchemy()
jwt = JWTManager()
# sio = SocketIO(debug=False, log_output=False, cors_allowed_origins="*")
# # logger
app_log_handler = RotatingFileHandler('logs/app.log', maxBytes=1000000, backupCount=30)
# logger
logger = logging.getLogger('api')
logger.setLevel(logging.DEBUG)
logger.addHandler(app_log_handler)

