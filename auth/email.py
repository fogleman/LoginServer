from flask import render_template
from flask_mail import Message
from auth import mail

def send_account_created_email(user):
    message = Message('Craft E-mail Verification', [user.email])
    message.body = render_template('account_created_email.txt', user=user)
    mail.send(message)
