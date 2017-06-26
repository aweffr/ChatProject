from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, g
from flask_socketio import emit, join_room, rooms

from . import main
from .forms import NameForm
from .. import db
from .. import mq
from .. import socketio
from ..models import Message
from .service import update_or_create_user, get_user_id, get_message_history, update_or_create_topic
import json


def broadcast_to_client(namespace: str, message):
    message = json.loads(message)
    send_room = namespace.replace("/topic", "", 1).strip("/")
    print("Sending Room name:", send_room)
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
    if recv_data['data'] == 'Connected!' and 'first_ack' not in session:
        data = "@{author} has enter the room!".format(author=session['name'])
        session['first_ack'] = True
    elif 'first_ack' not in session:
        data = "ReConnect."
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
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        user = update_or_create_user(name)
        session['name'] = user.name
        session['known'] = True
        form.name.data = ""
        return redirect(url_for(".public_channel"))
    return render_template('index.html',
                           form=form, name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow())


@main.route("/public_channel", methods=['GET'])
def public_channel():
    if 'name' not in session:
        flash('Please enter your name first!')
        return redirect(url_for('.index'))
    return render_template('topic_channel.html', name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow(),
                           allow_input=True,
                           topic_name="public")


@main.route("/channel-<topic_name>", methods=['GET'])
def topic_channel(topic_name):
    if 'name' not in session:
        flash('Please enter your name first!')
        return redirect(url_for('.index'))
    topic = update_or_create_topic(topic_name)
    return render_template('topic_channel.html', name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow(),
                           allow_input=True,
                           topic_name=topic_name)


@main.route("/clear", methods=['GET'])
def clear():
    if 'name' in session:
        session.pop('name')
    if 'first_ack' in session:
        session.pop('first_ack')
    session['known'] = False
    return redirect(url_for('.index'))
