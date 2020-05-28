from flask_wtf import Form
from wtforms import TextField, PasswordField, validators
from models import User

class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter_by(username=self.username.data).first()
        if not user:
            self.password.errors.append('Incorrect username or password.')
            return False
        if not user.check_password(self.password.data):
            self.password.errors.append('Incorrect username or password.')
            return False
        if not user.enabled:
            self.username.errors.append('User account is disabled.')
            return False
        self.user = user
        return True

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(3, 15)])
    email = TextField('E-mail Address', [validators.Email()])
    password = PasswordField('Password', [validators.Length(6)])
    confirm_password = PasswordField('Confirm Password', [validators.EqualTo('password')])
    def validate(self):
        if not Form.validate(self):
            return False
        user = User.query.filter(User.username.ilike(self.username.data)).first()
        if user:
            self.username.errors.append('Username already in use.')
            return False
        return True

class IdentityTokenForm(Form):
    name = TextField('Name', [validators.Required()])
