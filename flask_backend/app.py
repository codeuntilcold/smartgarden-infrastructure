from flask import Flask, render_template
from flask_socketio import SocketIO, send
from Adafruit_IO import MQTTClient, Client
import sys


# SOCKET INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret'
socketio = SocketIO(app)


AIO_FEED_IDS = ["bbc-temp"]
AIO_USERNAME = "toilaaihcmut"
AIO_KEY = "aio_eVKn92mKQRDZCyoUDXowg5meHC4n"


def connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_IDS:
        client.subscribe(feed)


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit(1)


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribe thanh cong...")

# EMIT NEW DATA TO SOCKETS
def message(client, feed_id, payload):
    print("Nhan du lieu: " + payload + " tu " + feed_id)

    # "Broadcast" payload from feed_id to feed_id listeners
    socketio.emit(feed_id, payload)


# MQTT CLIENT INIT
client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()


# Reserved keywords for events: connect, disconnect, message, json
@socketio.on('connect')
def initialize_socket():
    send("Successfully connected")


@app.route('/')
def index():
    # Depend on client info, we give them the feed_id
    return render_template('index.html',
                           hostname='localhost',
                           port='5000',
                           sub_to_feed_id=AIO_FEED_IDS[0])


# REST CLIENT INIT
aio = Client(AIO_USERNAME, AIO_KEY)


@app.route('/dashboard')
def test():
    nval = 100
    temp = [float(d.value) for d in aio.data("bbc-temp")][:nval]
    humid = [float(d.value) for d in aio.data("bbc-humid")][:nval]
    light = [float(d.value) for d in aio.data("bbc-temp1")][:nval]

    return render_template('dashboard.html', **locals())


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app)