from .. import db
from flask import g
from datetime import datetime
from ..models import User, Message
from .. import socketio
from flask_socketio import emit
import json


def update_or_create_user(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        user = create_user(name)
    else:
        user.last_login = datetime.now()
    return user


def create_user(name):
    user = User(name=name)
    db.session.add(user)
    return user


def get_user_id(name):
    user = User.query.filter_by(name=name).first()
    return user.id


def get_message_history():
    lst = []
    for message_id, user_name, content, time in \
            db.session.query(Message.id, User.name, Message.content, Message.create_time). \
                    filter(User.id == Message.user_id).order_by(Message.id.desc()).limit(50).all():
        d = {
            "data": "@{author}: {message}".format(author=user_name, message=content),
            "count": message_id
        }
        lst.append(d)
    return json.dumps(lst[::-1])
