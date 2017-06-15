from stomp import Connection, ConnectionListener
from flask import current_app, Flask, g


class MyListener(ConnectionListener):
    def __init__(self, conn, broadcast_interface, reconnect_and_subscribe, messages):
        self.conn = conn
        self.broadcast_interface = broadcast_interface
        self.reconnect_and_subscribe = reconnect_and_subscribe
        self.messages = messages
        print("MyListener inited!")

    def on_error(self, headers, message):
        print('received an error "%s"' % message)
        if self.broadcast_interface:
            self.broadcast_interface(message)

    def on_message(self, headers, message):
        self.messages.append(message)
        if self.broadcast_interface:
            self.broadcast_interface(message)

    def on_disconnected(self):
        print('disconnected, try to reconnect')
        if self.reconnect_and_subscribe:
            self.reconnect_and_subscribe()


class Mq(object):
    def __init__(self, app=None):
        self.__namespace = "default"
        self.__broadcast_interface = None
        self.stomp_url = None
        self.port = None
        self.conn = None
        self.listener = None
        self.connect_name = "flask_app"
        self.passcode = "default"
        self.messages = []
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['mq'] = self
        app.context_processor(self.context_processor)
        self.stomp_url = app.config['STOMP_URL']
        self.port = app.config['STOMP_PORT']
        self.namespace = app.config['STOMP_NAMESPACE']
        self.conn = Connection([(self.stomp_url, self.port)])
        self.conn.start()
        self.conn.connect(self.connect_name, self.passcode)
        self.subscribe(self.namespace)

    def subscribe(self, namespace):
        self.namespace = namespace
        self.listener = MyListener(self.conn,
                                   self.broadcast_interface,
                                   self.reconnect_and_subscribe,
                                   self.messages)
        self.conn.subscribe(destination=self.namespace, id="flask_app")
        self.conn.set_listener("test2", self.listener)

    def send(self, content: str):
        self.conn.send(destination=self.namespace, body=content)

    def disconnect(self):
        self.conn.disconnect()

    def reconnect_and_subscribe(self):
        self.conn.connect(self.connect_name, self.passcode)
        self.conn.start()
        self.subscribe(self.namespace)

    @property
    def namespace(self):
        return self.__namespace

    @namespace.setter
    def namespace(self, name_space: str):
        if not name_space.startswith("/topic/"):
            name_space = "/topic/" + name_space
        self.__namespace = name_space

    @property
    def broadcast_interface(self):
        return self.__broadcast_interface

    @broadcast_interface.setter
    def broadcast_interface(self, broadcast_interface):
        self.listener.broadcast_interface = broadcast_interface
        self.__broadcast_interface = broadcast_interface

    @staticmethod
    def context_processor():
        return {
            'mq': current_app.extensions['mq']
        }

    # noinspection PyMethodMayBeStatic
    def create(self, stomp_url, port):
        return current_app.extensions['mq'](stomp_url, port)
