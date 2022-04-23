from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

# Initialize Flask-SQLAlchemy
db = SQLAlchemy()

class Deserialize:
    def as_dict(self):
       return {c.name: getattr(self, c.name) for c in self.__table__.columns}


# USER
class user(db.Model, UserMixin, Deserialize):
    __tablename__ = 'user'

    ID = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(128), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    phone = db.Column(db.String(10), unique=True, nullable=False)
    image = db.Column(db.String(128))
    role = db.relationship('Role', secondary='user_role')

    def __init__(self, data):
        self.ID = data.get('ID')
        self.name = data.get('name')
        self.username = data.get('username')
        self.password = data.get('password')
        self.email = data.get('email')
        self.phone = data.get('phone')
        self.image = data.get('image')

    def get_id(self):
        return self.ID


# Define the Role data-model
class Role(db.Model, Deserialize):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model, Deserialize):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('user.ID', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('role.id', ondelete='CASCADE'))

# GARDEN
class garden(db.Model, Deserialize):
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
class measure(db.Model, Deserialize):
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
class pump(db.Model, Deserialize):
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
class light(db.Model, Deserialize):
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
class threshold(db.Model, Deserialize):
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
