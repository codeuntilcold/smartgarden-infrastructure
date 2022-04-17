from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

# class User(db.Model, UserMixin):
#     __tablename__ = 'users'
#     id = db.Column(db.Integer, primary_key=True)
#     active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

#     # User authentication information. The collation='NOCASE' is required
#     # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
#     email = db.Column(db.String(255), nullable=False, unique=True)
#     username = db.Column(db.String(50), nullable=False, unique=True)
#     password = db.Column(db.String(255), nullable=False)

#     # User information
#     first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
#     last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')


# ADMIN
# class admin(db.Model):
#     __tablename__ = 'admin'

#     ID = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(128), nullable=False)
#     username = db.Column(db.String(128), unique=True, nullable=False)
#     password = db.Column(db.String(128), nullable=False)
#     email = db.Column(db.String(128), unique=True, nullable=False)

#     def __init__(self, data):
#         self.ID = data.get('ID')
#         self.name = data.get('name')
#         self.username = data.get('username')
#         self.password = data.get('password')
#         self.email = data.get('email')


# USER
class user(db.Model, UserMixin):
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
