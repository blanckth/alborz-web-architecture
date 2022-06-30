import os
from flask import Flask, session, request, redirect, render_template, url_for
from flask_session import Session
from werkzeug.utils import secure_filename
from app.pyLib.db.datab import db_session
from app.pyLib.analysis.a_db import adb_session
from app.pyLib.analysis.a_models import ASession, Visit, APage
from app.pyLib.db.models import User, HReference, ImgCat, ImgRef
from app.pyLib.web import apology, login_required, super_required, validate_password, validate_username
from app.pyLib.upload import allowed_file

# Configure application
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Setup Upload Configuration
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000

# Ensure templates are auto-loaded
app.config['TEMPLATE_AUTO_RELOAD'] = True

# Configure session to use filesystem (instead of signed cookies)
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_TYPE'] = 'filesystem'

Session(app)

from app.pyLib.route import *
