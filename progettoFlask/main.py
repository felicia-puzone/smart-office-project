import datetime
import re
from re import Pattern

import requests as requests
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flask_mqtt import Mqtt
from flask_cors import CORS
import paho.mqtt.client as mqtt
from firebase import firebase
from flask_socketio import emit, SocketIO
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
appname="IOT main"
app = Flask(appname)
app.secret_key = 'secretkey'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MQTT_BROKER_URL'] = 'ilvero.davidepalma.it'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
app.config['MQTT_USERNAME'] ='uni'  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = 'more'#   set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "random string"
mqtt=Mqtt(app)
db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")
fb_app = firebase.FirebaseApplication('https://smartoffice-4eb51-default-rtdb.europe-west1.firebasedatabase.app/', None)
maintance=False
minimumAge=18

@mqtt.on_connect()
def handle_connect(client,userdata,flags,rc):
    print("Ciao! sono il server Flask di Billi!")

@mqtt.on_message()
def handle_message_mqtt(client,userdata,message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
    r = re.compile("smartoffice/building_\d/room_\d/sensors/\S")
    if r.match(data.get('topic')):
        print("ho ricevuto dati da un sensore!")
        identifiers=re.findall('\d',data.get('topic'))
        sensor=re.findall(r'\w+',data.get('topic'))
        print("ho ricevuto dati dall'edificio:"+str(identifiers[0]))
        print("ho ricevuto dati dalla stanza:"+str(identifiers[1]))
        print(sensor[4])
        values=re.findall(r'\d+',data['payload'])
        updateDigitalTwin(identifiers[1],sensor[4],values[0])
    #with app.test_request_context('/'):
     #   socketio.emit('Cambia valore', message.topic,broadcast=True)


@app.route("/") #percorsi url locali
@app.route('/login',methods = ['GET','POST'])
#le risposte saranno sempre stringhe
#TODO integrare  per android con il formato che vuole Felicia
#TODO testing con app o POSTMAN
def login():
    msg=''
    content=request.headers.get("Content-ID")
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = checkCredentials(username, password)
        if account:#loggato
            session['loggedin'] = True
            session['username'] = username
            session['id_user'] = account.id
            id_room = tryToGetAssignedRoom(session['id_user'])
            if id_room != -1:#sessione attiva
                digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
                if content != "LOGIN-APP":
                    return render_template('index.html', digitalTwin=digitalTwin)
                else:
                    return jsonify(loggedin=True, outcome="Active",digitalTwin=digitalTwin.serialize())
            else:#nessuna sessione attiva
                if content != "LOGIN-APP":
                    return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg=msg)
                else:
                    return jsonify(loggedin=True, outcome="Login", buildings=buildJsonList(getFreeBuildings()))
        else:
            msg = 'Incorrect username / password !'
    if content!="LOGIN-APP":
        return render_template('login.html',msg=msg)
    else:
        return jsonify(loggedin=False)
#TODO testing
@app.route('/logout',methods = ['GET','POST'])
def logout():
    content=request.headers.get("Content-ID")
    session.pop('loggedin', None)
    session.pop('username', None)
    session.pop('id_user',None)
    if content == "Logout-APP":
        return jsonify(loggedout=True)
    else:
        return redirect(url_for('login'))

#richieste che gestiscono la registrazione
#TODO registrazione tramite APP, serve sapere il formato che Felicia vuole
@app.route("/register", methods = ['GET','POST'])
def register():
    msg = ''
    #content_id=request.headers['Content-ID']
    content_id="sasso"
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        birthday=request.form['birthday']
        sex = request.form['sex']
        profession=request.form['profession']
        account=db.session.query(accounts).filter_by(username=username).first()
        if account:
            msg = 'Utente esistente!'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg='L\'username deve solo contenere lettere e numeri!'
        elif len(password)<8:
            msg = 'inserire almeno 8 caratteri nella password!'
        elif not username or not password:
            msg='Riempire i campi obbligatori!'
        else:
            account = accounts(username=username,password=password,profession=profession,sex=sex,dateOfBirth=datetime.strptime(birthday,"%Y-%m-%d"))
            db.session.add(account)
            db.session.commit()
            msg = 'Ti sei registrato con successo!'
    elif request.method == 'POST':
        msg = 'Riempire i campi obbligatori!'
    jobs=fetchJobs()
    if content_id=="REGISTER-APP":
        jobs = buildJsonList(jobs)
        return jsonify(signedUp=True,msg=msg,buildings=jobs)
    return render_template('register.html',msg=msg,jobs=jobs)

#TODO testing APP android e preparazione dati index
@app.route("/update",  methods = ['POST'])
def update():
    content=request.headers.get("Content-ID")
    id_user = 0
    color = 0
    brightness = 0
    temperature = 0
    if content == "UPDATE-APP":
        data=request.json()
        id_user=data['id_utente']
        color=data['color_val']
        brightness=data['brightness_val']
        temperature=data['temp_val']
    else:
        id_user = request.form['id_utente']
        color = request.form['color_val']
        brightness = request.form['brightness_val']
        temperature = request.form['temp_val']
    if id_user != 0:
        actualSession=db.session.query(sessionStates).filter_by(id_user=id_user,active=True)
        IdRoomOfActualSession=actualSession.id_room
        IdBuildingOfActualRoom=db.session.query(rooms).filter_by(id=IdRoomOfActualSession).id_building
        IdSessionOfActualSession = actualSession.id_session
        timestamp=datetime.now()
        digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=IdBuildingOfActualRoom).first()
        if digitalTwin.temperature_actuactor!=temperature:
            #digitalTwin.temperature_actuactor=temperature
            #db.session.add(histories(IdSessionOfActualSession,"temperature",temperature,timestamp))
            registerAction("temperature",temperature,IdSessionOfActualSession,timestamp,IdRoomOfActualSession,IdBuildingOfActualRoom,digitalTwin)
            #mqtt.publish('smartoffice/building_' + str(IdBuildingOfActualRoom) + '/room_1/actuactors/temperature', temperature)
        if digitalTwin.led_actuactor!=color:
            #digitalTwin.led_actuactor=color
            #db.session.add(histories(IdSessionOfActualSession,"color",color,timestamp))
            registerAction("color", color, IdSessionOfActualSession, timestamp,IdRoomOfActualSession,IdBuildingOfActualRoom,digitalTwin)
            #mqtt.publish('smartoffice/building_' + str(IdBuildingOfActualRoom) + '/room_1/actuactors/color', color)
        if digitalTwin.led_brightness !=brightness:
            #digitalTwin.led_brightness == brightness
            registerAction("brightness", brightness, IdSessionOfActualSession, timestamp,IdRoomOfActualSession,IdBuildingOfActualRoom,digitalTwin)
            #db.session.add(histories(IdSessionOfActualSession,"brightness",brightness,timestamp))
            #mqtt.publish('smartoffice/building_' + str(IdBuildingOfActualRoom) + '/room_1/actuactors/brightness', brightness)
        #db.session.commit()
        if content == "UPDATE-APP":
            return jsonify(changes=True)
        else:
            return render_template('index.html',digitalTwin=digitalTwin)
    return 0

#TODO da testare e adattare al formato che vuole Felicia
#TODO pagina di prenotazione per il browser
@app.route("/selectRoom",methods = ['POST'])
def occupyRoom():
    content=request.headers.get("Content-ID")
    if request.method == 'POST':
        building = request.form['building']
        id_room = tryToAssignRoom(session['id_user'], building)
        #ragioniamo: la select si può fare solo se loggati quindi va be
        if id_room == -1:
            if content=="SELECT-APP":
                return jsonify(outcome="Full",buildings=buildJsonList(getFreeBuildings()))
            else:
                msg = 'non ci sono stanze disponibili nell\'edificio ' + str(building)
                return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg=msg)
        elif id_room == -2:
            actualSession = db.session.query(sessionStates).filter_by(id_user=session['id_user'],active=True).first().id_session
            room = db.session.query(sessions).filter_by(id=actualSession).first().id_room
            building = db.session.query(rooms).filter_by(id=room).first().id_building
            session['id_room'] = room
            session['id_building'] = building
            session['actualSession'] = actualSession
            digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=room).first()
            #TODO ricavare dati da mandare
            #TODO mettere dei try catch per evitare bug
            #TODO server flask locale come failsafe
            dictToSend = {'user_age':0,'user_sex':0,'user_task':0,'ext_temp':0,'ext_humidity':0,'ext_light':0}
            res = requests.post('http://localhost:5001/tests', json=dictToSend)
            print ('response from server:', res.text)
            dictFromServer = res.json()
            led_color=dictFromServer['user_color']
            brightness=dictFromServer['user_light']
            temperature=dictFromServer['user_temp']
            timestamp=datetime.utcnow()
            registerAction('color',led_color,actualSession,timestamp,room,building,digitalTwin)
            registerAction('brightness', brightness, actualSession, timestamp, room, building,digitalTwin)
            registerAction('temperature', temperature, actualSession, timestamp, room, building,digitalTwin)
            if content=="SELECT-APP":
                return jsonify(outcome="Active",digitalTwin=digitalTwin.serialize())
            else:
                return render_template('index.html', digitalTwin=digitalTwin)
        else:
            actualSession = db.session.query(sessionStates).filter_by(id_user=session['id_user'],active=True).first().id_session
            session['id_room'] = id_room
            session['id_building'] = building
            session['actualSession'] = actualSession
            digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
            if content=="SELECT-APP":
                return jsonify(outcome="Success",digitalTwin=digitalTwin.serialize())
            else:
                return render_template('index.html', digitalTwin=digitalTwin)
    return 0

#TODO testing
@app.route("/freeRoom",methods=['POST'])
def freeRoom():
    content=request.headers.get("Content-ID")
    idSession=db.session.query(sessionStates).filter_by(id_session=session['id_user'])
    session.pop('id_room', None)
    session.pop('id_building', None)
    tryToFreeRoom(idSession)
    if content=="FREEROOM-APP":
        return jsonify(outcome="Freed")
    else:
        return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg='')


@app.route("/dashboard",methods = ['GET','POST'])
def dashboard():
    digitalTwins=db.session.query(digitalTwinFeed).all()
    return render_template('dashboard.html', digitalTwins=digitalTwins)

#TODO websocket per dashboard a tempo real
########################################################################
values = {
    'slider1': 25,
    'slider2': 0,
}
@app.route('/provawebsocket')
def prova():
    return render_template('websocket_test.html', **values)

@socketio.on('connect')
def test_connect():
    emit('after connect',  {'data':'Lets dance'})
    emit('Cambia valore', 'Hola')

@socketio.on('Slider value changed')
def value_changed(message):
    values[message['who']] = message['data']
    emit('update value', message, broadcast=True)

###############################################################################
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
       #q self.id = id
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
    id_session=db.Column('ID_SESSION', db.Integer, primary_key = True)
    type_of_action= db.Column(db.String(20))
    value= db.Column(db.String(20))
    db.Column(db.DateTime(timezone=True), nullable=True, default=datetime.utcnow)
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
    led_actuactor=db.Column(db.Integer)
    temperature_actuactor=db.Column(db.Integer)
    led_brightness=db.Column(db.Integer)
    healthy= db.Column(db.Boolean)
    def __init__(self,id_room,temperature_sensor,humidity_sensor,noise_sensor,light_sensor,led_actuactor,temperature_actuactor,led_brightness,healthy):
        self.healthy = healthy
        self.led_brightness = led_brightness
        self.temperature_actuactor = temperature_actuactor
        self.led_actuactor = led_actuactor
        self.light_sensor = light_sensor
        self.noise_sensor = noise_sensor
        self.temperature_sensor = temperature_sensor
        self.id_room = id_room
        self.humidity_sensor=humidity_sensor
    def serialize(self):
        return {"id_room": self.id_room,
                "temperature_sensor":self.temperature_sensor,
                "light_sensor":self.light_sensor,
                "led_actuactor" : self.led_actuactor,
                "temperature_actuactor" : self.temperature_actuactor,
                "led_brightness" : self.led_brightness,
                "healthy" : self.healthy,
                "noise_sensor": self.noise_sensor}
#testato
def StartListening():
    with app.app_context():
        fetchedRooms=rooms.query.all()
        for room in fetchedRooms:
            mqtt.subscribe('smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors/#')
            print("mi sono iscritto al topic "+'smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors')
    return 0



#testato
def updateDigitalTwin(id_room,sensor,value):
    with app.app_context():
        digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
        if sensor == "light":
            digitalTwin.light_sensor=value
        elif sensor == "humidity":
            digitalTwin.humidity_sensor=value
        elif sensor == "temperature":
            digitalTwin.temperature_sensor=value
        db.session.commit()
    return 0
#TODO testing
def calculateUserAge(born):
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
#testato
def appendDataToJson(jsonObj,keys,values): #testing
    for k,v in (keys,values):
        jsonObj[k]=v
    return jsonObj

#testato
def tryToAssignRoom(idUser,building):
    actualSessions = db.session.query(sessionStates).filter_by(id_user=idUser,active=True).first()
    if actualSessions:
        return -2 #sessione esistente
    else:
        activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True)  # stati attivi
        room = db.session.query(rooms).filter(rooms.id_room.notin_(activeSessionStates)).filter_by(id_building=building).first()  # stanze libere
        if room:
            now = datetime.utcnow()
            db.session.add(sessions(timestamp_begin=now))
            db.session.add(sessionStates(idUser,room.id_room))
            db.session.commit()
            return room.id_room
    return -1 # nessuna camera disponibile
#TODO testing
def tryToGetAssignedRoom(id_user):
    actualSessions = db.session.query(sessionStates).filter_by(id_user=id_user, active=True).first()
    if actualSessions:
        return actualSessions.id_room
    else:
        return -1  #sessione non esistente
#TODO: testing
def tryToFreeRoom(ID_SESSION): #testing
    now = datetime.utcnow()
    activeSessionState=db.session.query(sessionStates).filter_by(id_session=ID_SESSION).first()
    activeSessionState.active=False
    activeSession=db.session.query(sessions).filter_by(id=ID_SESSION).first()
    activeSession.timestamp_end=now
    db.session.commit()
    data=buildSessionData(activeSessionState.id_session,activeSessionState.id_room,activeSession.timestamp_begin,activeSession.timestamp_end)
    feedAIData(data)
    return 0

#TODO testing
def buildSessionData(ID_SESSION,ID_ROOM,timestamp_begin,timestamp_end):
    ID_BUILDING=db.session.query(rooms).filter_by(id_room=ID_ROOM).id_building
    data={"session_id":ID_SESSION}
    user = db.session.query(accounts).filter(id=db.session.query(sessionStates).filter(id_session=ID_SESSION).id_user)
    job = db.session.query(professions).filter(id=user.profession).name
    age=calculateUserAge(user.birthday)
    data = appendDataToJson(data,['user_id','user_age','user_sex','user_task','room_id','building_id','date','session_open_time','session_close_time'],[user.user_id,age,user.sex,job,ID_ROOM,
    ID_BUILDING,timestamp_begin.strftime("%Y/%m/%d"),timestamp_begin.strftime("%H::%M::%S"),timestamp_end.strftime("%H::%M::%S")])
    digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=ID_ROOM).first()
    data = appendDataToJson(data,['ext_temp','ext_humidity','ext_light'],[digitalTwin.temperature_sensor,digitalTwin.humity_sensor,digitalTwin.light_sensor])
    preValentTemperature = DataHistoryAccountFetch(ID_SESSION,"temperature")
    preValentColor = DataHistoryAccountFetch(ID_SESSION, "color")
    preValentBrightness = DataHistoryAccountFetch(ID_SESSION, "brightness")
    data = appendDataToJson(data, ['user_temp', 'ext_color', 'user_light'], [preValentTemperature,preValentColor,preValentBrightness])
    data = appendDataToJson(data, ['user_temp', 'ext_color', 'user_light'],[preValentTemperature, preValentColor, preValentBrightness])
    return data

#TODO testing
def DataHistoryAccountFetch(id_session,type):
    #def __init__(self, id_session, type_of_action, value, timestamp):
    maxDuration=0
    maxValue=0
    timestamp=db.session.query(sessions).filter_by(id_session=id_session).one().timestamp_begin
    actions=db.session.query(histories).filter_by(id_session=id_session,type_of_action=type).all()
    for action in actions:
        duration=minutes_between(action.timestamp,timestamp)
        if duration >= maxDuration:
            maxDuration=duration
            maxValue=action.value
        timestamp=action.timestamp
    return maxValue
#TODO testing
def minutes_between(d1, d2):
    return abs((d2 - d1).minutes)
#TODO testing
def feedAIData(data):
    fb_app.post('/sessionHistory',data)
    return 0

#TODO testing
def registerAction(type, value,session_id,timestamp,id_room,id_building,digitalTwin):
    db.session.add(histories(session_id, type, value, timestamp))
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuactors/'+type, value)
    if type=="temperature":
        digitalTwin.temperature_actuactor = value
    elif type=="color":
        digitalTwin.led_actuactor = value
    elif type=="brightness":
        digitalTwin.led_brightness = value
    db.session.commit()
    return 0

#testato
def checkCredentials(username, password):#testing
    return db.session.query(accounts).filter_by(username=username,password=password)

#testato
def getBuildings():
    return buildings.query.all()

#TODO testing
def getFreeBuildings():
    activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True)
    freeRoomsBuildings = db.session.query(rooms.id_building).filter(rooms.id_room.notin_(activeSessionStates))
    freeBuildings=db.session.query(buildings).filter(buildings.id_room.notin_(freeRoomsBuildings))
    return freeBuildings
#TODO testing
def fetchJobs():
    return professions.query.all()
#testato
def buildJsonList(list):
    new_list=[]
    for element in list:
        new_list.append(element.serialize())
    return new_list


#health check del microcontrollore
#vede se è sincronizzato con il digital twin oppure se ha problemi tecnici
#
def roomHealthCheck():
    return 0

#metodo che manda un messaggio al bot telegram
def botTelegramAlert():
    return 0

def createAndPopulateDb():
    with app.app_context():
       db.create_all()
       db.session.add(accounts(username="BArfaoui",password="18121996",profession=8,sex=1,dateOfBirth=datetime.now().date()))
       db.session.add(accounts(username="PFelica", password="99669966", profession=8, sex=2,
                               dateOfBirth=datetime.now().date()))
       db.session.add(accounts(username="Vincenzo", password="66996699", profession=8, sex=1,
                               dateOfBirth=datetime.now().date()))
       db.session.add(accounts(username="HLoredana", password="EmiliaBestWaifu", profession=10,  sex=2,
                               dateOfBirth=datetime.now().date()))
       db.session.add(accounts(username="IValeria",  password="DarthVal", profession=12,sex=2,
                               dateOfBirth=datetime.now().date()))
       db.session.add(accounts(username="Nicolò", password="11223344", profession=1, sex=3,
                               dateOfBirth=datetime.now().date()))
       db.session.add(buildings(city="Modena"))
       db.session.add(buildings(city="Roma"))
       db.session.add(buildings(city="Napoli"))
       db.session.add(buildings(city="Bologna"))
       db.session.add(buildings(city="Milano"))
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

if __name__ =="__main__":
    #with app.app_context():
     #   createAndPopulateDb()
    port=5000
    interface='0.0.0.0'
    StartListening()
    app.run(host=interface, port=port)

#TODO mettere a posto l'anno di nascita(Testing)
#TODO mettere a posto il login(Testing)
#TODO fare l'occupazione della stanza(Testing)
#TODO fare lo sgombero della stanza con scritttura al server firebase(Testing)
#TODO aggiornamento dei dati del digital twin da MQTT (Testing...)
#TODO richiesta dati all'ai (ai fittizia al momento da testare, e impostare un catch in caso di errore)
#TODO richieste da parte del client per la modifica del colore(Testing)
#TODO impostare try catch per richieste HTTP