from app import app
from flask import Flask, redirect, render_template, session, request, url_for
from pyLib.web import apology, login_required, super_required, validate_password, validate_username
from pyLib.analysis.a_models import ASession, Visit
from pyLib.analysis.a_db import adb_session
from pyLib.db.models import User, HReference
from pyLib.db.datab import db_session
import httpagentparser
import urllib.request
import json
from datetime import datetime
import hashlib

# GLOBAL CONST
USERNAME_MIN = 6
USERNAME_MAX = 20
PASS_MIN = 8
PASS_MAX = 66
ALLOWED_CHAR = ['!','@','#','$','%','^','&','*']


# Configure SQLite DB
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()
    adb_session.remove()


@app.before_request
def getAnalyticsData():
    if 'user' not in session:
        userInfo = httpagentparser.detect(request.headers.get('User-Agent'))
        session['userOS'] = userInfo['platform']['name']
        session['userBrowser'] = userInfo['browser']['name']
        ip = '5.237.179.21' if request.remote_addr == '127.0.0.1' else request.remote_addr
        session['userIP'] = ip
        ipapi = 'http://www.iplocate.io/api/lookup/' + ip
        session['userCountry'] = 'country'
        session['userContinent'] = 'continent'
        session['userCity'] = 'city'
        try:
            resp = urllib.request.urlopen(ipapi)
            result = resp.read()
            result = json.loads(result.decode('utf-8'))
            session['userCountry'] = result['country'] if result['country'] and len(result['country']) > 0 else ''
            session['userContinent'] = result['continent'] if result['continent'] and len(result['continent']) > 0 else ''
            session['userCity'] = result['city'] if result['city'] and len(result['city']) > 0 else ''
        except:
            print("Could Not Find: ", ip)
        sessid = ASession._id_by_ip(ip)
        if sessid == -1:
            time = datetime.now().replace(microsecond=0)
            lines = (str(time)+ip).encode('utf-8')
            session['session'] = hashlib.md5(lines).hexdigest()
            data = {'ip': ip, 'continent': session['userContinent'] , 'country': session['userCountry'], 'city': session['userCity'], 'os': session['userOS'], 'browser': session['userBrowser'], 'session': session['session']}
            sessid = ASession._new_session(data)
        session['user'] = sessid


# LandingPage
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        
        vis = Visit._new_visit(session['user'], 'domain','www')
        print('Domain visit: ', vis)
        vis = Visit._new_visit(session['user'], 'home','/')
        print('Home visit: ', vis)
        
        h = HReference._newRef('home', 'خانه', '/')
        h = HReference._newRef('gallery', 'گالری', '/gallery/')
        h = HReference._newRef('contact', 'ارتباط با ما', '/contact/')
        h = HReference._newRef('about', 'درباره ما', '/about/')

        refs = HReference._hrefList('home')
        return render_template('index.html', references = refs)


# Gallery Page
@app.route('/gallery/', methods=['GET'])
def gallery():
    if request.method == 'GET':
        vis = Visit._new_visit(session['user'], 'domain','www')
        print('Domain visit: ', vis)
        vis = Visit._new_visit(session['user'], 'gallery','/gallery')
        print('Gallery visit: ', vis)
        refs = HReference._hrefList('gallery')
        return render_template('gallery.html', references = refs)


# Login Page
@app.route('/admin/login/', methods=['GET', 'POST'])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        
        code = 403
        titl = 'خطای کاربر'
        # Save Requested USERNAME
        USERNAME = str(request.form.get('username'))

        # Ensure username was submitted
        if not USERNAME:
            explain = 'لطفا نام کاربری را وارد نمایید!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('must provide username', err, code)

        # Ensure username is VALID
        username_code = validate_username(USERNAME, USERNAME_MIN, USERNAME_MAX)
        if username_code:
            if username_code == 1:
                explain = 'نام کاربری باید حداقل شامل ' + USERNAME_MIN + ' کاراکتر باشد!'
            if username_code == 2:
                explain = 'نام کاربری باید حداکثر شامل ' + USERNAME_MAX + ' کاراکتر باشد!'
            if username_code == 3:
                explain = 'نام کاربری نباید شامل هیچ کاراکتر فاصله ای باشد!'
            if username_code == 4:
                explain = 'نام کاربری فقط میتواند شامل کاراکتر حروف انگلیسی و اعداد باشد!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('username', err, code)
        
        # Save Requested Password
        PASSWORD = str(request.form.get('password'))

        # Ensure password was submitted
        if not PASSWORD:
            explain = 'لطفا پسوورد را وارد نمایید!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('must provide password', err, code)

        # Ensure password is VALID
        pass_code = validate_password(PASSWORD, PASS_MIN, PASS_MAX, ALLOWED_CHAR)
        
        # IF Have Code Error
        if pass_code:
            if pass_code == 1:
                explain = 'پسوورد باید حداقل شامل ' + PASS_MIN + ' کاراکتر باشد!'
            elif pass_code == 2:
                explain = 'پسوورد باید حداکثر شامل ' + PASS_MAX + ' کاراکتر باشد!'
            elif pass_code == 3:
                explain = 'پسوورد نباید شامل هیچ کاراکتر فاصله ای باشد!'
            if pass_code == 4:
                explain = 'پسوورد فقط می تواند شامل کاراکتر های : ('
                for c in ALLOWED_CHAR:
                    explain += c + ', '
                explain += ') باشد!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('invalid password', err, code)
        
        # Query database for username and password check
        user = User._validate_password(USERNAME, PASSWORD)

        if user == -1 or user == -2:
            explain = 'نام کاربری و/یا کلمه عبور نادرست می باشد!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('must provide password', err, code)
        
        # Remember which user has logged in
        session['user_id'] = user.id
        session['permission'] = user.permission
        
        # Redirect user to home page
        return redirect(url_for('admin', uname = USERNAME))

    # Render Administrator Login Page
    return render_template('login.html')


# Log user out
@app.route('/admin/logout/')
@login_required
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to landingPage
    return redirect('/')

# Admin Panel
@app.route('/admin/<uname>/', methods=['GET'])
@login_required
def admin(uname):
    return f"Hello, {uname}"


# Register new Admin
@app.route('/admin/register/', methods=['GET', 'POST'])
@login_required
@super_required
def register():
    return

@app.errorhandler(404)
def bad_request(e):
    code = 404
    err = {'code': code, 'title': 'صفحه یافت نشد', 'explain': 'متاسفیم، صفحه ای که به دنبال آن هستید وجود ندارد.'}
    return apology(e, err, code)

