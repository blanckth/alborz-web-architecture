from app import app, session, request, render_template, redirect, url_for, os
from app import apology, login_required, super_required, validate_password, validate_username, secure_filename
from app import ASession, Visit, APage
from app import adb_session
from app import User, HReference, ImgCat, ImgRef
from app import db_session
import httpagentparser
import urllib
import json
from datetime import datetime
import hashlib

from app.pyLib.upload import allowed_file

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
            data = {'ip': ip, 'continent': session['userContinent'], 'country': session['userCountry'], 'city': session['userCity'], 'os': session['userOS'], 'browser': session['userBrowser'], 'session': session['session']}
            sessid = ASession._new_session(data)
        session['user'] = sessid


# LandingPage
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        HReference._newRef('home', 'صفحه اصلی', '/')
        HReference._newRef('gallery', 'نگارخانه', '/gallery')
        HReference._newRef('contact', 'ارتباط با ما', '/contact')
        HReference._newRef('about', 'درباره ما', '/about')
        HReference._newRef('admin', 'مدیریت', '/ap', -1)
        HReference._newRef('logout', 'خروج', '/logout', -1)
        HReference._newRef('profile', 'صفحه شخصی', '/profile', HReference._id_by_name('admin'))
        HReference._newRef('changepass', 'تغییر کلمه عبور', '/changepass', HReference._id_by_name('profile'))
        HReference._newRef('admins', 'مدیران', '/admins', HReference._id_by_name('profile'))
        HReference._newRef('addadmin', 'افزودن مدیر جدید', '/addadmin', HReference._id_by_name('admins'))
        HReference._newRef('images', 'نگاره ها', '/images', HReference._id_by_name('admin'))
        HReference._newRef('imageadd', 'افزودن نگاره', '/images/add', HReference._id_by_name('images'))
        HReference._newRef('posts', 'محتوا', '/posts', HReference._id_by_name('admin'))
        HReference._newRef('postadd', 'افزودن محتوا', '/posts/add', HReference._id_by_name('posts'))

        User._new_user('testtest', 'testtest')
        User._new_user('salarmhmdi', 'salarmhmdi')

        ImgCat._new_icat('general', 'عمومی')
        ImgCat._new_icat('post', 'پست')
        
        Visit._new_visit(session['user'], 'domain','www')
        Visit._new_visit(session['user'], 'home','/')
        isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
        refs = HReference._hrefList('home', isAdmin)
        return render_template('index.html', references = refs)


@app.route('/ajax/home/')
def homeservice():
    return render_template('ajax/ajax-home.html')


# Gallery Page
@app.route('/gallery/', methods=['GET'])
def gallery():
    if request.method == 'GET':
        vis = Visit._new_visit(session['user'], 'domain','www')
        print('Domain visit: ', vis)
        vis = Visit._new_visit(session['user'], 'gallery','/gallery')
        print('Gallery visit: ', vis)
        isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
        refs = HReference._hrefList('gallery', isAdmin)
        cats = []
        tmpDict = {'cat': 'one', 'value': 'دسته اول'}
        cats.append(tmpDict)
        tmpDict = {'cat': 'two', 'value': 'دسته دوم'}
        cats.append(tmpDict)
        tmpDict = {'cat': 'three', 'value': 'دسته سوم'}
        cats.append(tmpDict)
        tmpDict = {'cat': 'four', 'value': 'دسته چهارم'}
        cats.append(tmpDict)
        catlist = ImgCat._ic_list()
        if catlist != -1:
            for cl in catlist:
                tmpDict = {'cat': cl[0].name, 'value': cl[0].value}
                cats.append(tmpDict)
        imgs = []
        tmpDict = {'category': 'one', 'morehref': '/', 'href': '/static/img/uploaded/product1.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        tmpDict = {'category': 'two', 'morehref': '/', 'href': '/static/img/uploaded/product2.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        tmpDict = {'category': 'three', 'morehref': '/', 'href': '/static/img/uploaded/product3.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        tmpDict = {'category': 'four', 'morehref': '/', 'href': '/static/img/uploaded/product4.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        tmpDict = {'category': 'one', 'morehref': '/', 'href': '/static/img/uploaded/product5.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        tmpDict = {'category': 'two', 'morehref': '/', 'href': '/static/img/uploaded/product6.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        tmpDict = {'category': 'three', 'morehref': '/', 'href': '/static/img/uploaded/product7.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        tmpDict = {'category': 'four', 'morehref': '/', 'href': '/static/img/uploaded/product8.jpg', 'alt': 'Product one', 'title': 'Title', 'keyword': 'Keyword'}
        imgs.append(tmpDict)
        imglist = ImgRef._img_list()
        if imglist != -1:
            for il in imglist:
                tmpDict = {'category': il['cat'], 'morehref': '#', 'href': il['href'], 'alt': 'Product one', 'title': il['title'], 'keyword': il['kword']}
                imgs.append(tmpDict)
        return render_template('gallery.html', references = refs, images = imgs, category = cats)


# Contact Page
@app.route('/contact/', methods=['GET','POST'])
def contact():
    if request.method == 'POST':
        return 'render_template('')'
    vis = Visit._new_visit(session['user'], 'domain','www')
    print('Domain visit: ', vis)
    vis = Visit._new_visit(session['user'], 'contact','/contact')
    print('Contact visit: ', vis)
    isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
    refs = HReference._hrefList('contact', isAdmin)
    return render_template('contact.html', references = refs)


# About Page
@app.route('/about/', methods=['GET'])
def about():
    if request.method == 'GET':
        vis = Visit._new_visit(session['user'], 'domain','www')
        print('Domain visit: ', vis)
        vis = Visit._new_visit(session['user'], 'about','/about')
        print('About visit: ', vis)
        isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
        refs = HReference._hrefList('about', isAdmin)
        return render_template('about.html', references = refs)


# Login Page
@app.route('/login/', methods=['GET', 'POST'])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == 'POST':
        
        code = 403
        titl = 'خطای کاربر'

        # Ensure username was submitted
        if 'username' not in request.form:
            explain = 'لطفا نام کاربری را وارد نمایید!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('must provide username', err, code)

        # Ensure password was submitted
        if 'password' not in request.form:
            explain = 'لطفا پسوورد را وارد نمایید!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('must provide password', err, code)

        # Save Requested USERNAME
        USERNAME = str(request.form.get('username'))

        # Ensure username is VALID
        username_code = validate_username(USERNAME, USERNAME_MIN, USERNAME_MAX)
        if username_code:
            if username_code == 1:
                explain = 'نام کاربری باید حداقل شامل ' + str(USERNAME_MIN) + ' کاراکتر باشد!'
            if username_code == 2:
                explain = 'نام کاربری باید حداکثر شامل ' + str(USERNAME_MAX) + ' کاراکتر باشد!'
            if username_code == 3:
                explain = 'نام کاربری نباید شامل هیچ کاراکتر فاصله ای باشد!'
            if username_code == 4:
                explain = 'نام کاربری فقط میتواند شامل کاراکتر حروف انگلیسی و اعداد باشد!'

            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('username', err, code)
        
        # Save Requested Password
        PASSWORD = str(request.form.get('password'))

        # Ensure password is VALID
        pass_code = validate_password(PASSWORD, PASS_MIN, PASS_MAX, ALLOWED_CHAR)
        
        # IF Have Code Error
        if pass_code:
            if pass_code == 1:
                explain = 'پسوورد باید حداقل شامل ' + str(PASS_MIN) + ' کاراکتر باشد!'
            elif pass_code == 2:
                explain = 'پسوورد باید حداکثر شامل ' + str(PASS_MAX) + ' کاراکتر باشد!'
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
        vpcode, user = User._validate_password(USERNAME, PASSWORD)

        if vpcode < 0:
            explain = 'نام کاربری و/یا کلمه عبور نادرست می باشد!'
            err = {'code': code, 'title': titl, 'explain': explain}
            return apology('must provide password', err, code)
        
        # Remember which user has logged in
        session['user_id'] = user.id
        session['permission'] = user.permission
        session['username'] = user.username
        # Redirect user to home page
        return redirect('/ap')

    # Render Administrator Login Page
    refs = HReference._hrefList('login', 0)
    return render_template('login.html', references = refs)


# Log user out
@app.route('/logout/', methods = ['GET'])
@login_required
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to landingPage
    return redirect('/')


# Admin Route
@app.route('/ap/', methods = ['GET'])
@login_required
def adminroute():
    return redirect(url_for('admin', uname = session['username']))


# Admin Panel
@app.route('/ap/<uname>/', methods=['GET'])
@login_required
def admin(uname):
    if uname != session['username']:
        return redirect('/')
    user = {'username': uname, 'permit': session['permission']}
    isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
    refs = HReference._hrefList('admin', isAdmin)
    domainp = APage._page_by_name('domain')
    home = APage._page_by_name('home')
    gall = APage._page_by_name('gallery')
    about = APage._page_by_name('about')
    pageDict = {'domain': domainp if domainp == -1 else int(domainp.visit), 'home': home if home == -1 else int(home.visit),
                'gallery': gall if gall == -1 else int(gall.visit), 'about': about if about == -1 else int(about.visit)}
    return render_template('admin.html', references = refs, user = user, pages = pageDict)


# Images Admin router
@app.route('/images/', methods=['GET'])
@login_required
def imagesroute():
    return redirect(url_for('images', uname = session['username']))

# Admin Images
@app.route('/ap/<uname>/images/', methods=['GET', 'POST'])
@login_required
def images(uname):
    if uname != session['username']:
        return redirect('/')
    user = {'username': uname, 'permit': session['permission']}
    isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
    refs = HReference._hrefList('admin', isAdmin)
    imgs = ImgRef._img_list()
    imgs = [] if imgs == -1 else imgs
    return render_template('images.html', references = refs, user = user, images = imgs)

# Image ADD Admin router
@app.route('/images/add/', methods=['GET','POST'])
@login_required
def imageaddroute():
    if request.method == 'POST':
        if 'file' not in request.files:
            code = 404
            err = {'code': code, 'title': 'فایل پیدا نشد', 'explain': 'برای آپلود عکس ، لازم است فایل آن را انتخاب نمایید!'}
            return apology('Invalid File',err, code)
        file = request.files['file']
        if file.filename == '':
            code = 403
            err = {'code': code, 'title': 'فایل پیدا نشد', 'explain': 'برای آپلود عکس ، لازم است فایل آن را انتخاب نمایید!'}
            return apology('Invalid File',err, code)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            ImgRef._new_img(iname=filename, ihref=f'/static/uploads/{filename}',
                            iaddg = 1, ititle=request.form.get('title'), 
                            icat = request.form.get('cat'), 
                            ikeyword=request.form.get('kword'))
            return redirect('/images')
        else:
            code = 403
            err = {'code': code, 'title': 'فایل نادرست', 'explain': 'برای آپلود عکس ، لازم است فایل آن را بدرستی انتخاب نمایید!'}
            return apology('Invalid File',err, code)
    return redirect(url_for('imageadd', uname = session['username']))

# Admin Image ADD
@app.route('/ap/<uname>/images/add/', methods=['GET', 'POST'])
@login_required
def imageadd(uname):
    if uname != session['username']:
        return redirect('/')
    user = {'username': uname, 'permit': session['permission']}
    isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
    refs = HReference._hrefList('admin', isAdmin)
    icat = ImgCat._ic_list()
    ics = []
    if icat != -1:
        for ic in  icat:
            icdict = {'name': ic[0].name, 'value': ic[0].value}
            ics.append(icdict)
    return render_template('imageadd.html', references = refs, user = user, icats = ics)


# Profile Admin router
@app.route('/profile/', methods=['GET'])
@login_required
def profileroute():
    return redirect(url_for('profile', uname = session['username']))

# Admin Image ADD
@app.route('/ap/<uname>/profile/', methods=['GET', 'POST'])
@login_required
def profile(uname):
    if uname != session['username']:
        return redirect('/')
    user = {'username': uname, 'permit': session['permission']}
    isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
    refs = HReference._hrefList('admin', isAdmin)
    return render_template('profile.html', references = refs, user = user)



# Register Admin router
@app.route('/register/', methods=['GET'])
@login_required
@super_required
def registerroute():
    return redirect(url_for('register', uname = session['username']))

# Register new Admin
@app.route('/ap/<uname>/register/', methods=['GET', 'POST'])
@login_required
@super_required
def register(uname):
    if uname != session['username']:
        return redirect('/')
    return redirect('/gallery')


@app.errorhandler(404)
def bad_request(e):
    code = 404
    err = {'code': code, 'title': 'صفحه یافت نشد', 'explain': 'متاسفیم، صفحه ای که به دنبال آن هستید وجود ندارد.'}
    return apology(e, err, code)

