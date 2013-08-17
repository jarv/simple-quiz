# Set the path
import os
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
    os.environ['FLASK_SETTINGS'] = 'cfg/prod.py'
    test_user = user_datastore.find_user(email='test@example.com')
    if not test_user:
        user_datastore.create_user(email='test@example.com', password='test')

    admin_role = user_datastore.find_or_create_role(name="admin")
    user_datastore.add_role_to_user(test_user, admin_role)
    test_user.save()
    manager.run()
