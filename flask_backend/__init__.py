from flask import Flask, request
from flask_socketio import SocketIO, send
from flask_user import UserManager, PasswordManager, roles_required
from flask_user.db_manager import DBManager
from flask_login import login_user, logout_user, login_required

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


@socketio.on('connect')
def initialize_socket():
    send("Successfully connected")


with app.app_context():
    db.init_app(app)
    db.create_all()
    # Setup Flask-user and specify the user data-model
    user_manager = UserManager(app, db, user)

    if not user.query.filter(user.email == 'member@example.com').first():
        data = {
            # "ID": "1",
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

    if not user.query.filter(user.email == 'admin@example.com').first():
        data = {
            # "ID": "2",
            "name": "Nam",
            "username": 'admin1',
            "email": 'admin@example.com',
            "password": user_manager.hash_password('Password1'),
            "phone": "2",
            "image":""
        }
        new_user = user(data)
        user.roles.append(Role(name='Admin'))
        db.session.add(new_user)
        db.session.commit()


db_manager = DBManager(app, db, user)
pass_manager = PasswordManager(app)

@app.route("/login", methods=["POST"])
def user_login():
    username = request.get_json()['username']
    password = request.get_json()['password']
    remember_me = 'remember' in request.form
    user = db_manager.find_user_by_username(username)
    if user:
        if pass_manager.verify_password(password, user.password):
            login_user(user, remember=remember_me)
            return { "success": "true" }
    return { "success": "false" }


@app.route("/logout")
# @login_required
def user_logout():
    if logout_user():
        return { "success": "true" }
    return { "success": "false" }
