from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, g
from flask_socketio import emit

from . import main
from .forms import NameForm
from .. import db
from .. import mq
from .. import socketio
from ..models import User, Message
from .service import update_or_create_user, get_user_id, get_message_history
import json


def broadcast_to_client(message):
    message = json.loads(message)
    socketio.emit("radio", {"data": message['data'], "count": message['count']},
                  namespace="/room1", broadcast=True)


@socketio.on_error('/room1')  # handles the '/chat' namespace
def error_handler_chat(e):
    print("Error:", e)
    return redirect(url_for("main.index"))


@socketio.on("connect_ack", namespace="/room1")
def connect_ack(recv_data):
    if recv_data['data'] == 'Connected!' and 'first_ack' not in session:
        data = "@{author} has enter the room!".format(author=session['name'])
        session['first_ack'] = True
    else:
        data = "Error!"
    if mq.broadcast_interface is None:
        mq.broadcast_interface = broadcast_to_client
    emit("to_client", {"data": data, "count": '/'}, broadcast=True)


@socketio.on("to_server", namespace="/room1")
def recv(recv_data):
    if 'id' not in session:
        name = session['name']
        user_id = get_user_id(name)
        session['id'] = user_id
    name = session['name']
    message = Message(user_id=session['id'], content=recv_data['data'])
    db.session.add(message)
    data = "@{author}: {message}".format(author=name, message=message.content)
    db.session.commit()

    mq.send(json.dumps({"data": data, "count": message.id}))
    # emit("to_client", {"data": data, "count": message.id}, broadcast=True)


@socketio.on("get_history_from_server", namespace="/room1")
def get_history(recv_data):
    if 'id' not in session:
        name = session['name']
        user_id = get_user_id(name)
        session['id'] = user_id
    data = get_message_history()
    emit("return_history_to_client", {"data": data}, broadcast=True)


@main.route("/", methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        user = update_or_create_user(name)
        session['name'] = user.name
        session['known'] = True
        form.name.data = ""
        return redirect(url_for(".chat"))
    return render_template('index.html',
                           form=form, name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow())


@main.route("/chat", methods=['GET'])
def chat():
    if 'name' not in session:
        flash('Please enter your name first!')
        return redirect(url_for('.index'))
    return render_template('chat.html', name=session.get("name"),
                           known=session.get("known", False),
                           current_time=datetime.utcnow())


@main.route("/clear", methods=['GET'])
def clear():
    if 'name' in session:
        session.pop('name')
    session['known'] = False
    return redirect(url_for('.index'))
