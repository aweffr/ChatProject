from datetime import datetime
from flask import render_template, session, redirect, url_for, flash
from flask_socketio import emit

from . import main
from .forms import NameForm
from .. import db
from .. import socketio
from ..models import User, Message


@socketio.on("connect_ack", namespace="/room1")
def connect_ack(recv_data):
    if recv_data['data'] == 'Connected!':
        data = "@{author} has enter the room!".format(author=session['name'])
    else:
        data = "Error!"
    emit("to_client", {"data": data, "count": '/'}, broadcast=True)


@socketio.on("to_server", namespace="/room1")
def recv(recv_data):
    if 'id' not in session:
        user = User.query.filter_by(name=session['name']).first()
        session['id'] = user.id
        session['user'] = user
    user_id = session['id']
    name = session['name']
    message = Message(user_id=user_id, content=recv_data['data'])
    db.session.add(message)

    data = "@{author}: {message}".format(author=name, message=message.content)
    db.session.commit()
    emit("to_client", {"data": data, "count": message.id}, broadcast=True)


@main.route("/", methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        user = User(name=form.name.data)
        db.session.add(user)
        session['name'] = form.name.data
        form.name.data = ""
        return redirect(url_for(".index"))
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
        return redirect(url_for('.index'))
