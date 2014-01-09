from flask import render_template
from flask_mail import Message
from auth import app, mail

def send_account_created_email(user):
    if app.debug:
        return
    message = Message('Craft E-mail Verification', [user.email])
    message.body = render_template('account_created_email.txt', user=user)
    mail.send(message)
