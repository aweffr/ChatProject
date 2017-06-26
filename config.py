import os

basedir = os.path.abspath(os.path.dirname(__file__))

# TODO: 从 Config生成Topic列表

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "DAYDAYUP"
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ASYNC_MODE = "gevent"
    ENABLE_ENGINEIO_LOGGER = False

    STOMP_URL = "101.37.24.136"
    STOMP_PORT = 61613
    STOMP_PUBLIC_NAMESPACE = "public"

    @staticmethod
    def init_app():
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or \
    #                           "sqlite:///" + os.path.join(basedir, "data-dev.sqlite")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "mysql://aweffr:summer123@aweffr.win/chat"
    DROP_AND_CREATE = os.environ.get("DROP_AND_CREATE" or False)
    ENABLE_ENGINEIO_LOGGER = False
    TOPIC_LIST = os.environ.get("DEV_TOPIC_LIST") or \
                 ["海底捞", "汉堡王", "漫画同好会", "小时代", "围观组"]


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI") or \
                              "sqlite:///" + os.path.join(basedir, "data-test.sqlite")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URI") or \
                              "sqlite:///" + os.path.join(basedir, "data.sqlite")


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
