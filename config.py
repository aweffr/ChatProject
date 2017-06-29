import os

basedir = os.path.abspath(os.path.dirname(__file__))


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
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or "mysql://xxx:yyy@aweffr.win/chat"
    DROP_AND_CREATE = os.environ.get("DROP_AND_CREATE" or False)
    ENABLE_ENGINEIO_LOGGER = False


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("TEST_DATABASE_URI") or \
                              "sqlite:///" + os.path.join(basedir, "data-test.sqlite")


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URI") or \
                              "mysql://xxx:yyy@aweffr.win/chat"
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
