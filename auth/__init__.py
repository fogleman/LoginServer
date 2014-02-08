from flask import Flask
from flask_mail import Mail
from flask.ext.gravatar import Gravatar
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('auth.config')

mail = Mail(app)
gravatar = Gravatar(app, use_ssl=True)
db = SQLAlchemy(app)

import hooks
import models
import views
