from flask import Flask, render_template, jsonify, abort
from flask_socketio import SocketIO, send
from Adafruit_IO import MQTTClient, Client
import sys
import json
from datetime import datetime
from pytz import timezone

# SOCKET INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret'
socketio = SocketIO(app, cors_allowed_origins='*')


AIO_FEED_IDS = ["bbc-test-json", "bbc-led"]
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
    data = {}
    data['test'] = aio.data("bbc-test-json")

    temp = [float(json.loads(d.value)['temp']) for d in data['test']]
    humid = [float(json.loads(d.value)['humid']) for d in data['test']]
    # light = [float(json.loads(d.value)['light']) for d in data['test']]

    return render_template('dashboard.html', **locals())


# Get full data on the feed
@app.route('/history/<string:feed_key>')
def get_history_data(feed_key):
    response_data = {}
    if feed_key == AIO_FEED_IDS[0]:
        response_data["time"] = [d.created_at for d in aio.data(AIO_FEED_IDS[0])]
        value = [json.loads(d.value) for d in aio.data(AIO_FEED_IDS[0])]
        response_data["temp"] = [v['temp'] for v in value]
        response_data["humid"] = [v['humid'] for v in value]
        response_data["light"] = [v['light'] for v in value]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["temp"].reverse()
        response_data["humid"].reverse()
        response_data["light"].reverse()
    elif feed_key == AIO_FEED_IDS[1]:
        response_data["time"] = [d.created_at for d in aio.data(AIO_FEED_IDS[1])]
        response_data["value"] = [d.value for d in aio.data(AIO_FEED_IDS[1])]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["value"].reverse()
    return jsonify(response_data)


# Get a number of rows data on feed (use to load graph when in sensor page)
@app.route('/history/<string:feed_key>/<int:num_rows>')
def get_history_data_with_num_rows(feed_key, num_rows):
    response_data = {}
    if feed_key == AIO_FEED_IDS[0]:
        response_data["time"] = [d.created_at for d in aio.data(AIO_FEED_IDS[0])][:num_rows]
        value = [json.loads(d.value) for d in aio.data(AIO_FEED_IDS[0])]
        value_slice = value[:num_rows]
        response_data["temp"] = [v['temp'] for v in value_slice]
        response_data["humid"] = [v['humid'] for v in value_slice]
        response_data["light"] = [v['light'] for v in value_slice]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["temp"].reverse()
        response_data["humid"].reverse()
        response_data["light"].reverse()
    elif feed_key == AIO_FEED_IDS[1]:
        response_data["time"] = [d.created_at for d in aio.data(AIO_FEED_IDS[1])][:num_rows]
        response_data["value"] = [d.value for d in aio.data(AIO_FEED_IDS[1])][:num_rows]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["value"].reverse()
    return jsonify(response_data)


# Get the latest value of all sensor
@app.route('/current')
def get_current_sensor_data():
    response_data = json.loads(aio.data(AIO_FEED_IDS[0])[0].value)
    response_data["time"] = datetime.strptime(aio.data(AIO_FEED_IDS[0])[0].created_at, '%Y-%m-%dT%H:%M:%SZ').astimezone(timezone("UTC"))
    return jsonify(response_data)


# Control device <bbc-led: control light; bbc-pump: control pump> (status: 0 - OFF, 1 - ON)
@app.route('/control/<string:feed_key>/<int:status>', methods=["POST"])
def control_device(feed_key, status):
    try:
        client.publish(feed_key, status)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except:
        return abort(404)


if __name__ == '__main__':
    # app.run(debug=True)
    socketio.run(app)
