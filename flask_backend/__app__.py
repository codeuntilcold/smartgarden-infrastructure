from flask import Flask, render_template, jsonify, abort, request
from flask_socketio import SocketIO, send
from Adafruit_IO import MQTTClient, Client
import sys
import json
from datetime import datetime
import pytz
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

# SOCKET INIT
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_secret'
socketio = SocketIO(app, cors_allowed_origins='*')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres@localhost/garden'
app.debug = True
db = SQLAlchemy(app)

AIO_FEED_IDS = ["bbc-test-json", "bbc-led", "bbc-pump"]
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
    light = [float(json.loads(d.value)['light']) for d in data['test']]

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
    elif feed_key == AIO_FEED_IDS[2]:
        response_data["time"] = [d.created_at for d in aio.data(AIO_FEED_IDS[2])]
        response_data["value"] = [d.value for d in aio.data(AIO_FEED_IDS[2])]

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
@app.route('/sensor/current')
def get_current_sensor_data():
    response_data = json.loads(aio.data(AIO_FEED_IDS[0])[0].value)
    response_data["time"] = datetime.strptime(aio.data(AIO_FEED_IDS[0])[0].created_at, '%Y-%m-%dT%H:%M:%SZ').astimezone(pytz.timezone("UTC"))
    return jsonify(response_data)


# Get the current state of device
@app.route('/<string:feed_key>/current')
def get_current_device_data(feed_key):
    response_data = {}

    response_data["value"] = aio.data(feed_key)[0].value
    response_data["time"] = datetime.strptime(aio.data(feed_key)[0].created_at, '%Y-%m-%dT%H:%M:%SZ')
    return jsonify(response_data)


# Control device <bbc-led: control light; bbc-pump: control pump> (status: 0 - OFF, 1 - ON)
@app.route('/control/<string:feed_key>/<int:status>', methods=["POST"])
def control_device(feed_key, status):
    try:
        client.publish(feed_key, status)
        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    except:
        return abort(404)


# ADMIN
class admin(db.Model):
    __tablename__ = 'admin'

    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)

    def __init__(self, data):
        self.ID = data.get('ID')
        self.name = data.get('name')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')


# USER
class user(db.Model):
    __tablename__ = 'user'

    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    image = db.Column(db.String(128))

    def __init__(self, data):
        self.ID = data.get('ID')
        self.name = data.get('name')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.image = data.get('image')


# GARDEN
class garden(db.Model):
    __tablename__ = 'garden'

    gardenID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    userID = db.Column(db.Integer, db.ForeignKey('user.ID'), nullable=False)
    location = db.Column(db.String(128), nullable=False)
    starttime = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(255))
    area = db.Column(db.Integer)
    image = db.Column(db.String(128))

    def __init__(self, data):
        self.gardenID = data.get('gardenID')
        self.name = data.get('name')
        self.userID = data.get('userID')
        self.location = data.get('location')
        self.starttime = data.get('starttime')
        self.description = data.get('description')
        self.area = data.get('area')
        self.image = data.get('image')


# MEASURE
class measure(db.Model):
    __tablename__ = 'measure'

    ID = db.Column(db.Integer, primary_key=True)
    gardenID = db.Column(db.Integer, db.ForeignKey('garden.gardenID'), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)
    time = db.Column(db.DateTime, nullable=False)

    def __init__(self, data):
        self.ID = data.get('ID')
        self.gardenID = data.get('gardenID')
        self.type = data.get('type')
        self.value = data.get('value')
        self.time = data.get('time')


# PUMP
class pump(db.Model):
    __tablename__ = 'pump'

    ID = db.Column(db.Integer, primary_key=True)
    gardenID = db.Column(db.Integer, db.ForeignKey('garden.gardenID'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __init__(self, data):
        self.ID = data.get('ID')
        self.gardenID = data.get('gardenID')
        self.time = data.get('time')
        self.status = data.get('status')


# LIGHT
class light(db.Model):
    __tablename__ = 'light'

    ID = db.Column(db.Integer, primary_key=True)
    gardenID = db.Column(db.Integer, db.ForeignKey('garden.gardenID'), nullable=False)
    time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.Boolean, nullable=False)

    def __init__(self, data):
        self.ID = data.get('ID')
        self.gardenID = data.get('gardenID')
        self.time = data.get('time')
        self.status = data.get('status')


# THRESHOLD
class threshold(db.Model):
    __tablename__ = 'threshold'
    __table_args__ = (
        db.UniqueConstraint('TOE', 'TOM', 'gardenID', 'upper', 'lower'),
    )

    TOE = db.Column(db.Integer, nullable=False, primary_key=True)
    TOM = db.Column(db.Integer, nullable=False, primary_key=True)
    gardenID = db.Column(db.Integer, db.ForeignKey('garden.gardenID'), nullable=False, primary_key=True)
    upper = db.Column(db.Integer, nullable=False, primary_key=True)
    lower = db.Column(db.Integer, nullable=False, primary_key=True)
    action = db.Column(db.Boolean, nullable=False)
    actiontime = db.Column(db.Integer, nullable=False)
    cooldown = db.Column(db.Integer, nullable=False)

    def __init__(self, data):
        self.TOE = data.get('TOE')
        self.TOM = data.get('TOM')
        self.gardenID = data.get('gardenID')
        self.upper = data.get('upper')
        self.lower = data.get('lower')
        self.action = data.get('action')
        self.actiontime = data.get('actiontime')
        self.cooldown = data.get('cooldown')


@app.route("/admin/all", methods=["GET"])
def getAdmin():
    all = admin.query.all()
    output = []
    for ad in all:
        currAdmin = {}
        currAdmin['ID'] = ad.ID
        currAdmin['name'] = ad.name
        currAdmin['username'] = ad.username
        currAdmin['password'] = ad.password
        currAdmin['email'] = ad.email
        output.append(currAdmin)
    return jsonify(output)


@app.route("/admin", methods=["POST"])
def addAdmin():
    adminData = request.get_json()
    print(adminData)
    newAdmin = admin(adminData)
    db.session.add(newAdmin)
    db.session.commit()
    return jsonify(adminData)


@app.route("/push", methods=["POST"])
def pushDatatoPostgres():
    arr_data = {}
    for feed in AIO_FEED_IDS:
        if feed == "bbc-test-json":
            df = pd.read_csv('C:/Users/Acer/Desktop/HK212/project_AI/data_clear.csv')
            df = df[::-1]
            data = []
            for i in range(len(df)):
                temp = json.loads(df.value[i])["temp"]
                humid = json.loads(df.value[i])["humid"]
                light_s = json.loads(df.value[i])["light"]
                time = df.created_at[i]
                data.append({"type": 1, "value": temp, "time": time})
                data.append({"type": 2, "value": humid, "time": time})
                data.append({"type": 3, "value": light_s, "time": time})

            for i in range(len(data)):
                data[i]["ID"] = i + 1
                data[i]["gardenID"] = 1

            arr_data["sensor"] = data

            for i in range(len(data)):
                new_line = measure(data[i])
                db.session.add(new_line)
                db.session.commit()
        elif feed == "bbc-led" or feed == "bbc-pump":
            temp_data = []
            time = [datetime.strptime(d.created_at, '%Y-%m-%dT%H:%M:%SZ') for d in aio.data(feed)]
            value = [d.value for d in aio.data(feed)]

            # Reverse list from furthest to nearest
            time.reverse()
            value.reverse()

            for i in range(len(time)):
                temp = {}
                temp["ID"] = i+1
                temp["gardenID"] = 1
                temp["time"] = time[i]
                temp["status"] = True if value[i] == "1" else False
                temp_data.append(temp)

            if feed == "bbc-led":
                arr_data["led"] = temp_data
                for i in range(len(temp_data)):
                    new_line = light(temp_data[i])
                    db.session.add(new_line)
                    db.session.commit()
            else:
                arr_data["pump"] = temp_data
                for i in range(len(temp_data)):
                    new_line = pump(temp_data[i])
                    db.session.add(new_line)
                    db.session.commit()
    return jsonify(arr_data)


# Load all users
@app.route("/admin/all_users")
def get_all_users():
    all_users = user.query.all()
    response = []
    for u in all_users:
        cur_user = {}
        cur_user["ID"] = u.ID
        cur_user["name"] = u.name
        cur_user["username"] = u.username
        cur_user["password"] = u.password
        cur_user["email"] = u.email
        cur_user["phone"] = u.phone
        cur_user["image"] = u.image
        response.append(cur_user)
    return jsonify(response)


# Add garden
@app.route("/admin/add_garden", methods=["POST"])
def add_new_garden():
    garden_data = request.get_json()
    new_garden = garden(garden_data)
    db.session.add(new_garden)
    db.session.commit()

    return jsonify(garden_data)


# Add user
@app.route("/admin/add_user", methods=["POST"])
def add_new_user():
    user_data = request.get_json()
    new_user = user(user_data)
    db.session.add(new_user)
    db.session.commit()

    return jsonify(user_data)


# Delete user
@app.route("/admin/delete_user/<string:ID>")
def delete_user(ID):
    cur_user = user.query.filter_by(ID=ID).first()
    db.session.delete(cur_user)
    db.session.commit()

    return "Delete success"


# Load garden information
@app.route("/user/garden_info/<string:gardenID>")
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
@app.route("/user/sensor_history/<string:gardenID>")
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
@app.route("/user/device_history/<string:gardenID>/<string:name>")
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


if __name__ == '__main__':
    # app.run(debug=True)
    db.init_app(app)
    db.create_all()
    socketio.run(app)
