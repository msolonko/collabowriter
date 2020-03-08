from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_debug import Debug

#db connection
application = Flask(__name__)
application.config['SECRET_KEY'] = '38a76db9c969addb95283f371c4196e7ae88ee1b007c63f03e07230120aff345896444'
application.config['SQLALCHEMY_DATABASE_URI']='sqlite:///freewrite.db'
Debug(application)
db = SQLAlchemy(application)
bcrypt = Bcrypt(application)
login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from project import routes
