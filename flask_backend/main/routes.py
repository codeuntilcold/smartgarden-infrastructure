from flask import Blueprint, render_template, jsonify, abort, request
import json
from datetime import datetime
import pytz
from flask_backend.config import ConfigClass
from flask_backend.main import *
from flask_backend.models import *
import numpy as np

main = Blueprint('main', __name__)

@main.route('/')
def main_page():
    return 'Welcome to Khu vườn thông minh API endpoints'

# Route to demo realtime connection
@main.route('/realtime')
def index():
    # Depend on client info, we give them the feed_id
    return render_template('index.html', sub_to_feed_id=ConfigClass.AIO_FEED_IDS[0])


# Get full data on the feed
@main.route('/history/<string:feed_key>')
def get_history_data(feed_key):
    response_data = {}
    if feed_key == ConfigClass.AIO_FEED_IDS[0]:
        response_data["time"] = [d.created_at for d in aio.data(ConfigClass.AIO_FEED_IDS[0])]
        value = [json.loads(d.value) for d in aio.data(ConfigClass.AIO_FEED_IDS[0])]
        response_data["temp"] = [v['temp'] for v in value]
        response_data["humid"] = [v['humid'] for v in value]
        response_data["light"] = [v['light'] for v in value]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["temp"].reverse()
        response_data["humid"].reverse()
        response_data["light"].reverse()
    elif feed_key == ConfigClass.AIO_FEED_IDS[1]:
        response_data["time"] = [d.created_at for d in aio.data(ConfigClass.AIO_FEED_IDS[1])]
        response_data["value"] = [d.value for d in aio.data(ConfigClass.AIO_FEED_IDS[1])]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["value"].reverse()
    elif feed_key == ConfigClass.AIO_FEED_IDS[2]:
        response_data["time"] = [d.created_at for d in aio.data(ConfigClass.AIO_FEED_IDS[2])]
        response_data["value"] = [d.value for d in aio.data(ConfigClass.AIO_FEED_IDS[2])]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["value"].reverse()
    return jsonify(response_data)


# Get a number of rows data on feed (use to load graph when in sensor page)
@main.route('/history/<string:feed_key>/<int:num_rows>')
def get_history_data_with_num_rows(feed_key, num_rows):
    response_data = {}
    if feed_key == ConfigClass.AIO_FEED_IDS[0]:
        response_data["time"] = [d.created_at for d in aio.data(ConfigClass.AIO_FEED_IDS[0])][:num_rows]
        value = [json.loads(d.value) for d in aio.data(ConfigClass.AIO_FEED_IDS[0])]
        value_slice = value[:num_rows]
        response_data["temp"] = [v['temp'] for v in value_slice]
        response_data["humid"] = [v['humid'] for v in value_slice]
        response_data["light"] = [v['light'] for v in value_slice]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["temp"].reverse()
        response_data["humid"].reverse()
        response_data["light"].reverse()
    elif feed_key == ConfigClass.AIO_FEED_IDS[1]:
        response_data["time"] = [d.created_at for d in aio.data(ConfigClass.AIO_FEED_IDS[1])][:num_rows]
        response_data["value"] = [d.value for d in aio.data(ConfigClass.AIO_FEED_IDS[1])][:num_rows]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["value"].reverse()
    elif feed_key == ConfigClass.AIO_FEED_IDS[2]:
        response_data["time"] = [d.created_at for d in aio.data(ConfigClass.AIO_FEED_IDS[2])][:num_rows]
        response_data["value"] = [d.value for d in aio.data(ConfigClass.AIO_FEED_IDS[2])][:num_rows]

        # Reverse list from furthest to nearest
        response_data["time"].reverse()
        response_data["value"].reverse()
    return jsonify(response_data)


# Get the latest value of all sensor
@main.route('/sensor/current')
def get_current_sensor_data():
    # from datetime import datetime
    # response_data = json.loads(aio.data(ConfigClass.AIO_FEED_IDS[0])[0].value)
    # response_data["time"] = datetime.strptime(aio.data(ConfigClass.AIO_FEED_IDS[0])[0].created_at, '%Y-%m-%dT%H:%M:%SZ').astimezone(pytz.timezone("UTC"))
    temp = measure.query.order_by(measure.ID.desc()).filter_by(type=1).first()
    humid = measure.query.order_by(measure.ID.desc()).filter_by(type=2).first()
    light = measure.query.order_by(measure.ID.desc()).filter_by(type=3).first()
    response_data = [temp.as_dict(), humid.as_dict(), light.as_dict()]
    return jsonify(response_data)


# Get the current state of device
@main.route('/<string:feed_key>/current')
def get_current_device_data(feed_key):
    # from datetime import datetime
    # response_data = {}

    # response_data["value"] = aio.data(feed_key)[0].value
    # response_data["time"] = datetime.strptime(aio.data(feed_key)[0].created_at, '%Y-%m-%dT%H:%M:%SZ')
    if feed_key == ConfigClass.AIO_FEED_IDS[1]:
        data = light.query.order_by(light.ID.desc()).first()
    else:
        data = pump.query.order_by(pump.ID.desc()).first()
    return jsonify(data.as_dict())


# Control device <bbc-led: control light; bbc-pump: control pump> (status: 0 - OFF, 1 - ON)
@main.route('/control/<string:gardenID>/<string:feed_key>/<int:status>', methods=["POST"])
def control_device(gardenID, feed_key, status):
    try:
        client.publish(feed_key, status)
        if feed_key == ConfigClass.AIO_FEED_IDS[1]:
            cur_id = light.query.order_by(light.ID.desc()).first().as_dict()["ID"]
            data = {"ID": cur_id + 1, "gardenID": gardenID, "time": datetime.now(), "status": status}
            new_line = light(data)
        else:
            cur_id = pump.query.order_by(pump.ID.desc()).first().as_dict()["ID"]
            data = {"ID": cur_id + 1, "gardenID": gardenID, "time": datetime.now(), "status": status}
            new_line = pump(data)
        db.session.add(new_line)
        db.session.commit()
        return json.dumps({ 'success': True }), 200
    except:
        return json.dumps({ 'success': False }), 404


# Load all garden
@main.route("/user/all_garden/<string:userID>")
def get_all_garden(userID):
    all_garden = garden.query.filter_by(userID=userID).all()
    response = [gd.as_dict() for gd in all_garden]
    return jsonify(response)


# Load, change garden information
@main.route("/user/garden_info/<string:gardenID>", methods=["GET", "POST"])
def get_garden_info(gardenID):
    garden_info = garden.query.filter_by(gardenID=gardenID).first()
    if request.method == "GET":
        return jsonify(garden_info.as_dict())
    elif request.method == "POST":
        change_data = request.get_json()
        garden_info.gardenID = change_data["gardenID"]
        garden_info.name = change_data["name"]
        garden_info.userID = change_data["userID"]
        garden_info.location = change_data["location"]
        garden_info.starttime = change_data["starttime"]
        garden_info.description = change_data["description"]
        garden_info.area = change_data["area"]
        garden_info.image = change_data["image"]

        db.session.add(garden_info)
        db.session.commit()
        return { "success": "ok" }


# Load sensor history information
@main.route("/user/sensor_history/<string:gardenID>")
def get_sensor_history(gardenID):
    sensor_info = measure.query.filter_by(gardenID=gardenID).all()
    response = [data.as_dict() for data in sensor_info]
    return jsonify(response)


# Load device history information
@main.route("/user/device_history/<string:gardenID>/<string:name>")
def get_device_history(gardenID, name):
    response = []
    if name == "pump":
        pump_info = pump.query.filter_by(gardenID=gardenID).all()
        for data in pump_info:
            cur_data = data.as_dict()
            response.append(cur_data)
    else:
        light_info = light.query.filter_by(gardenID=gardenID).all()
        for data in light_info:
            cur_data = data.as_dict()
            response.append(cur_data)

    return jsonify(response)


# View or Change information of user
@main.route("/user/account_information/<string:ID>", methods=["GET", "POST"])
def get_account_information(ID):
    user_account = user.query.filter_by(ID=ID).first()
    if request.method == "GET":
        return jsonify(user_account.as_dict())
    elif request.method == "POST":
        change_data = request.get_json()
        user_account.ID = change_data["ID"]
        user_account.name = change_data["name"]
        user_account.username = change_data["username"]
        user_account.password = change_data["password"]
        user_account.email = change_data["email"]
        user_account.phone = change_data["phone"]
        user_account.image = change_data["image"]
        db.session.add(user_account)
        db.session.commit()
        return { "success": "ok" }


@main.route("/something")
def get_fifty_data():
    client.publish("bbc-test-json", "{\"temp\": 25, \"humid\": 55, \"light\": 220}")
    return {"success": "ok"}