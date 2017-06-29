import os
import sys
from app import create_app, db, socketio, mq
from app.models import Role, User, Message, Topic
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
                mq=mq)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)


@manager.command
def develop_run():
    """Run with debug"""
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)


@manager.command
def production_run():
    "Run with produciton"
    socketio.run(app, host="0.0.0.0", port=5000, debug=False)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover(start_dir='tests', pattern='test*.py')
    unittest.TextTestRunner(verbosity=2).run(tests)


@manager.command
def init_db():
    "Initialize the database."
    db.drop_all()
    db.create_all()
    Role.init_roles()
    User.init_user()
    Topic.init_topic()


if __name__ == "__main__":
    manager.run()
