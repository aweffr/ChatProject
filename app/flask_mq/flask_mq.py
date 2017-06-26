from stomp import Connection, ConnectionListener
from flask import current_app, Flask, g


class MyListener(ConnectionListener):
    def __init__(self, listener_id, conn, namespace, callback):
        self.id = listener_id
        self.conn = conn
        self.namespace = namespace
        self.broadcast_func = callback

    def on_error(self, headers, message):
        print('received an error "%s"' % message)

    def on_message(self, headers, message):
        if headers['destination'] != self.namespace:
            return
        if self.broadcast_func is not None:
            self.broadcast_func(self.namespace, message)
        else:
            print("""received an message, header:{header}, body:{message}""".
                  format(header=headers, message=message))

    def on_disconnected(self):
        print('disconnected')

    def __repr__(self):
        return "<MyListener namespace=%r>" % self.namespace


class Mq(object):
    def __init__(self, app=None):
        self.namespace = "default"
        self.__broadcast_interface = None
        self.connect_name = "flask_web"
        self.passcode = "passcode"
        self.stomp_url, self.port, self.conn = None, None, None
        self.listeners = dict()
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['mq'] = self
        app.context_processor(self.context_processor)

        self.stomp_url = app.config['STOMP_URL']
        self.port = app.config['STOMP_PORT']
        self.namespace = \
            self.regular_namespace(app.config['STOMP_PUBLIC_NAMESPACE'])

        self.connect()

    def has_listener(self, namespace):
        namespace = "flask_app" + self.regular_namespace(namespace)
        return namespace in self.listeners

    def connect(self):
        self.conn = Connection([(self.stomp_url, self.port)])
        self.conn.start()
        self.conn.connect(self.connect_name, self.passcode)

    def subscribe(self, namespace, callback_func):
        if not namespace.startswith("/topic/"):
            namespace = "/topic/" + namespace

        listener_id = "flask_app" + namespace
        listener = MyListener(listener_id=listener_id,
                              conn=self.conn,
                              namespace=namespace,
                              callback=callback_func)
        self.listeners[listener_id] = listener
        self.conn.subscribe(destination=namespace, id=listener_id)
        print("Before subscribe, self.conn.transport.listeners=", self.conn.transport.listeners)
        self.conn.set_listener(listener_id, listener)
        print("After subscribe, self.conn.transport.listeners=", self.conn.transport.listeners)

    def send(self, content: str, namespace: str = None):
        if namespace is None:
            namespace = self.namespace
        elif not namespace.startswith("/topic/"):
            namespace = "/topic/" + namespace
        self.conn.send(destination=namespace, body=content)

    def disconnect(self):
        self.conn.disconnect()

    def reconnect_and_subscribe(self):
        self.conn.connect(self.connect_name, self.passcode)
        self.conn.start()
        self.subscribe(self.namespace)

    @staticmethod
    def regular_namespace(namespace: str):
        if not namespace.startswith("/topic/"):
            namespace = "/topic/" + namespace
        return namespace

    @staticmethod
    def context_processor():
        return {
            'mq': current_app.extensions['mq']
        }

    # noinspection PyMethodMayBeStatic
    def create(self, stomp_url, port):
        return current_app.extensions['mq'](stomp_url, port)
