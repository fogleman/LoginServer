from auth import app, db
from flask import Flask
from flask_mail import Mail
from flask_gravatar import Gravatar
from flask_sqlalchemy import SQLAlchemy

#app = Flask(__name__)
#app.config.from_object('auth.config')

#mail = Mail(app)
#gravatar = Gravatar(app, use_ssl=True)
#db = SQLAlchemy(app)

from auth import hooks
from auth import models
from auth import views 




if __name__ == '__main__':
    db.create_all()
    app.run(debug=True, host='0.0.0.0')
