from flask_wtf import CSRFProtect
csrf = CSRFProtect()

from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

from flask_login import LoginManager
login_manager = LoginManager()

from flask_mail import Mail
mail = Mail()