from flask_backend.config import *
from Adafruit_IO import MQTTClient, Client
import sys
from flask_backend import *

def connected(client):
    print("Ket noi thanh cong...")
    for feed in ConfigClass.AIO_FEED_IDS:
        client.subscribe(feed)


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit(1)


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribe thanh cong...")


# EMIT NEW DATA TO SOCKETS
def message(_client, feed_id, payload):
    print("Nhan du lieu: " + payload + " tu " + feed_id)
    # "Broadcast" payload from feed_id to feed_id listeners
    socketio.emit(feed_id, payload)

# MQTT CLIENT INIT
client = MQTTClient(ConfigClass.AIO_USERNAME, ConfigClass.AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_subscribe = subscribe
client.on_message = message
client.connect()
client.loop_background()

aio = Client(ConfigClass.AIO_USERNAME, ConfigClass.AIO_KEY)