from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from .flask_mq import Mq
from flask_login import LoginManager
from config import config

'''
使用程序工厂函数:
延迟创建程序实例, 把创建过程移到可显示调用的工厂函数中.
'''

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
socketio = SocketIO()
mq = Mq()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = "auth.login"


def create_app(config_name: str):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app()

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    socketio.init_app(app, async_mode=app.config['ASYNC_MODE'], engineio_logger=app.config['ENABLE_ENGINEIO_LOGGER'])
    mq.init_app(app)
    login_manager.init_app(app)

    # 附加路由和自定义的错误页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix="/auth")

    return app
