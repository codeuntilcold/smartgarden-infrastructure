from Adafruit_IO import MQTTClient, Client
import sys


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


# MQTT CLIENT INIT
client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_subscribe = subscribe

aio = Client(AIO_USERNAME, AIO_KEY)
