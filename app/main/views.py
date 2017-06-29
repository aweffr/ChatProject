from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, g, current_app
from flask_socketio import emit, join_room, rooms

from . import main
from .. import db
from .. import mq
from .. import socketio
from ..models import Message
from .service import update_or_create_user, get_user_id, get_message_history, update_or_create_topic
from .service import get_topic_name_list
import json


def broadcast_to_client(namespace: str, message):
    message = json.loads(message)
    send_room = namespace.replace("/topic", "", 1).strip("/")
    if send_room != "public":
        socketio.emit("radio", {"data": message['data'], "count": message['count']},
                      namespace="/room1", room=send_room)
    else:
        socketio.emit("radio", {"data": message['data'], "count": message['count'], "topic": message['topic']},
                      namespace="/room1", broadcast=True)


@socketio.on_error('/room1')
def error_handler_chat(e):
    print("socket Error:", e)


@socketio.on("connect_ack", namespace="/room1")
def connect_ack(recv_data):
    """
    在收到成功连接的信息时，会做两件事:
    1. 向客户端通过socket发送“XX进入聊天室的字符串”。
    2. 后台join_room，把用户放到topic对应的room里。
    :param recv_data:
    :return:
    """
    if "first_ack" in session and session["first_ack"]:
        data = "{author}@{time} 重新连接".format(author=session['name'],
                                             time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    elif recv_data['data'] == 'Connected!':
        data = "{author}@{time} 进入了聊天室".format(author=session['name'],
                                               time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        session['first_ack'] = True
    else:
        data = "Error!"

    topic_name = recv_data['topic']
    join_room(recv_data['topic'])
    topic = update_or_create_topic(topic_name=topic_name)
    session["topic_id"] = topic.id

    if not mq.has_listener(topic_name):
        mq.subscribe(namespace=topic_name, callback_func=broadcast_to_client)

    emit("to_client", {"data": data, "count": '/'})


@socketio.on("to_server", namespace="/room1")
def recv(recv_data):
    if 'id' not in session:
        name = session['name']
        user_id = get_user_id(name)
        session['id'] = user_id
    name = session['name']
    topic_name = recv_data['topic']

    message = Message(user_id=session['id'],
                      content=recv_data['data'],
                      topic_id=session["topic_id"],
                      create_time=datetime.now())
    db.session.add(message)
    db.session.commit()
    data = "{author}@{time}: {message}".format(author=name,
                                               time=message.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                                               message=message.content)

    mq.send(content=json.dumps({"data": data, "count": message.id, "topic": topic_name}),
            namespace=topic_name)


@socketio.on("get_history_from_server", namespace="/room1")
def get_history(recv_data):
    if 'id' not in session:
        name = session['name']
        user_id = get_user_id(name)
        session['id'] = user_id

    topic_name = recv_data['topic']
    data = get_message_history(topic_name=topic_name)

    emit("return_history_to_client", {"data": data}, broadcast=False)


@main.route("/", methods=['GET', 'POST'])
def index():
    user = session.get("name", None)
    if user is None:
        if "active_logout" in session and session["active_logout"] is True:
            session.pop("active_logout")
        else:
            flash('请先登录!')
        return redirect(url_for("auth.login"))
    else:
        return redirect(url_for(".public_channel"))



@main.route("/public_channel", methods=['GET'])
def public_channel():
    topic_name_list = get_topic_name_list()
    if 'name' not in session:
        return redirect(url_for('.index'))
    return render_template('topic_channel.html', name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow(),
                           allow_input=True,
                           topic_name="public",
                           topic_name_list=topic_name_list)


@main.route("/channel-<topic_name>", methods=['GET'])
def topic_channel(topic_name):
    if 'name' not in session:
        return redirect(url_for('.index'))
    topic_name_list = get_topic_name_list()
    topic = update_or_create_topic(topic_name)
    return render_template('topic_channel.html', name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow(),
                           allow_input=True,
                           topic_name=topic_name,
                           topic_name_list=topic_name_list)


@main.route("/clear", methods=['GET'])
def clear():
    if 'name' in session:
        session.pop('name')
    if 'first_ack' in session:
        session.pop('first_ack')
    session['known'] = False
    return redirect(url_for('.index'))
