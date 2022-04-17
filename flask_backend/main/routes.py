from flask import Blueprint, render_template, jsonify, abort
import json
from datetime import datetime
import pytz
from flask_backend.config import ConfigClass
from flask_backend.main import *

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


# Load garden information
@main.route("/user/garden_info/<string:gardenID>")
def get_garden_info(gardenID):
    garden_info = garden.query.filter_by(gardenID=gardenID).first()
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