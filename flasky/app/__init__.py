from flask import Flask 
from flask.ext.bootstrap import Bootstrap 
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy 
from flask.ext.login import LoginManager
from config import config
import logging
from logging.handlers import TimedRotatingFileHandler
import os

basedir=os.path.abspath(os.path.dirname(__file__))
bootstrap=Bootstrap()
moment=Moment()
db=SQLAlchemy( )
log = logging.getLogger()
formatter = logging.Formatter('%(name)-12s %(asctime)s level-%(levelname)-8s %(funcName)s %(message)s')   
fileTimeHandler = TimedRotatingFileHandler(basedir+"/logs/flask.log", 'midnight',1)

fileTimeHandler.suffix = "%Y%m%d.log"  
fileTimeHandler.setFormatter(formatter)
logging.basicConfig(level = logging.NOTSET)
fileTimeHandler.setFormatter(formatter)
log.addHandler(fileTimeHandler)

log.error(basedir)

 

login_manager=LoginManager()
login_manager.session_protection='basic'
login_manager.login_view='auth.login'


def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    return app