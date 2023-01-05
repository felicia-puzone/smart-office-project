from flask_admin.contrib import sqla
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
import datetime

from itsdangerous import URLSafeTimedSerializer
from werkzeug.routing import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash

import geolog
from geolog import getMarker,getMarkerByType
serializer_secret = "my_secret_key"
serializer = URLSafeTimedSerializer(serializer_secret)
db = SQLAlchemy()

class User(db.Model,UserMixin):
    id = db.Column('ID_USER', db.Integer, primary_key = True)
    username=db.Column(db.String(100),unique= True)
    password = db.Column(db.String(150))
    profession = db.Column(db.Integer,nullable=False)
    sex = db.Column(db.Integer)
    dateOfBirth=db.Column(db.DateTime(timezone=True), nullable=False,  default=datetime.datetime.utcnow)
    def __init__(self,username,password,profession,sex,dateOfBirth):
        self.sex = sex
        self.profession = profession
        self.password = generate_password_hash(password)
        self.username = username
        self.dateOfBirth = dateOfBirth
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

    def __init__(self, id_building):
        self.id_building = id_building

    def set_building(self,building):
        self.id_building=building

#TODO testing
class buildings(db.Model):
    id_building = db.Column('ID_BUILDING', db.Integer, primary_key=True)
    id_zone = db.Column(db.Integer)
    route=db.Column(db.String(100))
    number=db.Column(db.String(100))
    lat = db.Column(db.String(100))
    lon = db.Column(db.String(100))
    __table_args__ = (
        db.UniqueConstraint(route, lat),
        db.UniqueConstraint(route, lon),
    )
    def __init__(self,city,route,number,state):
        #self.city = city
        if route == '' and number=='':
            marker = getMarker(city + ','+ state)
            self.lon = marker['lon']
            self.lat = marker['lat']
        else:
            marker=getMarker(city+','+route+'+'+number+','+state)
            self.lon = marker['lon']
            self.lat = marker['lat']
        self.id_zone=tryToAssignZone(city,state)
        self.route=route
        self.number=number

    #def __init__(self,city,lat,log):
        #self.city = city
    def serialize(self):
        return {"id_building": self.id_building,
                "city": db.session.query(zones).filter_by(id_zone=self.id_zone).first().city,
                "lat":self.lat,
                "lon":self.lon,"route":self.route,"number":self.number}
#TODO testing
class zones(db.Model):
    id_zone= db.Column(db.Integer, primary_key=True,autoincrement=True,nullable=True)
    city = db.Column(db.String(100),unique= True)
    state = db.Column(db.String(100))
    lat = db.Column(db.String(100))
    lon = db.Column(db.String(100))
    __table_args__ = (
        db.UniqueConstraint(city, state),
    )
    def __init__(self,city,state):
        self.city = city
        self.state=state
        marker=getMarkerByType(city+','+state,"administrative")
        self.lon=marker['lon']
        self.lat = marker['lat']
    def serialize(self):
        return {"id_zone": self.id_zone,
                "city": self.city,"lat": self.lat,"lon": self.lon}
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
class professions(db.Model):
    id_profession=db.Column('ID_PROFESSION', db.Integer, primary_key=True)
    name= db.Column(db.String(20))
    category= db.Column(db.String(20))

    def __init__(self,name,category):
        self.category = category
        self.name = name
    def serialize(self):
        return {"id_profession": self.id_profession,
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
    #door=db.Column(db.Boolean)
    #pending
    def __init__(self,id_room,temperature_sensor=0,humidity_sensor=0,noise_sensor=0,light_sensor=0,led_actuator=0,temperature_actuator=0,led_brightness=0,healthy=False):
        self.healthy = healthy
        self.led_brightness = led_brightness
        self.temperature_actuator = temperature_actuator
        self.led_actuator = led_actuator
        self.light_sensor = light_sensor
        self.noise_sensor = noise_sensor
        self.temperature_sensor = temperature_sensor
        self.id_room = id_room
        self.humidity_sensor=humidity_sensor
     #   self.door="CLOSED"
    #def close_door(self):
     #   self.door = "CLOSED"
    #def open_door(self):
     #   self.door ="OPEN"
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


#TODO testing
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

#TODO testing
class admins(db.Model):
    id = db.Column('ID', db.Integer, primary_key=True)
    def __init__(self, id):
        self.id = id


#TODO testing
#TODO ogni stanza avrà un digitalTwin
def createNewBuilding(city,route,number,state,numberofrooms):
    #Modena, Giuseppe Verdi 11/a, State
    address = str(city).title() + ", " + str(route).title() + " " + str(number).title() + ", "+ str(state).title()
    if geolog.isAddressValid(address):
        #indirizzo valido
        zone=db.session.query(zones).filter_by(state=state,city=city).first()
        if zone:
            #esiste già
            building = buildings(city,route,number,state,zone.id_zone)
            db.session.add(building)
            db.session.refresh()
            addrooms(numberofrooms, building.id_building)
        else:
            building = buildings(city, route, number, state)
            db.session.add(building)
            db.session.refresh()
            addrooms(numberofrooms,building.id_building)
    else:
        return False
    #in questo metodo prendiamo in input l'indirizzo e
    #mettiamo i dati in un formato tale da non poter creare dati duplicati
    #Città Via Numero (Prima lettera maiuscola, il resto minuscolo)
    return True


#TODO testing
def addrooms(numberofrooms,id_building):
    for _ in numberofrooms:
        room = rooms(id_building)
        db.session.add(room)
        db.session.commit()
        db.session.refresh()
        if room:
            db.session.add(digitalTwinFeed(room.id_room))
            db.session.refresh()
    return 0

#TODO testing
def removerooms(id_building,number):
    roomsFetched = db.session.query(rooms).filter_by(id_building=id_building)
    for _ in number:
        digitalTwinToRemove = db.session.query(digitalTwinFeed).filter_by(id_room=roomsFetched.last().id_room)
        db.session.delete(roomsFetched.last())
        db.session.delete(digitalTwinToRemove)
        db.session.refresh()
    return 0
def updateBuilding():
    #città #indirizzo #zona
    #numero di stanze 2 casi più stanze o meno stanze
    return 0

#TODO testing
def deleteBuilding(id_building):
    building = db.session.query(buildings).filter_by(id_building=id_building).first()
    roomsToDelete = db.session.query(rooms).filter_by(id_building=id_building)
    db.session.delete(building)
    for room in roomsToDelete:
        digitalTwinToDelete = db.session.query(digitalTwinFeed).filter_by(id_room=room.id_room).first()
        db.session.delete(room)
        db.session.delete(digitalTwinToDelete)
        db.session.refresh()
    if building is None:
        if roomsToDelete is None:
            return True
    return False
def createAndPopulateDb():
       db.create_all()
       #db.session.add(User(username="BArfaoui",password="18121996",profession=8,sex=1,dateOfBirth=datetime.utcnow().date()))
       #db.session.add(User(username="PFelica", password="99669966", profession=8, sex=2,
        #                       dateOfBirth=datetime.utcnow().date()))
       #db.session.add(User(username="Vincenzo", password="66996699", profession=8, sex=1,
         #                      dateOfBirth=datetime.utcnow().date()))
       #db.session.add(User(username="HLoredana", password="EmiliaBestWaifu", profession=10,  sex=2,
        #                       dateOfBirth=datetime.utcnow().date()))
       #db.session.add(User(username="IValeria",  password="DarthVal", profession=12,sex=2,
        #                       dateOfBirth=datetime.utcnow().date()))
       #db.session.add(User(username="Nicolò", password="11223344", profession=1, sex=3,
        #                       dateOfBirth=datetime.strptime("2000-12-1","%Y-%m-%d")))
       db.session.add(buildings(city="Modena",route='',number='',state='Italia'))
       db.session.add(buildings(city="Roma",route='',number='',state='Italia'))
       db.session.add(buildings(city="Napoli",route='',number='',state='Italia'))
       db.session.add(buildings(city="Bologna",route='',number='',state='Italia'))
       db.session.add(buildings(city="Milano",route='',number='',state='Italia'))
       db.session.add(buildings(city="Genova",route='',number='',state='Italia'))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=5))
       db.session.add(rooms(id_building=5))
       db.session.add(rooms(id_building=5))
       db.session.add(digitalTwinFeed(1,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(2, 0,0, 0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(3, 0,0, 0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(4, 0,0, 0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(5,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(6, 0, 0,0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(7, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(8, 0, 0, 0,0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(9,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(10, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(11, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(12, 0, 0, 0, 0, 0,0, 0, True))
       db.session.add(digitalTwinFeed(13,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(14, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(15, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(16, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(17,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(18, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(19, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(20, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(21,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(22, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(23, 0, 0, 0, 0, 0,0, 0, True))
       db.session.add(digitalTwinFeed(24, 0, 0, 0, 0, 0,0, 0, True))
       db.session.add(professions(name="Streamer", category=0))
       db.session.add(professions(name="Blogger", category=0))
       db.session.add(professions(name="Televendite", category=0))
       db.session.add(professions(name="Professore/Istruttore",category=1))
       db.session.add(professions(name="Seminarista",category=1))
       db.session.add(professions(name="Snake oil seller", category=1))
       db.session.add(professions(name="Assistenza telefonica", category=2))
       db.session.add(professions(name="Programmatore", category=2))
       db.session.add(professions(name="Contabile", category=2))
       db.session.add(professions(name="Manager", category=2))
       db.session.add(professions(name="Elettricista", category=3))
       db.session.add(professions(name="Sistemista", category=3))
       db.session.add(professions(name="Colf/Badante", category=4))
       db.session.add(professions(name="Babysitter", category=4))
       db.session.add(professions(name="Operatore CAF/CISL", category=5))
       db.session.add(professions(name="Operatore NASPI", category=5))
       db.session.commit()




#tested
def getFreeBuildings():
    activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True)
    freeRoomsBuildings = db.session.query(rooms.id_building).filter(rooms.id_room.notin_(activeSessionStates))
    freeBuildings=db.session.query(buildings).filter(buildings.id_building.in_(freeRoomsBuildings))

    return freeBuildings

def tryToAssignZone(city,state):
    zone = db.session.query(zones).filter_by(city=city,state=state).first()
    #se la zona non esiste, la creiamo
    if zone is None:
        zone = zones(city,state)
        db.session.add(zone)
        db.session.commit()
        if zone.id_zone is None:
            db.session.refresh(zone)
    return zone.id_zone

#testato
def getBuildings():
    return buildings.query.all()

#testato
def fetchJobs():
    return professions.query.all()

#Formato Indirizzo Città,Via/Viale+Via+Numero,Stato



