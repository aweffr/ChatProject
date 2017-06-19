import os
import sys
from app import create_app, db, socketio, mq
from app.models import Role, User, Message, DatabaseInit, Topic
from flask_script import Manager, Shell, Command
from flask_migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app,
                db=db,
                Role=Role,
                User=User,
                Message=Message,
                mq=mq,
                DatabaseInit=DatabaseInit,
                # Broadcaster=Broadcaster)
                )


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


class MyRunserver(Command):
    def run(self):
        socketio.run(app)


class ResetDB(Command):
    def run(self):
        db.drop_all()
        db.create_all()
        Role.insert_roles()
        Topic.insert_topic()


manager.add_command("myrunserver", MyRunserver())
manager.add_command("resetdb", ResetDB())

if __name__ == "__main__":
    manager.run()
