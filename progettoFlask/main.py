import datetime
import re
import requests as requests
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from models import db,digitalTwinFeed,accounts,sessions,sessionStates,rooms,professions,histories,buildings
from flask_mqtt import Mqtt
from flask_cors import CORS
import paho.mqtt.client as mqtt
from firebase import firebase
from flask_socketio import emit, SocketIO
from datetime import datetime
appname="IOT main"
app = Flask(appname)
app.secret_key = 'secretkey'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MQTT_BROKER_URL'] = 'broker.hivemq.com'#'ilvero.davidepalma.it'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 1883  # default port for non-tls connection
#app.config['MQTT_USERNAME'] ='uni'  # set the username here if you need authentication for the broker
#app.config['MQTT_PASSWORD'] = 'more'#   set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = "random string"
mqtt=Mqtt()

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
        updateDigitalTwinSensors(identifiers[1],sensor[4],values[0])
    #with app.test_request_context('/'):
     #   socketio.emit('Cambia valore', message.topic,broadcast=True)


@app.route("/") #percorsi url locali
def homepage():
    return render_template('login.html',msg='')
@app.route("/signup",  methods = ['GET'])
def signUp():
    content=request.headers.get("Content-ID")
    jobs = fetchJobs()
    if content=="REGISTER-APP":
        jobs = buildJsonList(jobs)
        return jsonify(jobs=jobs)
    else:
        return render_template('register.html',msg='',jobs=jobs)
@app.route("/dashboard",methods = ['GET'])
def dashboard():
    digitalTwins=db.session.query(digitalTwinFeed).all()
    return render_template('dashboard.html', digitalTwins=digitalTwins)


@app.route('/login',methods = ['POST'])
def login():
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = checkCredentials(username, password)
        msg = ''
        content = request.headers.get("Content-ID")
        if account is not None :#loggato
            session['loggedin'] = True
            session['id_user'] = account.id
            session['username'] = username
            id_room = tryToGetAssignedRoom(session['id_user'])
            if id_room != -1:
                if content == "LOGIN-APP":
                    content = "HOME-APP"
                return renderHome(id_room,content)
            else:
                if content == "LOGIN-APP":
                    content="SELECTION-APP"
                return renderSelection(content)
        else:
            msg = 'Incorrect username / password !'
    else:
        msg='Riempire i campi!'
    if content!="LOGIN-APP":
        return render_template('login.html',msg=msg)
    else:
        return jsonify(logged_in=False)




#TODO testing
@app.route('/logout',methods = ['POST'])
def logout():
    content=request.headers.get("Content-ID")
    session.pop('loggedin', None)
    session.pop('id_user',None)
    session.pop('username', None)
    if content == "Logout-APP":
        return jsonify(loggedout=True)
    else:
        return render_template('login.html',msg='')
#TODO testare la registrazione
@app.route("/register", methods = ['GET','POST'])
def register():
    msg = ''
    signedUp=False
    content=request.headers.get("Content-ID")
    if 'username' in request.form and 'password' in request.form:
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
            signedUp=True
    else:
        msg = 'Riempire i campi obbligatori!'
    if content=="REGISTER-APP":
        return jsonify(signedUp=signedUp,msg=msg)
    else:
        return redirect(url_for('signup'))
#TODO testing
#TODO questa route serve anche per l'app






#TODO richiesta POST per far vedere i palazzi liberi
@app.route("/roomListing", methods=['POST'])
def listRooms():
    content = request.headers.get("Content-ID")
    if content != "SELECTION-APP":
        return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg='')
    else:
        return jsonify(loggedin=True, outcome="Login", buildings=buildJsonList(getFreeBuildings()))


######################################################################################################################
#Fine route che ritornano una view

#TODO testing APP android e preparazione dati index
#TODO renderlo impervio agli exceptions
@app.route("/update",  methods = ['POST'])
def update():
    content=request.headers.get("Content-ID")
    if content == "UPDATE-APP":
        data=request.get_json(silent=True)
        id_user=data['id_utente']
        color=data['color_val']
        brightness=data['brightness_val']
        temperature=data['temp_val']
        digitalTwin=updateDigitalTwinActuators(id_user,color,brightness,temperature)
        return jsonify(changes=True,digitalTwin=digitalTwin.serializedActuators())
    else:
        id_user = session['id_user']
        color = int(request.form['color'])
        brightness = int(request.form['brightness'])
        temperature = int(request.form['temperature'])
        digitalTwin=updateDigitalTwinActuators(id_user, color, brightness, temperature)
        return render_template('index.html',digitalTwin=digitalTwin,username=session['username'])

#TODO da testare e adattare al formato che vuole Felicia
#TODO pagina di prenotazione per il browser
#TODO rendere questa fase impervia agli exception perchè è una fase delicata
#TODO codice da snellire
#TODO caso 1, l'utente ha appena loggato e sceglie un edificio vuoto
#TODO caso 2 l'utente ha appena loggato e sceglie un edificio pieno
#TODO caso 3 l'utente ha appena loggato e ha già una stanza assegnata
@app.route("/selectRoom",methods = ['POST'])
def occupyRoom():
    content=request.headers.get("Content-ID")
    id_room=-1
    if content == "SELECT-APP":
        #prendo dati dal json
        data = request.get_json(silent=True)
        id_user = data['id_utente']
        building = data['building_id']
        id_room = tryToAssignRoom(id_user, building)
        return handleRoomAssignment(id_room, content, building)
    else:
        #prendo dati dal form e sessione
        building = request.form['building']
        id_room = tryToAssignRoom(session['id_user'], building)
        return handleRoomAssignment(id_room,content,building)

#TODO testing
#TODO coprire i casi dove può dare errore
@app.route("/freeRoom",methods=['POST'])
def freeRoom():
    content=request.headers.get("Content-ID")
    session.pop('id_room', None)
    session.pop('id_building', None)
    if content == "FREEROOM-APP":
        data = request.get_json(silent=True)
        id_user = data['id_utente']
        idSession = db.session.query(sessionStates) .filter_by(id_user=id_user,active=True).first().id_session
        tryToFreeRoom(idSession)
        return jsonify(outcome="Freed")
    else:
        idSession=db.session.query(sessionStates).filter_by(id_user=session['id_user'],active=True).first().id_session
        tryToFreeRoom(idSession)
        return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg='')




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




def redirectWithParams(route,method,header):
    if method == "POST":
        redir = redirect(url_for(route, code=307))
        redir.headers['Content-ID'] = header
    else:
        redir = redirect(url_for(route))
        redir.headers['Content-ID'] = header
    return redir


#testato
def StartListening():
    with app.app_context():
        fetchedRooms=rooms.query.all()
        for room in fetchedRooms:
            mqtt.subscribe('smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors/#')
            print("mi sono iscritto al topic "+'smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors')
    return 0



#testato
def updateDigitalTwinSensors(id_room,sensor,value):
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
def updateDigitalTwinActuators(id_user, color, brightness, temperature):
    actualSession=db.session.query(sessionStates).filter_by(id_user=id_user,active=True).first()
    IdRoomOfActualSession=actualSession.id_room
    IdBuildingOfActualRoom=db.session.query(rooms).filter_by(id_room=IdRoomOfActualSession).first().id_building
    IdSessionOfActualSession = actualSession.id_session
    timestamp=datetime.utcnow()
    digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=IdRoomOfActualSession).first()
    if digitalTwin.temperature_actuator!=temperature:
        registerAction("temperature",temperature,IdSessionOfActualSession,timestamp,IdRoomOfActualSession,IdBuildingOfActualRoom,digitalTwin)
    if digitalTwin.led_actuator!=color:
        registerAction("color", color, IdSessionOfActualSession, timestamp,IdRoomOfActualSession,IdBuildingOfActualRoom,digitalTwin)
    if digitalTwin.led_brightness !=brightness:
        registerAction("brightness", brightness, IdSessionOfActualSession, timestamp,IdRoomOfActualSession,IdBuildingOfActualRoom,digitalTwin)
    db.session.commit()
    return digitalTwin

#TODO testing
def handleRoomAssignment(id_room,content,building):
    if id_room == -1: #stanza non disponibile
        if content=="SELECT-APP":
            return jsonify(outcome="Full",buildings=buildJsonList(getFreeBuildings()))
        else:
            msg = 'non ci sono stanze disponibili nell\'edificio ' + str(building)
            return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg=msg)
    elif id_room == -2: #stanza esistente
        sessionState=db.session.query(sessionStates).filter_by(id_user=session['id_user'],active=True).first()
        actualSession = sessionState.id_session
        room = sessionState.id_room
        building = db.session.query(rooms).filter_by(id_room=room).first().id_building
        session['id_room'] = room
        session['id_building'] = building
        session['actualSession'] = actualSession
        digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=room).first()
        if fetchLastSetting(actualSession,digitalTwin) == -1:
            prepareRoom(session['id_user'], actualSession, digitalTwin, session['id_building'])
        if content=="SELECT-APP":
            return jsonify(outcome="Active",digitalTwin=digitalTwin.serialize())
        else:
            return render_template('index.html', digitalTwin=digitalTwin)
    else:#stanza assegnata
        actualSession = db.session.query(sessionStates).filter_by(id_user=session['id_user'],active=True).first().id_session
        session['id_room'] = id_room
        session['id_building'] = building
        session['actualSession'] = actualSession
        digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
        prepareRoom(session['id_user'],actualSession,digitalTwin,session['id_building'])
        if content=="SELECT-APP":
            return jsonify(outcome="Success",digitalTwin=digitalTwin.serialize())
        else:
            return render_template('index.html', digitalTwin=digitalTwin,session=session['username'])

#TODO testing
def prepareRoom(id_user,id_session,digitalTwin,id_building):
    data = getAIdata(id_user, digitalTwin)
    led_color = data['user_color']
    brightness = data['user_light']
    temperature = data['user_temp']
    timestamp = datetime.utcnow()
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=digitalTwin.id_room).first()
    registerAction('color', led_color, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('brightness', brightness, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('temperature', temperature, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    return 0

#tested
def getAIdata(id_user,digitalTwin):
    account = db.session.query(accounts).filter_by(id=id_user).first()
    job = db.session.query(professions).filter_by(id_profession=account.profession).first()
    dataToSend = {'user_age': calculateUserAge(account.dateOfBirth), 'user_sex': account.sex, 'user_task': job.name,
                  'ext_temp': digitalTwin.temperature_sensor, 'ext_humidity': digitalTwin.humidity_sensor,
                  'ext_light': digitalTwin.light_sensor}
    try:
        res = requests.post('http://localhost:5001/AI', json=dataToSend)
        print('response from server:', res.text)
        dataFromServer = res.json()
    except requests.exceptions.RequestException as e:
        print("c'è stato un errore! Prenderò i dati dall'AI locale!")
        try:
            res = requests.post('http://localhost:5001/AI', json=dataToSend)
            print('response from server:', res.text)
            dataFromServer = res.json()
        except requests.exceptions.RequestException as e:
            print("c'è stato un errore! Prenderò dati di Default!")
            dataFromServer = {'user_temp':25,'user_color':3,'user_light':4}
    return dataFromServer


#TODO testing e caso dove il db è vuoto
#Se il db è vuoto chiediamo i dati all'AI per sicurezza
def fetchLastSetting(id_session,digitalTwin):
    historyColor = db.session.query(histories).filter_by(id_session=id_session,type_of_action="color").order_by(histories.timestamp).first()
    historyBrightness=db.session.query(histories).filter_by(id_session=id_session,type_of_action="brightness").order_by(histories.timestamp).first()
    historyTemperature=db.session.query(histories).filter_by(id_session=id_session,type_of_action="temperature").order_by(histories.timestamp).first()
    if historyBrightness is not None and historyColor is not None and historyTemperature is not None:
        digitalTwin.led_actuator=historyColor.value
        digitalTwin.led_brightness=historyBrightness.value
        digitalTwin.temperature_actuator=historyTemperature.value
        db.session.commit()
    else:
        return -1
    return 0
#tested
def renderHome(id_room,content):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    if content != "HOME-APP":
        return render_template('index.html', digitalTwin=digitalTwin, username=session['username'])
    else:
        return jsonify(logged_in=True, outcome="Active", digitalTwin={"led_actuator": 0,"temperature_actuator": 0,
                "led_brightness": 0},id=session['id_user'],id_edificio=0,id_room=0,username=session['username'])
def renderSelection(content):
    if content != "SELECTION-APP":
        return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg='')
    else:
        #return jsonify(loggedin=True, outcome="Login", buildings=buildJsonList(getFreeBuildings()))
        return jsonify(logged_in=True, outcome="Active", digitalTwin={"led_actuator": 0, "temperature_actuator": 0,
                                                                      "led_brightness": 0}, id=session['id_user'],
                       id_edificio=0, id_room=0, username=session['username'])
#tested
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
        session["id_room"] = actualSessions.id_room
        session["building"] = db.session.query(rooms).filter_by(id_room=actualSessions.id_room).first().id_building
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
    ID_BUILDING=db.session.query(rooms).filter_by(id_room=ID_ROOM).one().id_building
    data={"session_id":ID_SESSION}
    user = db.session.query(accounts).filter_by(id=db.session.query(sessionStates).filter_by(id_session=ID_SESSION).one().id_user).one()
    job = db.session.query(professions).filter_by(id_profession=user.profession).one().name
    age=calculateUserAge(user.dateOfBirth)
    new_data = {'user_id':user.id,'user_age':age,'user_sex':user.sex,'user_task':job,'room_id':ID_ROOM,'building_id':ID_BUILDING,'date':timestamp_begin.strftime("%Y/%m/%d"),
           'session_open_time':timestamp_begin.strftime("%H:%M:%S"),'session_close_time':timestamp_end.strftime("%H:%M:%S")}
    data ={**data, **new_data}
    digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=ID_ROOM).first()
    new_data={'ext_temp':digitalTwin.temperature_sensor,'ext_humidity':digitalTwin.humidity_sensor,'ext_light':digitalTwin.light_sensor}
    data = {**data, **new_data}
    preValentTemperature = DataHistoryAccountFetch(ID_SESSION,"temperature")
    preValentColor = DataHistoryAccountFetch(ID_SESSION, "color")
    preValentBrightness = DataHistoryAccountFetch(ID_SESSION, "brightness")
    new_data={'user_temp':preValentTemperature, 'ext_color':preValentColor, 'user_light':preValentBrightness}
    data = {**data, **new_data}
    return data

#TODO testing
def DataHistoryAccountFetch(id_session,type):
    maxDuration=0
    maxValue=0
    timestamp_end = db.session.query(sessions).filter_by(id=id_session).one().timestamp_end
    actions=db.session.query(histories).filter_by(id_session=id_session,type_of_action=type).all()
    for action in actions:
        if actions.index(action) == (len(actions) -1):
            duration=seconds_between(timestamp_end,action.timestamp)
            print("The actuator "+type+" had the value:" +str(action.value)+" for "+str(duration)+" seconds!")
            if duration >= maxDuration:
                maxDuration=duration
                maxValue=action.value
        else:
            duration=seconds_between(actions[actions.index(action) + 1].timestamp,action.timestamp)
            print("The actuator "+type+" had the value:" +str(action.value)+" for "+str(duration)+" seconds!")
            if duration >= maxDuration:
                maxDuration=duration
                maxValue=action.value
    print("The actuator " + type + " had the value:" + str(maxValue) + " for the most time! " + str(maxDuration) + "seconds!")
    return maxValue
#tested
def seconds_between(d1, d2):
    return abs((d2 - d1).total_seconds())

#tested
def feedAIData(data):
    fb_app.post('/sessionHistory',data)
    return 0

#tested
def registerAction(type, value,session_id,timestamp,id_room,id_building,digitalTwin):
    db.session.add(histories(session_id, type, value, timestamp))
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuators/'+type, value)
    print('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuators/'+type)
    if type=="temperature":
        digitalTwin.temperature_actuator = value
    elif type=="color":
        digitalTwin.led_actuator = value
    elif type=="brightness":
        digitalTwin.led_brightness = value
    db.session.commit()
    return 0

#testato
def checkCredentials(username, password):#testing
    account =db.session.query(accounts).filter_by(username=username,password=password).first()
    return account

#testato
def getBuildings():
    return buildings.query.all()

#tested
def getFreeBuildings():
    activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True)
    freeRoomsBuildings = db.session.query(rooms.id_building).filter(rooms.id_room.notin_(activeSessionStates))
    freeBuildings=db.session.query(buildings).filter(buildings.id_building.in_(freeRoomsBuildings))
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
        #createAndPopulateDb()
        #DataHistoryAccountFetch(3,"temperature")
        #digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=1).first()
        #getAIdata(1, digitalTwin)
    db.init_app(app)
    mqtt.init_app(app)
    port=5000
    interface='0.0.0.0'
    StartListening()
    app.run(host=interface, port=port)

#DONE mettere a posto l'anno di nascita(Tested)
#DONE mettere a posto il login(Tested)
#TODO occupazione della stanza(Testing)
#DONE fare lo sgombero della stanza con scritttura al server firebase(Done)
#DONE testare il collasso della cronologia e controllare lo sgombero della stanza
#DONE aggiornamento dei dati del digital twin da MQTT (Testato con il microcontrollore di Felicia)
#DONE richiesta dati all'ai (try-catch impostati)
#DONE richieste da parte del client per la modifica del colore(Tested)
#TODO impostare l'indirizzo per l'AI
#TODO impostare i dati di default nel caso l'AI e l'AI fittizia schiattino
#TODO testare la preparazione della stanza
#TODO aggiornare la registrazione
#TODO testare il login
#TODO snellire il codice
#TODO commentare
#TODO snellire il codice dell'interpretazione dei dati mqtt
#TODO fornire i dati che vuole Felicia
#TODO impostare un error handler, che reindirizza alla pagina di login/index/selezione
#TODO separare le route get da quelle post, per snellire il codice (Non causa codice ripetuto)
#TODO dati sessione {id_user,logged_in(non so se serve),id_sessione,id_stanza,id_building}
#TODO dati che servono per l'app android in base alla route
#TODO fixare i timestamp
#TODO testare l'update snellito
#TODO aggiungere controlli nel caso di errore nella scrittura nel db
#TODO gestione della sessione web->Session app->tramite json
#TODO geodecodificazione
#TODO Content-ID dell'header LOGIN-APP,REGISTER-APP,SELECT-APP

#REPORT(Testing Login):
#Mostra gli edifici liberi correttamente
#Se una sessione è attiva lo porta in output
#Login funzionante

#REPORT (SelectRoom)

