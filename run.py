from distutils.log import debug
from flask_backend import socketio, app

if __name__ == '__main__':
    socketio.run(app, debug=True)