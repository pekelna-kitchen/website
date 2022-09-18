from app import app
from flask_script import Manager, Server

manager = Manager(app)
manager.add_command('server', Server)

if __name__ == '__main__':
    manager.run()
