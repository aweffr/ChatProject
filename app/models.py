from . import db
from . import login_manager
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class RoleLevel:
    ROOT = 0xff  # 0b1111 1111
    ADMIN = 0xff  # 0b1111 1111
    OPERATOR = 0x0f  # 0b0000 1111
    USER = 0x07  # 0b0000 0111
    ANONYMOUS = 0x00  # 0b0000 0000


class Permission:
    RECEIVE = 0x01  # 接收消息 0b0000 0001
    COMMENT = 0x02  # 发送消息 0b0000 0011
    DELETE = 0x04  # 删除消息 0b0000 0100
    CREATE_TOPIC = 0x08  # 创建主题  0b0000 1000


class Role(db.Model):
    __tablename__ = 'role'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    level = db.Column(db.Integer, index=True)
    permission = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.now())
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    @staticmethod
    def init_roles():
        p_user = Permission.RECEIVE | Permission.COMMENT
        p_operator = Permission.RECEIVE | Permission.COMMENT | Permission.DELETE
        p_admin = Permission.RECEIVE | Permission.COMMENT | Permission.DELETE | Permission.CREATE_TOPIC
        p_root = Permission.RECEIVE | Permission.COMMENT | Permission.DELETE | Permission.CREATE_TOPIC

        roles = {'root': (RoleLevel.ROOT, p_root, False),
                 'admin': (RoleLevel.ADMIN, p_admin, False),
                 'operator': (RoleLevel.OPERATOR, p_operator, False),
                 'user': (RoleLevel.USER, p_user, True), }

        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            level, permission, default = roles[r]
            role.level, role.permission, role.default = level, permission, default
            db.session.add(role)
        db.session.commit()


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'))
    name = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    create_time = db.Column(db.DateTime, default=datetime.now())
    last_login = db.Column(db.DateTime, default=datetime.now())
    last_mod = db.Column(db.DateTime, default=datetime.now())
    messages = db.relationship('Message', backref='user', lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role_id is None:
            role = Role.query.filter_by(default=True).first()
            self.role_id = role.id

    @property
    def password(self):
        raise AttributeError("password is not a readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User %r>' % self.name

    @staticmethod
    def init_user():
        admin_role = Role.query.filter_by(name="admin").first()
        root_role = Role.query.filter_by(name="root").first()
        assert admin_role is not None and root_role is not None

        root = User(role_id=root_role.id, name="root", email="root@huami.com", password="root")
        admin = User(role_id=admin_role.id, name="admin", email="admin@huami.com", password="admin")

        db.session.add_all([root, admin, ])
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Message(db.Model):
    __tablename__ = 'message'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    create_time = db.Column(db.DateTime, default=datetime.now())
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'))

    def __init__(self, **kwargs):
        super(Message, self).__init__(**kwargs)
        if self.topic_id is None:
            topic = Topic.query.filter_by(namespace='public').first()
            self.topic_id = topic.id

    def __repr__(self):
        return '<Message %r>' % self.content


class Topic(db.Model):
    __tablename__ = "topic"
    id = db.Column(db.Integer, primary_key=True)
    namespace = db.Column(db.String(64), unique=True, index=True)
    create_time = db.Column(db.DateTime, default=datetime.now())
    last_visit = db.Column(db.DateTime, default=datetime.now())
    messages = db.relationship('Message', backref='topic', lazy='dynamic')

    def __repr__(self):
        return '<Topic %r>' % self.namespace

    @staticmethod
    def init_topic():
        public_topic = Topic(namespace='public')
        db.session.add(public_topic)
        db.session.commit()

    @staticmethod
    def create_topic(namespace: str):
        topic = Topic(namespace=namespace)
        db.session.add(topic)
        db.session.commit()
        return topic
