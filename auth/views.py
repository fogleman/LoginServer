from flask import render_template, url_for, redirect, g, request, flash, session, abort
from werkzeug.security import generate_password_hash
from auth import app, db
from forms import LoginForm, RegistrationForm, IdentityTokenForm
from hooks import admin_required, login_required
from models import User, IdentityToken, AccessToken
from util import get_serializer
import datetime
import email
import uuid

# Views
@app.route('/', methods=['GET', 'POST'])
def index():
    if g.user is None:
        login_form = LoginForm(prefix="login")
        registration_form = RegistrationForm(prefix="register")
        button = request.form.get('button')
        if button == 'login' and login_form.validate_on_submit():
            user = login_form.user
            user.touch()
            session['username'] = user.username
            return redirect(request.args.get('next', url_for('index')))
        elif button == 'register' and registration_form.validate_on_submit():
            count = User.query.count()
            user = User(
                registration_form.username.data,
                generate_password_hash(registration_form.password.data),
                registration_form.email.data,
                False,
                True,
                bool(count == 0),
            )
            db.session.add(user)
            db.session.flush()
            email.send_account_created_email(user)
            db.session.commit()
            session['username'] = user.username
            flash('Registration successful! Please check your e-mail so we can verify your address.')
            return redirect(url_for('index'))
        else:
            return render_template('index.html',
                login_form=login_form,
                registration_form=registration_form)
    else:
        identity_tokens = list(g.user.identity_tokens.filter_by(enabled=True))
        return render_template('index.html', identity_tokens=identity_tokens)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/verify/<payload>')
@login_required
def verify_email(payload):
    try:
        user_id = get_serializer().loads(payload)
    except BadSignature:
        abort(404)
    user = User.query.get_or_404(user_id)
    if user != g.user:
        abort(403)
    user.verified = True
    db.session.commit()
    flash('E-mail verification successful - thank you!')
    return redirect(url_for('index'))

@app.route('/admin/user')
@admin_required
def admin_user():
    users = list(User.query.order_by(User.user_id))
    return render_template('admin_users.html', users=users)

@app.route('/admin/access')
@admin_required
def admin_access():
    access_tokens = list(AccessToken.query.order_by(
        db.desc(AccessToken.client_timestamp)))
    return render_template('admin_access_tokens.html',
        access_tokens=access_tokens)

@app.route('/access')
@login_required
def access():
    access_tokens = list(g.user.access_tokens.order_by(
        db.desc(AccessToken.client_timestamp)).limit(100))
    return render_template('access_tokens.html', access_tokens=access_tokens)

@app.route('/identity/create', methods=['GET', 'POST'])
@login_required
def identity_create():
    form = IdentityTokenForm()
    if form.validate_on_submit():
        token = uuid.uuid4().hex
        flash(token, 'token')
        identity_token = IdentityToken(
            g.user,
            form.name.data,
            generate_password_hash(token),
            True)
        db.session.add(identity_token)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('identity_create.html', form=form)

@app.route('/identity/delete/<int:identity_token_id>', methods=['POST'])
@login_required
def identity_delete(identity_token_id):
    identity_token = IdentityToken.query.get_or_404(identity_token_id)
    if identity_token.user != g.user or not identity_token.enabled:
        abort(403)
    identity_token.touch()
    identity_token.enabled = False
    db.session.commit()
    flash('Identity token successfully deleted.')
    return redirect(url_for('index'))

@app.route('/api/1/identity', methods=['POST'])
def api_identity():
    form = request.form
    user = User.query.filter_by(username=form['username']).first()
    if user is None:
        abort(403)
    for identity_token in user.identity_tokens.filter_by(enabled=True):
        if identity_token.check_token(form['identity_token']):
            break
    else:
        abort(403)
    identity_token.touch()
    token = uuid.uuid4().hex
    access_token = AccessToken(
        identity_token,
        user,
        generate_password_hash(token),
        True,
        request.remote_addr,
        datetime.datetime.utcnow(),
        None,
        None)
    db.session.add(access_token)
    db.session.commit()
    return token

@app.route('/api/1/access', methods=['POST'])
def api_access():
    form = request.form
    user = User.query.filter_by(username=form['username']).first()
    if user is None:
        abort(403)
    access_tokens = list(user.access_tokens.filter_by(enabled=True))
    for access_token in access_tokens:
        access_token.enabled = False
    db.session.commit()
    max_age = datetime.timedelta(minutes=1)
    for access_token in access_tokens:
        if access_token.check_token(form['access_token'], max_age):
            break
    else:
        abort(403)
    access_token.server_addr = request.remote_addr
    access_token.server_timestamp = datetime.datetime.utcnow()
    db.session.commit()
    return str(user.user_id)
