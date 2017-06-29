from flask import render_template, redirect, request, url_for, flash, session, g
from flask_login import login_user, login_required, logout_user
from . import auth
from .. import db
from ..models import User
from .forms import LoginForm, RegistrationForm

from ..main.service import get_topic_name_list


@auth.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            session["name"] = user.name
            session["known"] = True
            return redirect(request.args.get('next') or url_for("main.index"))
        flash("Invalid username or password.")
    return render_template("auth/login.html", form=form,
                           topic_name_list=get_topic_name_list())


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    flash("已登出")
    if "name" in session:
        session.pop("name")
    if "known" in session:
        session.pop("known")
    session["active_logout"] = True
    return redirect(url_for("main.index"))


@auth.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    name=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        flash("注册成功， 请登录")
        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form,
                           topic_name_list=get_topic_name_list())
