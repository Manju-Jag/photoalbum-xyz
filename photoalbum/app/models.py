from datetime import datetime
from hashlib import md5
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from flask import url_for
import base64
from datetime import datetime, timedelta
import os

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    album = db.relationship('Album', backref='author', lazy='dynamic')
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def to_dict(self, include_email=False):
        data = {
            'id': self.id,
            'username': self.username,
            'photos_count': self.photos.count(),
            '_links': {'self': url_for('api.get_user', id=self.id),}
        }
        if include_email:
            data['email'] = self.email
        return data
    def from_dict(self, data, new_user=False):
        for field in ['username', 'email']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password']) 
    def get_token(self, expires_in=3600):
        now = datetime.utcnow()
        if self.token and self.token_expiration > now + timedelta(seconds=60):
            return self.token
        self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
        self.token_expiration = now + timedelta(seconds=expires_in)
        db.session.add(self)
        return self.token

    def revoke_token(self):
        self.token_expiration = datetime.utcnow() - timedelta(seconds=1)

    def check_token(token):
        user = User.query.filter_by(token=token).first()
        if user is None or user.token_expiration < datetime.utcnow():
            return None
        return user           
    
@login.user_loader
def load_user(id):
    return User.query.get(int(id))
class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    photo_url = db.Column(db.String(140))
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
def __repr__(self):
        return '<Photo {}>'.format(self.photo_url)


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(25))
    description = db.Column(db.String(150))
    category = db.Column(db.String(50))
    is_favourite = db.Column(db.Boolean)
    photo = db.relationship('Photo', backref='author', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
def __repr__(self):
    return '<Album {}>'.format(self.name)


    