from flask_mail import Message
from manager.ext import mail
from flask import render_template

def send_email(to, subject, template):

    msg = Message(  subject,
                    recipients=[to],
                    html=template,
                    sender= 'russellpinto996@gmail.com')
    mail.send(msg)