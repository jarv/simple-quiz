from flask import Flask, render_template, request
from flask.ext.mongoengine import MongoEngine

app = Flask(__name__)
app.config.from_envvar('FLASK_SETTINGS')
db = MongoEngine(app)

if app.config['DEBUG']:
    from werkzeug import SharedDataMiddleware
    import os
    app.wsgi_app = SharedDataMiddleware(app.wsgi_app, {
        '/': os.path.join(os.path.dirname(__file__), '../static')
    })


# Create database connection object
db = MongoEngine(app)

import simple_quiz.views
import simple_quiz.models

