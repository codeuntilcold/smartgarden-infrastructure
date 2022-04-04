
import serial.tools.list_ports
import random
import time
import  sys
from  Adafruit_IO import  MQTTClient
import json

AIO_FEED_IDS = ["bbc-test-json", "bbc-led", "bbc-pump"] #, "bbc-temp", "bbc-temp1"]

AIO_USERNAME = "toilaaihcmut"
AIO_KEY = "aio_eVKn92mKQRDZCyoUDXowg5meHC4n"

FIXED_PORT = False

def  connected(client):
    print("Ket noi thanh cong...")
    for feed in AIO_FEED_IDS:
        client.subscribe(feed)

def  subscribe(client , userdata , mid , granted_qos):
    print("Subcribe thanh cong...")

def  disconnected(client):
    print("Ngat ket noi...")
    sys.exit (1)

def  message(client , feed_id , payload):
    print("Nhan du lieu: " + payload)
    # print(type(payload), len(payload))
    if isMicrobitConnected:
        print("Sending " + payload)
        if feed_id == "bbc-led":
            ser.write(("LIGHT" + str(payload) + "#").encode())
        elif feed_id == "bbc-pump":
            ser.write(("PUMP" + str(payload) + "#").encode())

client = MQTTClient(AIO_USERNAME , AIO_KEY)
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
if FIXED_PORT == False:
    if getPort() != "None":
        ser = serial.Serial( port=getPort(), baudrate=115200)
        isMicrobitConnected = True
    # fixed com port
else:
    ser = serial.Serial(port='COM6', baudrate=115200)
    isMicrobitConnected = True

def processData(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[1] == "TEMP":
            client.publish("bbc-temp", splitData[3])
        elif splitData[2] == "HUMI":
            client.publish("bbc-temp", splitData[4])
        elif splitData[1] == "LIGHT":
            client.publish("bbc-temp1", splitData[2])
    except:
        pass

mess = ""

N_SENSORS = 2
n_recv = 0
curr_data = dict()

def processDataToJson(data):
    data = data.replace("!", "")
    data = data.replace("#", "")
    splitData = data.split(":")
    print(splitData)
    try:
        if splitData[1] == "TEMP" and splitData[2] == "HUMI":
            curr_data["temp"] = splitData[3]
            curr_data["humid"] = splitData[4]
        elif splitData[1] == "LIGHT":
            curr_data["light"] = splitData[2]
    except:
        return

    global n_recv
    n_recv += 1
    if n_recv >= N_SENSORS:
        n_recv = 0
        client.publish(AIO_FEED_IDS[0], json.dumps(curr_data))

def readSerial():
    bytesToRead = ser.inWaiting()
    if (bytesToRead > 0):
        global mess
        mess = mess + ser.read(bytesToRead).decode("UTF-8")
        while ("#" in mess) and ("!" in mess):
            start = mess.find("!")
            end = mess.find("#")
            # processData(mess[start:end + 1])
            processDataToJson(mess[start:end + 1])
            if (end == len(mess)):
                mess = ""
            else:
                mess = mess[end+1:]

# connect_sig = 0
while True:
    if isMicrobitConnected:
        # print("COM connected", connect_sig)
        # connect_sig += 1
        readSerial()

    time.sleep(3)
