import pytz
import random
import datetime
from hashlib import md5

from flask import current_app
from flask_login import UserMixin

from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, TimedJSONWebSignatureSerializer

from manager.ext import db
from manager.libs.utils.util_sqlalchemy import ResourceMixin, AwareDateTime

class Users(UserMixin, ResourceMixin, db.Model):
    
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(24), index=True)
    phone = db.Column(db.String(13))
    email = db.Column(db.String(255), unique=True, nullable=False, server_default='')
    password = db.Column(db.String(128), nullable=False, server_default='')
    
    phone_confirmed = db.Column(db.Boolean(), nullable=False, server_default='0')
    email_confirmed = db.Column(db.Boolean(), nullable=False, server_default='0')
    
    verified = db.Column('is_verified', db.Boolean(), nullable=False, server_default="0")
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
    otp = db.Column(db.String(10), nullable=True)

    # Activity tracking.
    sign_in_count = db.Column(db.Integer, nullable=False, default=0)
    current_sign_in_on = db.Column(AwareDateTime())
    current_sign_in_ip = db.Column(db.String(45))
    last_sign_in_on = db.Column(AwareDateTime())
    last_sign_in_ip = db.Column(db.String(45))

    def __init__(self, **kwargs):
        super(Users, self).__init__(**kwargs)
        self.password = Users.encrypt_password(kwargs.get('password', ''))

    @classmethod
    def find_by_identity(cls, identity):
        return Users.query.filter((Users.email == identity) | (Users.username == identity)).first()
    
    @classmethod
    def encrypt_password(cls, plaintext_password):
        if plaintext_password:
            return generate_password_hash(plaintext_password)

        return None
    
    def authenticated(self, with_password=True, password=''):        
        if with_password:
            return check_password_hash(self.password, password)

        return True
    
    def is_active(self, act=False):
        if act:
            self.active = True
            return self.active
        return self.active

    def update_activity_tracking(self, ip_address):
        self.sign_in_count += 1
        self.active = True

        self.last_sign_in_on = self.current_sign_in_on
        self.last_sign_in_ip = self.current_sign_in_ip

        self.current_sign_in_on = datetime.datetime.now(pytz.utc)
        self.current_sign_in_ip = ip_address

        return self.save()

    def get_auth_token(self):        
        private_key = current_app.config['SECRET_KEY']
        serializer = URLSafeTimedSerializer(private_key)
        data = [str(self.id), md5(self.password.encode('utf-8')).hexdigest()]

        return serializer.dumps(data)

    def serialize_token(self, expiration=3600):        
        private_key = current_app.config['SECRET_KEY']
        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)

        return serializer.dumps({'user_email': self.email}).decode('utf-8')

    @classmethod
    def confirm_email_token(cls, username, email, password, expiration=3600):
        private_key = current_app.config['SECRET_KEY']
        serializer = TimedJSONWebSignatureSerializer(private_key, expiration)

        token = serializer.dumps({'user_username': username,'user_email': email,'user_password': password}).decode('utf-8')

        return token

    @classmethod
    def deserialize_token(cls, token):        
        private_key = TimedJSONWebSignatureSerializer(current_app.config['SECRET_KEY'])
        try:
            decoded_payload = private_key.loads(token)
            data = {'user_username':decoded_payload.get('user_username'),
                    'user_email':decoded_payload.get('user_email'),
                    'user_password':decoded_payload.get('user_password')}
            return data
        except Exception:
            return None


    def genrate_otp(self, digit=4):
        f = int('1'+'0'*(digit - 1))
        l = int('9'*digit)
        otp = random.randint(f,l)

        return otp
    


    def verify_otp(self, otp):
        if self.otp:
            if self.otp == otp:
                return True
        
        return False