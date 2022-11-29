from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
db = SQLAlchemy()
class accounts(db.Model):
    id = db.Column('ID_USER', db.Integer, primary_key = True)
    username=db.Column(db.String(100),unique= True)
    password = db.Column(db.String(20))
    profession = db.Column(db.Integer,nullable=False)
    sex = db.Column(db.Integer)
    dateOfBirth=db.Column(db.DateTime(timezone=True), nullable=False,  default=datetime.utcnow)
    def __init__(self,username,password,profession,sex,dateOfBirth):
        self.sex = sex
        self.profession = profession
        self.password = password
        self.username = username
        self.dateOfBirth = dateOfBirth
class sessions(db.Model):
    id = db.Column('ID_SESSION', db.Integer, primary_key = True)
    timestamp_begin = db.Column('timestamp_begin',db.DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    timestamp_end = db.Column('timestamp_end',db.DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    def __init__(self,timestamp_begin):
        self.timestamp_begin = timestamp_begin

class sessionStates(db.Model):
    id_session = db.Column('ID_SESSION', db.Integer, primary_key = True)
    id_user = db.Column('ID_USER', db.Integer)
    id_room = db.Column('ID_ROOM', db.Integer)
    active = db.Column(db.Boolean)
    def __init__(self, id_user,id_room):
        self.active = True
        self.id_room = id_room
        self.id_user = id_user
class rooms(db.Model):
    id_room = db.Column('ID_ROOM', db.Integer, primary_key=True)
    id_building = db.Column('ID_BUILDING', db.Integer)

    def __init__(self, id_building):
        self.id_building = id_building
class buildings(db.Model):
    id_building = db.Column('ID_BUILDING', db.Integer, primary_key=True)
    city = db.Column(db.String(100),unique= True)
    def __init__(self,city):
        self.city = city
    def serialize(self):
        return {"id_building": self.id_building,
                "city": self.city}
class histories(db.Model):
    id = db.Column('ID', db.Integer, primary_key=True)
    id_session=db.Column('ID_SESSION', db.Integer)
    type_of_action= db.Column(db.String(20))
    value= db.Column(db.String(20))
    timestamp = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.utcnow)
    def __init__(self, id_session,type_of_action,value,timestamp):
        self.timestamp = timestamp
        self.value = value
        self.type_of_action = type_of_action
        self.id_session = id_session
class professions(db.Model):
    id_profession=db.Column('ID_PROFESSION', db.Integer, primary_key=True)
    name= db.Column(db.String(20))
    category= db.Column(db.String(20))

    def __init__(self,name,category):
        self.category = category
        self.name = name
    def serialize(self):
        return {"id_profession": self.id_building,
                "name":self.name,
                "category": self.category}
class digitalTwinFeed(db.Model):
    id_room=db.Column('ID_ROOM', db.Integer, primary_key = True)
    temperature_sensor=db.Column(db.Integer)
    humidity_sensor=db.Column(db.Integer)
    noise_sensor=db.Column(db.Integer)
    light_sensor=db.Column(db.Integer)
    led_actuator=db.Column(db.Integer)
    temperature_actuator=db.Column(db.Integer)
    led_brightness=db.Column(db.Integer)
    healthy= db.Column(db.Boolean)
    def __init__(self,id_room,temperature_sensor,humidity_sensor,noise_sensor,light_sensor,led_actuator,temperature_actuator,led_brightness,healthy):
        self.healthy = healthy
        self.led_brightness = led_brightness
        self.temperature_actuator = temperature_actuator
        self.led_actuator = led_actuator
        self.light_sensor = light_sensor
        self.noise_sensor = noise_sensor
        self.temperature_sensor = temperature_sensor
        self.id_room = id_room
        self.humidity_sensor=humidity_sensor
    def serialize(self):
        return {"id_room": self.id_room,
                "temperature_sensor":self.temperature_sensor,
                "light_sensor":self.light_sensor,
                "led_actuator" : self.led_actuator,
                "temperature_actuator" : self.temperature_actuator,
                "led_brightness" : self.led_brightness,
                "healthy" : self.healthy,
                "noise_sensor": self.noise_sensor}
    def serializedActuators(self):
        return {"led_actuator": self.led_actuator,
                "temperature_actuator": self.temperature_actuator,
                "led_brightness": self.led_brightness}
