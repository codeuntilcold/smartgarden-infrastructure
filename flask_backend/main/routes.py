from flask import Blueprint, render_template, jsonify, abort
import json
from datetime import datetime
import pytz
from flask_backend.config import ConfigClass
from flask_backend.main import *
from flask_backend.models import *

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
    response_data = json.loads(aio.data(ConfigClass.AIO_FEED_IDS[0])[0].value)
    response_data["time"] = datetime.strptime(aio.data(ConfigClass.AIO_FEED_IDS[0])[0].created_at, '%Y-%m-%dT%H:%M:%SZ').astimezone(pytz.timezone("UTC"))
    return jsonify(response_data)


# Get the current state of device
@main.route('/<string:feed_key>/current')
def get_current_device_data(feed_key):
    response_data = {}

    response_data["value"] = aio.data(feed_key)[0].value
    response_data["time"] = datetime.strptime(aio.data(feed_key)[0].created_at, '%Y-%m-%dT%H:%M:%SZ')
    return jsonify(response_data)


# Control device <bbc-led: control light; bbc-pump: control pump> (status: 0 - OFF, 1 - ON)
@main.route('/control/<string:feed_key>/<int:status>', methods=["POST"])
def control_device(feed_key, status):
    try:
        client.publish(feed_key, status)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    finally:
        return abort(404)


# Load all garden
@main.route("/user/all_garden/<string:userID>")
def get_all_garden(userID):
    all_garden = garden.query.filter_by(userID=userID).all()
    response = []
    for gd in all_garden:
        cur_garden = {}
        cur_garden["gardenID"] = gd.gardenID
        cur_garden["name"] = gd.name
        cur_garden["userID"] = gd.userID
        cur_garden["location"] = gd.location
        cur_garden["starttime"] = gd.starttime
        cur_garden["description"] = gd.description
        cur_garden["area"] = gd.area
        cur_garden["image"] = gd.image
        response.append(cur_garden)
    return jsonify(response)


# Load, change garden information
@main.route("/user/garden_info/<string:gardenID>", methods=["GET", "POST"])
def get_garden_info(gardenID):
    garden_info = garden.query.filter_by(gardenID=gardenID).first()
    if request.method == "GET":
        cur_garden = {}
        cur_garden["gardenID"] = garden_info.gardenID
        cur_garden["name"] = garden_info.name
        cur_garden["userID"] = garden_info.userID
        cur_garden["location"] = garden_info.location
        cur_garden["starttime"] = garden_info.starttime
        cur_garden["description"] = garden_info.description
        cur_garden["area"] = garden_info.area
        cur_garden["image"] = garden_info.image

        return jsonify(cur_garden)
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
    response = []
    for data in sensor_info:
        cur_data = {}
        cur_data["ID"] = data.ID
        cur_data["gardenID"] = data.gardenID
        cur_data["type"] = data.type
        cur_data["value"] = data.value
        cur_data["time"] = data.time
        response.append(cur_data)

    return jsonify(response)


# Load device history information
@main.route("/user/device_history/<string:gardenID>/<string:name>")
def get_device_history(gardenID, name):
    response = []
    if name == "pump":
        pump_info = pump.query.filter_by(gardenID=gardenID).all()
        for data in pump_info:
            cur_data = {}
            cur_data["ID"] = data.ID
            cur_data["gardenID"] = data.gardenID
            cur_data["time"] = data.time
            cur_data["status"] = data.status
            response.append(cur_data)
    else:
        light_info = light.query.filter_by(gardenID=gardenID).all()
        for data in light_info:
            cur_data = {}
            cur_data["ID"] = data.ID
            cur_data["gardenID"] = data.gardenID
            cur_data["time"] = data.time
            cur_data["status"] = data.status
            response.append(cur_data)

    return jsonify(response)


# View or Change information of user
@main.route("/user/account_information/<string:ID>", methods=["GET", "POST"])
def get_account_information(ID):
    user_account = user.query.filter_by(ID=ID).first()
    if request.method == "GET":
        cur_user = {}
        cur_user["ID"] = user_account.ID
        cur_user["name"] = user_account.name
        cur_user["username"] = user_account.username
        cur_user["password"] = user_account.password
        cur_user["email"] = user_account.email
        cur_user["phone"] = user_account.phone
        cur_user["image"] = user_account.image
        return jsonify(cur_user)
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

