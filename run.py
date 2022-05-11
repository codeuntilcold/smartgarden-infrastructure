import eventlet
eventlet.monkey_patch()
from flask_backend import socketio, app

if __name__ == '__main__':
    socketio.run(app)
