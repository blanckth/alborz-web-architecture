import os
from flask import Flask, session, request
from flask_session import Session
from werkzeug.utils import secure_filename
#from babel import Locale
from pyLib.db.datab import db_session
from pyLib.analysis.a_db import adb_session



# Configure application
app = Flask(__name__)
app.debug = True
app.secret_key = os.urandom(24)
# Setup Upload Configuration
UPLOAD_FOLDER = '/upload'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

# Ensure templates are auto-loaded
app.config['TEMPLATE_AUTO_RELOAD'] = True

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

from pyLib.route import *

if __name__ == '__main__':
   app.run(port = 6119, debug = True)