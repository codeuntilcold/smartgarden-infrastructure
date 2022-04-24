import datetime
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, send
from flask_user import UserManager, PasswordManager
from flask_user.db_manager import DBManager
from flask_jwt_extended import (
    create_access_token,
    JWTManager
)

from .main.routes import main
from .admin.routes import admin
from .config import *
from .models import *

app = Flask(__name__)
app.config.from_object(ConfigClass)

app.register_blueprint(main, url_prefix='/')
app.register_blueprint(admin, url_prefix='/admin')

# SOCKET INIT
socketio = SocketIO(app, cors_allowed_origins='*')
jwt = JWTManager(app)

@socketio.on('connect')
def initialize_socket():
    send("Successfully connected")


with app.app_context():
    db.init_app(app)
    db.create_all()
    # Setup Flask-user and specify the user data-model
    user_manager = UserManager(app, db, user)

    default_user = user.query.filter(user.email == 'member@example.com').first()
    if not default_user:
        data = {
            "name": "Nam",
            "username": 'user1',
            "email": 'member@example.com',
            "password": user_manager.hash_password('Password1'),
            "phone": "1",
            "image":""
        }
        new_user = user(data)
        db.session.add(new_user)
        db.session.commit()

    default_admin = user.query.filter(user.email == 'admin@example.com').first()
    if not default_admin:
        data = {
            "name": "Nam",
            "username": 'admin1',
            "email": 'admin@example.com',
            "password": user_manager.hash_password('Password1'),
            "phone": "2",
            "image":""
        }
        new_user = user(data)
        new_user.is_admin = True
        db.session.add(new_user)
        db.session.commit()


db_manager = DBManager(app, db, user)
pass_manager = PasswordManager(app)

@app.route("/login", methods=["POST"])
def user_login():
    username = request.get_json()['username']
    password = request.get_json()['password']
    expire = datetime.timedelta(days=30) if 'remember' in request.form else None
    user = db_manager.find_user_by_username(username)
    if user:
        if pass_manager.verify_password(password, user.password):
            access_token = create_access_token(
                identity={ 
                    "username": user.username,
                    "is_admin": user.is_admin
                }, 
                expires_delta=expire)
            return jsonify(success=True, access_token=access_token)
    return jsonify(access_token=None, success=False)
