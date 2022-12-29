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


def createAndPopulateDb():
       db.create_all()
       db.session.add(accounts(username="BArfaoui",password="18121996",profession=8,sex=1,dateOfBirth=datetime.utcnow().date()))
       db.session.add(accounts(username="PFelica", password="99669966", profession=8, sex=2,
                               dateOfBirth=datetime.utcnow().date()))
       db.session.add(accounts(username="Vincenzo", password="66996699", profession=8, sex=1,
                               dateOfBirth=datetime.utcnow().date()))
       db.session.add(accounts(username="HLoredana", password="EmiliaBestWaifu", profession=10,  sex=2,
                               dateOfBirth=datetime.utcnow().date()))
       db.session.add(accounts(username="IValeria",  password="DarthVal", profession=12,sex=2,
                               dateOfBirth=datetime.utcnow().date()))
       db.session.add(accounts(username="Nicolò", password="11223344", profession=1, sex=3,
                               dateOfBirth=datetime.strptime("2000-12-1","%Y-%m-%d")))
       db.session.add(buildings(city="Modena"))
       db.session.add(buildings(city="Roma"))
       db.session.add(buildings(city="Napoli"))
       db.session.add(buildings(city="Bologna"))
       db.session.add(buildings(city="Milano"))
       db.session.add(buildings(city="Genova"))
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