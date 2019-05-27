#talismansoftwaresolutions/__init__.py

from flask import Flask, Blueprint

app = Flask(__name__)
app.config.from_pyfile('_config.py')

import views

#new
#from talismansoftwaresolutions.tasks.views import tasks_blueprint
from .tasks.views import tasks_blueprint
from .users.views import users_blueprint

app.register_blueprint(users_blueprint)
app.register_blueprint(tasks_blueprint)
#end new


