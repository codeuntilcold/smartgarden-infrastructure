from flask import Flask
from flask_socketio import SocketIO, send

from flask_backend.main.routes import main
from flask_backend.admin.routes import admin
from flask_backend.config import *

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret'
app.register_blueprint(main, url_prefix='/')
app.register_blueprint(admin, url_prefix='/admin')

# SOCKET INIT
socketio = SocketIO(app, cors_allowed_origins='*')

# EMIT NEW DATA TO SOCKETS
def message(client, feed_id, payload):
    print("Nhan du lieu: " + payload + " tu " + feed_id)

    # "Broadcast" payload from feed_id to feed_id listeners
    socketio.emit(feed_id, payload)

client.on_message = message
client.connect()
client.loop_background()

@socketio.on('connect')
def initialize_socket():
    send("Successfully connected")