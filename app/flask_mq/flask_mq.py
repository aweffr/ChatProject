from stomp import Connection, ConnectionListener
from flask import current_app, Flask, g

# TODO: 将namespace抽出来成接口
'''
先做连接, 发送, 订阅所需的参数分离

订阅作为子方法/或者独立出来

测试同时连接两个Topic时候的功能对不对,能否分别推送

发送作为子方法

先做发送 check
'''


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
            print("""received an message, header:{header}, body:{message}""".
                  format(header=headers, message=message))
            self.broadcast_func(self.namespace, message)
        else:
            print("""received an message, header:{header}, body:{message}""".
                  format(header=headers, message=message))

    def on_disconnected(self):
        print('disconnected')


class Mq(object):
    def __init__(self, app=None):
        self.__namespace = "default"
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
        self.namespace = app.config['STOMP_PUBLIC_NAMESPACE']

        self.connect()

    def has_listener(self, namespace):
        namespace = self.regular_namespace(namespace)
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
        self.conn.set_listener(listener_id, listener)

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

    @property
    def namespace(self):
        return self.__namespace

    @namespace.setter
    def namespace(self, namespace: str):
        if not namespace.startswith("/topic/"):
            namespace = "/topic/" + namespace
        self.__namespace = namespace

    @property
    def broadcast_interface(self):
        return self.__broadcast_interface

    @broadcast_interface.setter
    def broadcast_interface(self, broadcast_interface):
        self.listener.broadcast_interface = broadcast_interface
        self.__broadcast_interface = broadcast_interface

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
