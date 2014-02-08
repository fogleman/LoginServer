from flask import url_for
from auth import db
from util import get_serializer
from werkzeug.security import check_password_hash
import datetime

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    verified = db.Column(db.Boolean, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
    admin = db.Column(db.Boolean, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    touched = db.Column(db.DateTime, nullable=False)
    def __init__(self, username, password, email, verified, enabled, admin):
        self.username = username
        self.password = password
        self.email = email
        self.verified = verified
        self.enabled = enabled
        self.admin = admin
        self.created = datetime.datetime.utcnow()
        self.touched = self.created
    def check_password(self, password):
        return check_password_hash(self.password, password)
    def touch(self):
        self.touched = datetime.datetime.utcnow()
        db.session.commit()
    def get_verification_link(self):
        payload = get_serializer().dumps(self.user_id)
        return url_for('verify_email', payload=payload, _external=True)

class IdentityToken(db.Model):
    identity_token_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False, index=True)
    name = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(256), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    touched = db.Column(db.DateTime, nullable=False)
    user = db.relationship(User, backref=db.backref('identity_tokens', lazy='dynamic'))
    def __init__(self, user, name, token, enabled):
        self.user = user
        self.name = name
        self.token = token
        self.enabled = enabled
        self.created = datetime.datetime.utcnow()
        self.touched = self.created
    def check_token(self, token):
        return check_password_hash(self.token, token)
    def touch(self):
        self.touched = datetime.datetime.utcnow()
        db.session.commit()

class AccessToken(db.Model):
    access_token_id = db.Column(db.Integer, primary_key=True)
    identity_token_id = db.Column(db.Integer, db.ForeignKey(IdentityToken.identity_token_id), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey(User.user_id), nullable=False, index=True)
    token = db.Column(db.String(256), nullable=False, unique=True)
    enabled = db.Column(db.Boolean, nullable=False)
    client_addr = db.Column(db.String(256), nullable=False)
    client_timestamp = db.Column(db.DateTime, nullable=False)
    server_addr = db.Column(db.String(256), nullable=True)
    server_timestamp = db.Column(db.DateTime, nullable=True)
    identity_token = db.relationship(IdentityToken, backref=db.backref('access_tokens', lazy='dynamic'))
    user = db.relationship(User, backref=db.backref('access_tokens', lazy='dynamic'))
    def __init__(self, identity_token, user, token, enabled, client_addr, client_timestamp, server_addr, server_timestamp):
        self.identity_token = identity_token
        self.user = user
        self.token = token
        self.enabled = enabled
        self.client_addr = client_addr
        self.client_timestamp = client_timestamp
        self.server_addr = server_addr
        self.server_timestamp = server_timestamp
    @property
    def server_addr_str(self):
        known_servers = {
            '162.243.195.82': 'michaelfogleman.com',
        }
        return known_servers.get(self.server_addr, self.server_addr)
    @property
    def age(self):
        return datetime.datetime.utcnow() - self.client_timestamp
    def check_token(self, token, max_age):
        if self.age > max_age:
            return False
        return check_password_hash(self.token, token)
