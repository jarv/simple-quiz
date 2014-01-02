# Set the path
import os
os.environ['FLASK_SETTINGS'] = 'cfg/prod.py'
import sys
from simple_quiz import app
from flask.ext.script import Manager, Server
from simple_quiz_tests import StateTestCase
from simple_quiz.models import user_datastore

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'simple_quiz/cfg')))
manager = Manager(app)

# Turn on debugger by default and reloader
manager.add_command("runserver", Server(
    use_debugger=True,
    use_reloader=True,
    host='0.0.0.0')
)


if __name__ == "__main__":
    manager.run()
