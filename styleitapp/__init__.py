#first open init beside the template folder which is the top root init. 
# after the init inside the template next is config.py not in instance
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from flask_socketio import SocketIO
from threading import Lock
# from flask_share import Share
# async_mode = None

#instantiate an object of Flask app
app = Flask(__name__, instance_relative_config=True)
csrf=CSRFProtect(app)

#Load the config file
from styleitapp import config
app.config.from_object(config.ProductionConfig)
app.config.from_pyfile('config.py', silent=False) #this is the config in instance folders

#database connection
db=SQLAlchemy(app)
migrate=Migrate(app,db)
mail=Mail(app)
sio = SocketIO(app, manage_session=True)
# sio = SocketIO(app, async_mode=async_mode)
# thread = None
# thread_lock = Lock()

# share = Share(app)


#load your routes here
from styleitapp.myroutes import adminroutes, userroutes #since routes is now a module on its own

#Load forms
from styleitapp import forms

#load models
from styleitapp import models
