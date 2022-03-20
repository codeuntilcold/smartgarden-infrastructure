from flask import Flask, render_template
from Adafruit_IO import MQTTClient, Client, Data
import sys


AIO_FEED_ID = "bbc-temp"
AIO_USERNAME = "toilaaihcmut"
AIO_KEY = "aio_eVKn92mKQRDZCyoUDXowg5meHC4n"


def connected(client):
    print("Ket noi thanh cong...")
    client.subscribe(AIO_FEED_ID)


def subscribe(client, userdata, mid, granted_qos):
    print("Subscribe thanh cong...")


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit(1)


def message(client, feed_id, payload):
    print("Nhan du lieu: " + payload)
    # Gửi xuống react, render được
    # Socket


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()

aio = Client(AIO_USERNAME, AIO_KEY)


app = Flask(__name__)


@app.route('/')
def index():
    return '<a href="/dashboard">Go to dashboard</a>'


@app.route('/dashboard')
def test():
    name = 'Temp'
    data = {}
    data['temp'] = aio.data("bbc-temp")
    data['humid'] = aio.data("bbc-humid")
    data['light'] = aio.data("bbc-temp1")
    temp = [float(d.value) for d in data['temp']]
    temp = temp[:100]
    humid = [float(d.value) for d in data['humid']]
    humid = humid[:100]
    light = [float(d.value) for d in data['light']]
    light = light[:100]

    return render_template('index.html', **locals())


if __name__ == '__main__':
    app.run(debug=True)
