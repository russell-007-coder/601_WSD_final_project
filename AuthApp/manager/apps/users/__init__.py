from flask import Blueprint

users = Blueprint("users", __name__ , template_folder='./mails')

from .routes import *