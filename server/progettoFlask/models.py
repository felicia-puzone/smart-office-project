from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import datetime
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import generate_password_hash, check_password_hash
import geolog
from utilities import formatName

serializer_secret = "my_secret_key"
serializer = URLSafeTimedSerializer(serializer_secret)
db = SQLAlchemy()
class professions(db.Model):
    id_profession=db.Column('ID_PROFESSION', db.Integer,primary_key=True,autoincrement=True)
    name= db.Column(db.String(20),unique=True)
    category= db.Column(db.String(20))

    def __init__(self,name,category):
        self.category = category
        self.name = name
    def serialize(self):
        return {"id_profession": self.id_profession,
                "name":self.name,
                "category": self.category}
    def __str__(self):
        return self.name
class User(db.Model,UserMixin):
    id = db.Column('ID_USER', db.Integer, primary_key = True)
    username=db.Column(db.String(100),unique= True)
    password = db.Column(db.String(150))
    profession = db.Column(db.String,nullable=False)
    sex = db.Column(db.Integer)
    dateOfBirth=db.Column(db.DateTime(timezone=True), nullable=False,  default=datetime.datetime.utcnow)
    admin=db.Column(db.Boolean)
    super_user=db.Column(db.Boolean)
    def __init__(self,username,password,profession,sex,dateOfBirth):
        self.sex = sex
        self.profession = profession
        self.password = generate_password_hash(password)
        self.username = username
        self.dateOfBirth = dateOfBirth
        self.admin=False
        self.super_user=False
    def get_username(self):
        return self.username
    def verify_password(self,pwd):
        return check_password_hash(self.password,pwd)
    def update_password(self,old_pwd,pwd):
        if self.verify_password(old_pwd):
            self.password = generate_password_hash(pwd)
    def get_id(self):
        return self.id
    def get_auth_token(self, user, password):
        data = [str(self.username), self.password]
        return serializer.dumps(data, salt=serializer_secret)
    def is_admin(self):
        return self.admin
    def is_super(self):
        return self.super_user
    def new_password(self,password,new_password,new_password_confirm):
        if len(password) < 8:
            if self.verify_password(password):
                if len(new_password) < 8 and len(new_password_confirm) < 8 and new_password_confirm==new_password:
                    self.password = generate_password_hash(new_password)
                    return True
        return False
    def set_sex(self,sex):
        self.sex=sex
    def set_profession(self,profession):
        self.profession=profession
    def set_birthday(self,birthday):
        self.dateOfBirth=birthday






class sessions(db.Model):
    id = db.Column('ID_SESSION', db.Integer, primary_key = True)
    timestamp_begin = db.Column('timestamp_begin',db.DateTime(timezone=True), nullable=False, default=datetime.datetime.utcnow)
    timestamp_end = db.Column('timestamp_end',db.DateTime(timezone=True), nullable=True, default=datetime.datetime.utcnow)
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
    description = db.Column(db.String(100))
    available = db.Column(db.Boolean)
    dashboard = db.db.Column(db.String(100))
    def __init__(self, id_building):
        self.id_building = id_building
        building = db.session.query(buildings).filter_by(id_building=id_building).first()
        self.description = "Room of building id:"+str(building.id_building)+ " stationed at "+building.city + " " +building.address
        self.available = True
        self.dashboard = ""
    def set_building(self,building):
        self.id_building=building
    def set_availability(self,availability):
        self.available = availability
#TODO testing
class buildings(db.Model):
    id_building = db.Column('ID_BUILDING', db.Integer, primary_key=True)
    city = db.Column(db.String(100))
    address = db.Column(db.String(100))
    lat = db.Column(db.String(100))
    lon = db.Column(db.String(100))
    available = db.Column(db.Boolean)
    dashboard = db.Column(db.String(100))
    __table_args__ = (
        db.UniqueConstraint(lat, lon,address,city),
    )
    def __init__(self,city,route,number,state):
        street=""
        if route:
            if number:
                street=formatName(route+" "+number)
            else:
                street=formatName(route)
        marker = geolog.geoMarker(formatName(city),street,state)
        street +=" ("+state+")"
        self.lon = marker['lon']
        self.lat = marker['lat']
        self.address=street
        self.city=formatName(city)
        self.available = True
    def set_availability(self,availability):
        self.available = availability

    def serialize(self):
        return {"id_building": self.id_building,
                "city": self.city,
                "lat":self.lat,
                "lon":self.lon,"address":self.address}
#TODO testing
class zones(db.Model):
    id_zone = db.Column('ID_ZONE', db.Integer, primary_key=True,autoincrement=True)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    lat = db.Column(db.String(100))
    lon = db.Column(db.String(100))
    dashboard = db.Column(db.String(100))
    __table_args__ = (
        db.UniqueConstraint(city, state),
        db.UniqueConstraint(lat, lon),
    )
    def __init__(self,city,state):
        marker = geolog.geoMarker(formatName(city), "", state)
        self.city = formatName(city)
        self.state=formatName(state)
        self.lon=marker['lon']
        self.lat = marker['lat']
        self.dashboard=""
    def serialize(self):
        return {"city": self.city,"lat": self.lat,"lon": self.lon}
    def set_lon(self,lon):
        self.lon = lon
    def set_lat(self,lat):
        self.lat = lat
#class buildingInZone(db.Model):
#    id_building=db.Column('ID_BUILDING', db.Integer, primary_key=True)
 #   id_zone=db.Column('ID_ZONE', db.Integer, primary_key=True)
  #  def __init__(self,id_building,id_zone):
   #     self.id_zone=id_zone
   #     self.id_building=id_building

class digitalTwinFeed(db.Model):
    id_room=db.Column('ID_ROOM', db.Integer, primary_key = True)
    light_sensor=db.Column(db.Integer)
    led_actuator=db.Column(db.String(20))
    temperature_actuator=db.Column(db.Integer)
    led_brightness=db.Column(db.Integer)
    #door=db.Column(db.Boolean)
    #pending
    def __init__(self,id_room,light_sensor=0,led_actuator=0,temperature_actuator=0,led_brightness=0):
        self.led_brightness = led_brightness
        self.temperature_actuator = temperature_actuator
        self.led_actuator = led_actuator
        self.light_sensor = light_sensor
        self.id_room = id_room
     #   self.door="CLOSED"
    #def close_door(self):
     #   self.door = "CLOSED"
    #def open_door(self):
     #   self.door ="OPEN"
    def serialize(self):
        return {"id_room": self.id_room,
                "temperature_sensor":self.temperature_sensor,
                "light_sensor":self.light_sensor,
                "room_color" : self.led_actuator,
                "room_temperature" : self.temperature_actuator,
                "room_brightness" : self.led_brightness,
                "healthy" : self.healthy,
                "noise_sensor": self.noise_sensor}
    def serializedActuators(self):
        return {"room_color": self.led_actuator,
                "room_temperature": int(self.temperature_actuator),
                "room_brightness": self.led_brightness}
    def set_to_sleep_mode(self):
        self.temperature_actuator = 20
        self.led_brightness = "LOW"
        self.led_actuator = "NONE"
#DONE Testing
class sensorFeeds(db.Model):
    id_room = db.Column('ID_ROOM', db.Integer,primary_key=True)
    type_of_sensor= db.Column(db.String(20),primary_key=True)
    value= db.Column(db.String(20),primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.datetime.utcnow,primary_key=True)
    def __init__(self, id_room, type_of_sensor,value,timestamp):
        self.id_room = id_room
        self.type_of_sensor = type_of_sensor
        self.value = value
        self.timestamp = timestamp
    def serialize(self):
        return {"id_room": self.id_room,
                "type_of_sensor":self.type_of_sensor,
                "value":self.value,
                "timestamp":self.timestamp
                }
class actuatorFeeds(db.Model):
   # id = db.Column('ID', db.Integer, primary_key=True)
    id_session=db.Column('ID_SESSION', db.Integer,primary_key=True)
    type_of_action= db.Column(db.String(20),primary_key=True)
    value= db.Column(db.String(20),primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.datetime.utcnow,primary_key=True)
    def __init__(self, id_session,type_of_action,value,timestamp):
        self.timestamp = timestamp
        self.value = value
        self.type_of_action = type_of_action
        self.id_session = id_session
    def serialize(self):
        return {#"id_room": self.id_room,
                "type_of_action":self.type_of_action,
                "value":self.value,
                "timestamp":self.timestamp
                }


class zoneToBuildingAssociation(db.Model):
    id_zone = db.Column('id_zone', db.Integer, primary_key=True)
    id_building = db.Column('ID_BUILDING', db.Integer,primary_key=True)
    def __init__(self, id_zone,id_building):
        self.id_building = id_building
        self.id_zone = id_zone

class weatherReport(db.Model):
    id_zone=db.Column('ID_ZONE', db.Integer,primary_key=True)
    temperature= db.Column(db.String(20),primary_key=True)
    humidity= db.Column(db.String(20),primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.datetime.utcnow,primary_key=True)
    def __init__(self, id_zone,temperature,humidity,timestamp):
        self.timestamp = timestamp
        self.temperature = temperature
        self.humidity = humidity
        self.id_zone = id_zone
    def serialize(self):
        return {"id_zone": self.id_id_zone,
                "humidity":self.humidity,
                "temperature":self.temperature,
                "timestamp":self.timestamp
                }

class dailyconsumptionReport(db.Model):
    id_building = db.Column('ID_BUILDING', db.Integer, primary_key=True)
    temperature = db.Column(db.String(20), primary_key=True)
    light = db.Column(db.String(20), primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.datetime.utcnow, primary_key=True)

    def __init__(self, id_building, temperature, light, timestamp):
        self.timestamp = timestamp
        self.temperature = temperature
        self.light = light
        self.id_building = id_building

    def serialize(self):
        return {"id_room": self.id_building,
                "light": self.light,
                "temperature": self.temperature,
                "timestamp": self.timestamp
                }
class session_consumption_report(db.Model):
    id_session = db.Column('ID_BUILDING', db.Integer, primary_key=True)
    temperature = db.Column(db.String(20), primary_key=True)
    light = db.Column(db.String(20), primary_key=True)
    timestamp = db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.datetime.utcnow, primary_key=True)

    def __init__(self, id_building, temperature, light, timestamp):
        self.timestamp = timestamp
        self.temperature = temperature
        self.light = light
        self.id_building = id_building

    def serialize(self):
        return {"id_room": self.id_building,
                "light": self.light,
                "temperature": self.temperature,
                "timestamp": self.timestamp
                }
#class monthlyConsumption()
#class actuatorReport(db.Model):





