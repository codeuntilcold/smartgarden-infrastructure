import json
from flask import jsonify
from flask_backend.config import *
from Adafruit_IO import MQTTClient, Client
import sys
import flask_backend
from flask_backend.main import *
from flask_backend.models import *
import numpy as np
from datetime import datetime

def get_fifty_data():
    with flask_backend.app.app_context():
        all_data = measure.query.order_by(measure.ID.desc()).limit(150)
        response1 = [data.as_dict()["value"] for data in all_data if data.as_dict()["type"] == 1]
        response2 = [data.as_dict()["value"] for data in all_data if data.as_dict()["type"] == 2]
        response3 = [data.as_dict()["value"] for data in all_data if data.as_dict()["type"] == 3]
        return response1, response2, response3


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
    temp, humid, light = get_fifty_data()
    q25_t, q75_t = np.percentile(temp, 25), np.percentile(temp, 75)
    q25_h, q75_h = np.percentile(humid, 25), np.percentile(humid, 75)
    q25_l, q75_l = np.percentile(light, 25), np.percentile(light, 75)
    iqr_t = q75_t - q25_t
    iqr_h = q75_h - q25_h
    iqr_l = q75_l - q25_l

    limit_iqr_t = 1.5*iqr_t
    limit_iqr_h = 1.5*iqr_h
    limit_iqr_l = 1.5*iqr_l
    
    lower_iqr_t, upper_iqr_t = q25_t - limit_iqr_t, q75_t + limit_iqr_t
    lower_iqr_h, upper_iqr_h = q25_h - limit_iqr_h, q75_h + limit_iqr_h
    lower_iqr_l, upper_iqr_l = q25_l - limit_iqr_l, q75_l + limit_iqr_l

    gardenID = 1 # the first garden
    payload = json.loads(payload)
    if int(payload["temp"]) >= lower_iqr_t and int(payload["temp"]) <= upper_iqr_t and int(payload["humid"]) >= lower_iqr_h and int(payload["humid"]) <= upper_iqr_h and int(payload["light"]) >= lower_iqr_l and int(payload["light"]) <= upper_iqr_l:

        # "Broadcast" payload from feed_id to feed_id listeners
        flask_backend.socketio.emit(feed_id, payload)

        # add data to database
        with flask_backend.app.app_context():
            cur_id = measure.query.order_by(measure.ID.desc()).first().as_dict()["ID"]
            temp_data = {"ID": cur_id + 1, "gardenID": gardenID, "type": 1, "value": payload["temp"], "time": datetime.now()}
            humid_data = {"ID": cur_id + 2, "gardenID": gardenID, "type": 2, "value": payload["humid"], "time": datetime.now()}
            light_data = {"ID": cur_id + 3, "gardenID": gardenID, "type": 3, "value": payload["light"], "time": datetime.now()}
            data = [temp_data, humid_data, light_data]
            for ele in data:
                new_line = measure(ele)
                db.session.add(new_line)
                db.session.commit()
    else:
        print("out")
        flask_backend.socketio.emit(feed_id, "There is a problem with the data")

# MQTT CLIENT INIT
client = MQTTClient(ConfigClass.AIO_USERNAME, ConfigClass.AIO_KEY)
client.on_connect = connected
client.on_disconnect = disconnected
client.on_subscribe = subscribe
client.on_message = message
client.connect()
client.loop_background()

aio = Client(ConfigClass.AIO_USERNAME, ConfigClass.AIO_KEY)
