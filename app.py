import os
from flask import Flask, jsonify
from flask_session import Session
from werkzeug.utils import secure_filename
from babel import Locale
import httpagentparser
import urllib.request
import json
import hashlib
from pyLib.analysis.a_models import ASession


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

userOS = None
userIP = None
userCity = None
userBrowser = None
userCountry = None
userContinent = None
sessionID = None

Session(app)

@app.before_request
def getAnalyticsData():
    userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
    session['userOS'] = userInfo['platform']['name']
    session['userBrowser'] = userInfo['browser']['name']
    ip = request.remote_addr
    session['userIP'] = '5.237.179.21' if ip == '127.0.0.1' else ip
    ipapi = 'http://www.iplocate.io/api/lookup/' + ip
    try:
        resp = urllib.request.urlopen(ipapi)
        result = resp.read()
        result = json.loads(result.decode('utf-8'))
        session['userCountry'] = result['country'] if len(result['country']) > 0 else ''
        session['userContinent'] = result['continent'] if len(result['continent']) > 0 else ''
        session['userCity'] = result['city'] if len(result['city']) > 0 else ''
    except:
        print("Could Not Find: ", ip)
    sessid = ASession._id_by_ip(ip)
    if sessid == -1:
        data = {'ip': ip, 'continent': session['continent'], 'country': session['country'], 'city': session['city'], 'os': session['os'], 'browser': session['browser'], 'session': session['session']}
        sessid = ASession._new_session(data)


from pyLib.route import *

if __name__ == '__main__':
   app.run(port = 6119, debug = True )