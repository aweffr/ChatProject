from . import db
from datetime import datetime


class RoleLevel:
    ROOT = 0x01
    ADMIN = 0x02
    OPERATOR = 0x04
    USER = 0x08


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    level = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.now())
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {'user': (RoleLevel.USER, True),
                 'operator': (RoleLevel.OPERATOR, False),
                 'admin': (RoleLevel.ADMIN, False),
                 'root': (RoleLevel.ROOT, False)}
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            level, default = roles[r]
            role.level, role.default = level, default
            db.session.add(role)
        db.session.commit()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    name = db.Column(db.String(64), unique=True, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.now())
    last_mod = db.Column(db.DateTime, default=datetime.now())
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            role = Role.query.filter_by(default=True).first()
            self.role_id = role.id

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
