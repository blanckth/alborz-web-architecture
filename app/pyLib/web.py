from flask import redirect, render_template, session
from functools import wraps
from app.pyLib.db.models import HReference


# Escape Special Characters
def escape(s):
        # Escape special characters.
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s


# Error Message Template
def apology(error, err, code=400):
    if code >= 400 and code < 500:
        isAdmin = 1 if 'permission' in session and session['permission'] >= 0 else 0
        refs = HReference._hrefList('', isAdmin)
        return render_template('error/400.html',references = refs, Err = err, error = error), code
    

# Login required Decorator
def login_required(f):

    # Decorate routes to require login.
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# Super Admin Permission
def super_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Not Admin
        if session.get("permission") is None:
            return redirect("/")
        # Not Super Admin
        if int(session.get("permission")):
            return redirect("/ap")
        return f(*args, **kwargs)
    return decorated_function


# Validate Username
def validate_username(username: str, username_min: int, username_max: int) -> int:

    # Correct Length
    if len(username) < username_min:
        return 1

    if len(username) > username_max:
        return 2

    # Blank Skip
    if " " in username:
        return 3
    
    # Special Char Skip
    if not username.isalnum():
        return 4

    # Validated
    return 0


# Validate Password
def validate_password(password: str, pass_min: int, pass_max:int, spec_chars:list) -> int:
    
    # Correct Length
    if len(password) < pass_min:
        return 1
    
    if len(password) > pass_max:
        return 2

    def validChar(char):
        for sc in spec_chars:
            if char == sc:
                return True
        return False

    # Check And Validate All Characters
    for c in password:
        if c.isspace():
            return 3
        if c.isalnum():
            continue
        if not validChar(c):
            return 4

    # Validated
    return 0