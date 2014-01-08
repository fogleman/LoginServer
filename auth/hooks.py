from flask import url_for, g, session, redirect, request
from auth import app
from models import User
import functools
import urlparse

def static(path):
    root = app.config.get('STATIC_ROOT')
    if root is None:
        return url_for('static', filename=path)
    else:
        return urlparse.urljoin(root, path)

@app.context_processor
def context_processor():
    return dict(static=static)

@app.before_request
def before_request():
    try:
        g.user = User.query.filter_by(username=session['username']).first()
    except Exception:
        g.user = None

def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return redirect(url_for('index', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user and g.user.admin:
            return f(*args, **kwargs)
        else:
            abort(403)
    return decorated_function
