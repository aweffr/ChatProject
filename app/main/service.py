from .. import db, socketio, mq
from flask import g
import sys
from datetime import datetime
from ..models import Role, User, Message, Topic
import json


# TODO: 把flask.g用上

# class Broadcaster(mq.BroadcasterBase):
#     def __init__(self, namespace: str):
#         if namespace.startswith("/topic"):
#             namespace.replace("/topic", "")
#         self.client_namespace = namespace
#
#     def send(self, message):
#         message = json.loads(message)
#         socketio.emit("radio", {"data": message['data'], "count": message['count']},
#                       namespace=self.client_namespace, broadcast=True)

def update_or_create_topic(topic_name):
    topic = Topic.query.filter_by(namespace=topic_name).first()
    if topic is None:
        topic = Topic.create_topic(namespace=topic_name)
    else:
        topic.last_visit = datetime.now()
    return topic


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
