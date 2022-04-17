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
    # Setup Flask-User and specify the User data-model
    user_manager = UserManager(app, db, User)

    # Create 'member@example.com' user with no roles
    if not User.query.filter(User.email == 'member@example.com').first():
        user = User(
            username='user1',
            email='member@example.com',
            password=user_manager.hash_password('Password1'),
        )
        db.session.add(user)
        db.session.commit()

    # Create 'admin@example.com' user with 'Admin' and 'Agent' roles
    if not User.query.filter(User.email == 'admin@example.com').first():
        user = User(
            username='admin1',
            email='admin@example.com',
            password=user_manager.hash_password('Password1'),
        )
        user.roles.append(Role(name='Admin'))
        user.roles.append(Role(name='Agent'))
        db.session.add(user)
        db.session.commit()


db_manager = DBManager(app, db, User)
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
            return { "success": "ok" }
    return { "success": "false" }


@app.route("/logout")
@login_required
def user_logout():
    if logout_user():
        return { "success": "ok" }
    return { "success": "false" }


@app.route("/signup", methods=["POST"])
# @roles_required('Admin')
def user_signup():
    username = request.get_json()['username']
    password = request.get_json()['password']
    if db_manager.username_is_available(username):
        new_user = User(username=username, email=username, password=user_manager.hash_password(password))
        db.session.add(new_user)
        db.session.commit()
        return { "success": "ok" }
    return { "success": "false" }
