#!/usr/bin/env python
import os
from app import create_app,db
from app.models import User,Role,Permission,DeviceInfo,OnlineDeviceInfo,WarnInfo
from flask.ext.script import Manager,Shell
from flask.ext.migrate import Migrate,MigrateCommand
from flask import Blueprint
import sys
defaultencoding = 'utf-8'
if sys.getdefaultencoding() != defaultencoding:
    reload(sys)
    sys.setdefaultencoding(defaultencoding)
app=create_app(os.getenv('FLASK_CONFIG')or 'default')

manager=Manager(app)
migrate=Migrate(app,db)


def make_shell_context():
    return dict(app=app,db=db,User=User,Role=Role,Permission=Permission,DeviceInfo=DeviceInfo,OnlineDeviceInfo=OnlineDeviceInfo,WarnInfo=WarnInfo)
manager.add_command("shell",Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)
@manager.command
def test():
    "run the unit tests"
    import unittest
    test=unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)



if __name__ == '__main__':
    manager.run()