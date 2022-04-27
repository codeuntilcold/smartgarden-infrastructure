import datetime
import json
from flask import Blueprint, jsonify, request
from flask_backend.main import *
from flask_backend.models import *
from flask_backend.config import *
from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity,
)
import pandas as pd


admin = Blueprint('admin', __name__)

@admin.before_request
@jwt_required()
def protect_admin_route():
    cu = get_jwt_identity()
    if cu["is_admin"]:
        return
    else:
        return jsonify(msg="Admins only!"), 403


@admin.route("/all_admins", methods=["GET"])
def getAdmin():
    all = user.query.all()
    output = list(map(lambda u: u.as_dict(), filter(lambda u: u.is_admin, all)))
    return jsonify(output)


@admin.route("/add_admin", methods=["POST"])
def addAdmin():
    adminData = {**request.get_json(), "is_admin": True}
    newAdmin = user(adminData)
    db.session.add(newAdmin)
    db.session.commit()
    return jsonify(adminData)


@admin.route("/push", methods=["POST"])
def pushDatatoPostgres():
    arr_data = {}
    for feed in ConfigClass.AIO_FEED_IDS:
        if feed == "bbc-test-json":
            df = pd.read_csv('../data/data_clean.csv')
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
            time = [datetime.datetime.strptime(d.created_at, '%Y-%m-%dT%H:%M:%SZ') for d in aio.data(feed)]
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
@admin.route("/all_users")
def get_all_users():
    all_users = user.query.all()
    response = list(map(lambda u: u.as_dict(), filter(lambda u: not u.is_admin, all_users)))
    return jsonify(response)


# Add garden
@admin.route("/add_garden", methods=["POST"])
def add_new_garden():
    garden_data = request.get_json()
    new_garden = garden(garden_data)
    db.session.add(new_garden)
    db.session.commit()
    return jsonify(garden_data)


# Add user
@admin.route("/add_user", methods=["POST"])
def add_new_user():
    from flask_backend import db_manager, user_manager
    
    username = request.get_json()['username']
    password = request.get_json()['password']
    if db_manager.find_user_by_username(username):
        return jsonify(success=False)
    new_user = user({**request.get_json(), 
        "is_admin": False,
        "password": user_manager.hash_password(password)})
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.as_dict())


# Delete user
@admin.route("/delete_user/<string:ID>")
def delete_user(ID):
    cur_user = user.query.filter_by(ID=ID).first()
    db.session.delete(cur_user)
    db.session.commit()
    return jsonify(success=True)
