from .. import db, socketio, mq
from datetime import datetime
from ..models import Role, User, Message, Topic
from functools import lru_cache
import json


@lru_cache(maxsize=16)
def get_topic_name_list():
    tmp = Topic.query.order_by(Topic.id.asc()).all()
    topic_name_list = []
    for topic in tmp:
        if topic.namespace != "public":
            topic_name_list.append(topic.namespace)
    print("get_topic_list()", topic_name_list)
    return topic_name_list


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


def get_message_history(topic_name):
    lst = []
    topic = Topic.query.filter_by(namespace=topic_name).first()
    assert topic is not None
    sql = db.session.query(Message.id, User.name, Message.content, Message.create_time). \
        filter(User.id == Message.user_id).filter(Message.topic_id == topic.id).order_by(
        Message.id.desc()).limit(50).all()
    print("query SQL:", str(sql))
    for message_id, user_name, content, time in sql:
        d = {"data": "{author}@{time}: {message}".format(author=user_name,
                                                         message=content,
                                                         time=time.strftime("%Y-%m-%d %H:%M:%S")),
             "topic": topic_name,
             "count": message_id}
        lst.append(d)
    return json.dumps(lst[::-1])
