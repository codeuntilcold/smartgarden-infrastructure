from flask import Blueprint, render_template, jsonify, abort
import json
from datetime import datetime
from pytz import timezone
from flask_backend.config import ConfigClass
from flask_backend.main import *

main = Blueprint('main', __name__)

# # Route to demo realtime connection
# @main.route('/')
# def index():
#     # Depend on client info, we give them the feed_id
#     return render_template('index.html',
#                            hostname='localhost',
#                            port='5000',
#                            sub_to_feed_id=ConfigClass.AIO_FEED_IDS[0])


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
@main.route('/current')
def get_current_sensor_data():
    response_data = json.loads(aio.data(ConfigClass.AIO_FEED_IDS[0])[0].value)
    response_data["time"] = datetime.strptime(aio.data(ConfigClass.AIO_FEED_IDS[0])[0].created_at, '%Y-%m-%dT%H:%M:%SZ').astimezone(timezone("UTC"))
    return jsonify(response_data)


# Control device <bbc-led: control light; bbc-pump: control pump> (status: 0 - OFF, 1 - ON)
@main.route('/control/<string:feed_key>/<int:status>', methods=["POST"])
def control_device(feed_key, status):
    try:
        client.publish(feed_key, status)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    finally:
        return abort(404)


from flask_user import login_required


# Route to demo user
@main.route('/')
def home_page():
    # String-based templates
    return render_template('home.html')


# Route to demo user
@main.route('/members')
@login_required
def member_page():
    # String-based templates
    return render_template('member.html')


