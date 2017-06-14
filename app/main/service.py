from .. import db
from flask import g
from ..models import User, Message
import json


def get_or_create_user(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        user = create_user(name)
    return user


def create_user(name):
    user = User(name=name)
    db.session.add(user)
    return user


def get_user_id(name):
    user = User.query.filter_by(name=name).first()
    return user.id


def get_message_history():
    messages = Message.query.order_by("id").all()
    lst = []

    for m in messages:
        lst.append({"data": "@{author}: {message}".format(author=m.user_id, message=m.content)})
    return json.dumps(lst)
