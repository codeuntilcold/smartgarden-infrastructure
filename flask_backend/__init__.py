from flask import Flask
from flask_socketio import SocketIO, send
from flask_user import UserManager

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
