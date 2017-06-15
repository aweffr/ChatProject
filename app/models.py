from . import db
from datetime import datetime


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.now())
    last_mod = db.Column(db.DateTime, default=datetime.now())
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % self.name


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_time = db.Column(db.DateTime, default=datetime.now())

    def __repr__(self):
        return '<Message %r>' % self.content
