import sys
from Adafruit_IO import MQTTClient
import random
import time
import serial.tools.list_ports
import json

AIO_FEED_IDS = ["bbc-test-json"]
AIO_USERNAME = "toilaaihcmut"
AIO_KEY = "aio_eVKn92mKQRDZCyoUDXowg5meHC4n"


def connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_IDS:
        client.subscribe(feed)


def subscribe(client, userdata, mid, granted_qos):
    print("Subcribe thanh cong...")


def disconnected(client):
    print("Ngat ket noi...")
    sys.exit(1)


def message(client, feed_id, payload):
    print("Nhan du lieu: " + payload)
    # if isMicrobitConnected:
    #     ser.write((str(payload) + "#").encode())


client = MQTTClient(AIO_USERNAME, AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_message = message
client.on_subscribe = subscribe
client.connect()
client.loop_background()


def getPort():
    ports = serial.tools.list_ports.comports()
    N = len(ports)
    commPort = "None"
    for i in range(0, N):
        port = ports[i]
        strPort = str(port)
        if "USB Serial Device" in strPort:
            splitPort = strPort.split(" ")
            commPort = (splitPort[0])
    return commPort


isMicrobitConnected = False
if getPort() != "None":
    ser = serial.Serial(port=getPort(), baudrate=115200)
    isMicrobitConnected = True


def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[1] == "TEMP" and splitData[2] == "HUMI":
            client.publish("bbc-temp", splitData[3])
            client.publish("bbc-humid", splitData[4])
        elif splitData[1] == "TEMP":
            client.publish("bbc-temp", splitData[2])
        elif splitData[2] == "HUMI":
            client.publish("bbc-humid", splitData[3])
        elif splitData[1] == "LIGHT":
            client.publish("bbc-temp1", splitData[2])
    except:
        pass


mess = ""


def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            processData(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]


# function to test publish json to only one feed
def test_post_json():
    arr = {}
    value = random.randint(0, 100)
    print("Cap nhat:", value)
    arr["temp"] = value
    arr["humid"] = value
    arr["light"] = value

    if len(arr) == 3:
        client.publish("bbc-test-json", json.dumps(arr))


while True:
    # if isMicrobitConnected:
    #     readSerial()
    test_post_json()
    time.sleep(5)
