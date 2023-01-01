import datetime
import re
import requests as requests
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from models import db,digitalTwinFeed,accounts,sessions,sessionStates,rooms,professions,histories,buildings, createAndPopulateDb
from flask_mqtt import Mqtt
from flask_cors import CORS
import paho.mqtt.client as mqtt
from firebase import firebase
from flask_socketio import emit, SocketIO
from datetime import datetime
from utilities import buildJsonList,calculateUserAge
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
#testato
@app.route('/logout',methods = ['POST'])
def logout():
    content=request.headers.get("Content-ID")
    session.pop('loggedin', None)
    session.pop('id_user',None)
    session.pop('username', None)
    session.pop('id_building',None)
    session.pop('id_room',None)
    if content == "Logout-APP":
        return jsonify(loggedout=True)
    else:
        return render_template('login.html',msg='')
#testato
@app.route("/register", methods = ['GET','POST'])
def register():
    msg = ''
    signedUp=False
    jobs = fetchJobs()
    content=request.headers.get("Content-ID")
    if request.method == 'POST':
        if 'username' in request.form and 'password'in request.form and 'birthday'in request.form and 'sex'in request.form and 'profession'in request.form:
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
        if content == "REGISTER-APP":
            jobs = buildJsonList(jobs)
            return jsonify(signedUp=signedUp,msg=msg,jobs=jobs)
        else:
            return render_template('register.html', msg=msg, jobs=jobs)
    else:
        if content == "REGISTER-APP":
            jobs = buildJsonList(jobs)
            return jsonify(jobs=jobs)
        else:
            return render_template('register.html', msg=msg, jobs=jobs)
######################################################################################################################
#Fine route che ritornano una view

#testato
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

#testato
@app.route("/selectRoom",methods = ['POST'])
def occupyRoom():
    content=request.headers.get("Content-ID")
    #id_room=-1
    id_user=0
    building=0
    if content == "SELECT-APP":
        #prendo dati dal json
        data = request.get_json(silent=True)
        id_user = data['id_utente']
        building = data['building_id']
        #id_room = tryToAssignRoom(id_user, building)
        #return handleRoomAssignment(id_user,id_room, content, building)
    else:
        #prendo dati dal form e sessione
        building = request.form['building']
        id_user=session['id_user']
        #id_room = tryToAssignRoom(session['id_user'], building)
    return handleRoomAssignment(id_user,content,building)


#testato
@app.route("/freeRoom",methods=['POST'])
def freeRoom():
    content=request.headers.get("Content-ID")
    session.pop('id_room', None)
    session.pop('id_building', None)
    if content == "FREEROOM-APP":
        data = request.get_json(silent=True)
        id_user = data['id_utente']
        tryToFreeRoom(id_user)
        return jsonify(outcome="Freed")
    else:
        tryToFreeRoom(session['id_user'])
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
#TODO metodi non ancora implementati
#TODO da vedere se lo implemento o meno, magari al resume session
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
#TODO
def roomHealthCheck():
    return 0
#TODO
#metodo che manda un messaggio al bot telegram
def botTelegramAlert():
    return 0
#################################################################################
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
#testato
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
#testato
def prepareRoom(id_user,id_session,digitalTwin,id_building):
    data = getAIdata(id_user, digitalTwin)
    led_color = data['user_color']
    brightness = data['user_light']
    temperature = data['user_temp']
    timestamp = datetime.utcnow()
    #ew
    #digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=digitalTwin.id_room).first()
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
            dataFromServer = {'user_temp':21,'user_color':9,'user_light':3}
    return dataFromServer
#tested
def renderHome(id_room,content):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    if content != "HOME-APP" and content!= "SELECT-APP":
        return render_template('index.html', digitalTwin=digitalTwin, username=session['username'])
    else:
        return jsonify(logged_in=True, outcome="Active", digitalTwin=digitalTwin.serializedActuators(),id=session['id_user'],id_edificio=0,id_room=0,username=session['username'])
def renderSelection(content):
    if content != "SELECTION-APP":
        return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg='')
    else:
        #return jsonify(loggedin=True, outcome="Login", buildings=buildJsonList(getFreeBuildings()))
        return jsonify(logged_in=True, outcome="Login", digitalTwin={"led_actuator": 0, "temperature_actuator": 0,
                                                                      "led_brightness": 0}, id=session['id_user'],
                       id_edificio=0, id_room=0, username=session['username'])
#tested


#testato
#return della json con esito e session state
# -1 pieno -2 esistente 0 successo
def tryToAssignRoom(id_user,building):
    actual_sessionState = db.session.query(sessionStates).filter_by(id_user=id_user,active=True).first()
    if actual_sessionState is not None:
        return {"outcome":-2,"session_state":actual_sessionState} #sessione esistente
    else:
        active_sessionStates = db.session.query(sessionStates.id_room).filter_by(active=True)  # stati attivi
        room = db.session.query(rooms).filter(rooms.id_room.notin_(active_sessionStates)).filter_by(id_building=building).first()  # stanze libere
        if room:
            now = datetime.utcnow()
            db.session.add(sessions(timestamp_begin=now))
            db.session.add(sessionStates(id_user,room.id_room))
            db.session.commit()
            assigned_sessionState= db.session.query(sessionStates).filter_by(id_user=id_user,active=True).first()
            return {"outcome":0,"session_state":assigned_sessionState}
    return {"outcome":-1} # nessuna camera disponibile nell'edificio

#tested
def handleRoomAssignment(id_user,content,building):
    data = tryToAssignRoom(id_user,building)
    if data["outcome"] == -1: #palazzo pieno
        if content=="SELECT-APP":
            return jsonify(outcome="Full",buildings=buildJsonList(getFreeBuildings()))
        else:
            msg = 'non ci sono stanze disponibili nell\'edificio ' + str(building)
            return render_template('select.html', buildings=buildJsonList(getFreeBuildings()), msg=msg)
    elif data["outcome"] == -2: #stanza esistente
        session['id_room'] = data["session_state"].id_room
        session['id_building'] = building
        return renderHome(data["session_state"].id_room,content)
    else:#stanza assegnata
        session['id_room'] = data["session_state"].id_room
        session['id_building'] = building
        digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=data["session_state"].id_room).first()
        prepareRoom(id_user,data["session_state"].id_session,digitalTwin,building)
        return renderHome(data["session_state"].id_room,content)
#tested
def tryToGetAssignedRoom(id_user):
    actualSessions = db.session.query(sessionStates).filter_by(id_user=id_user, active=True).first()
    if actualSessions:
        session["id_room"] = actualSessions.id_room
        session["building"] = db.session.query(rooms).filter_by(id_room=actualSessions.id_room).first().id_building
        return actualSessions.id_room
    else:
        return -1  #sessione non esistente
#testato
def tryToFreeRoom(id_user):
    active_sessionState = db.session.query(sessionStates).filter_by(id_user=id_user, active=True).first()
    active_session=db.session.query(sessions).filter_by(id=active_sessionState.id_session).first()
    room = db.session.query(rooms).filter_by(id_room=active_sessionState.id_room).first()
    user = db.session.query(accounts).filter_by(id=id_user).first()
    now = datetime.utcnow()
    active_sessionState.active=False
    active_session.timestamp_end=now
    db.session.commit()
    data=buildSessionData(user,room,active_session)
    feedAIData(data)
    return 0

#testato
def buildSessionData(user,room,active_session):
    preValentTemperature = DataHistoryAccountFetch(active_session.id, "temperature")
    preValentColor = DataHistoryAccountFetch(active_session.id, "color")
    preValentBrightness = DataHistoryAccountFetch(active_session.id, "brightness")
    digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=room.id_room).first()
    job = db.session.query(professions).filter_by(id_profession=user.profession).one().name
    age=calculateUserAge(user.dateOfBirth)
    data = {'user_age':age,'user_sex':user.sex,'user_task':job,'room_id':room.id_room,'building_id':room.id_building,
            'date':active_session.timestamp_begin.strftime("%Y/%m/%d"),
            'session_open_time':active_session.timestamp_begin.strftime("%H:%M:%S"),
            'session_close_time':active_session.timestamp_end.strftime("%H:%M:%S"),'ext_temp':digitalTwin.temperature_sensor,
            'ext_humidity':digitalTwin.humidity_sensor,'ext_light':digitalTwin.light_sensor,
            'user_temp': preValentTemperature, 'user_color': preValentColor, 'user_light': preValentBrightness}
    return data

#Testato
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
#testato
def fetchJobs():
    return professions.query.all()
#testato

#health check del microcontrollore
#vede se è sincronizzato con il digital twin oppure se ha problemi tecnici







if __name__ =="__main__":
    db.init_app(app)
    mqtt.init_app(app)
    #with app.app_context():
     #   createAndPopulateDb()
    port=5000
    interface='0.0.0.0'
    StartListening()
    app.run(host=interface, port=port)

#DONE mettere a posto l'anno di nascita(Tested)
#DONE mettere a posto il login(Tested)
#DONE occupazione della stanza
#DONE fare lo sgombero della stanza con scritttura al server firebase(Done)
#DONE testare il collasso della cronologia e controllare lo sgombero della stanza
#DONE aggiornamento dei dati del digital twin da MQTT (Testato con il microcontrollore di Felicia)
#DONE richiesta dati all'ai (try-catch impostati)
#DONE richieste da parte del client per la modifica del colore(Tested)
#DONE impostare i dati di default nel caso l'AI e l'AI fittizia schiattino
#DONE testare la preparazione della stanza
#DONE aggiornare la registrazione
#DONE testare il login
#TODO impostare l'indirizzo per l'AI
#TODO snellire il codice
#TODO commentare
#TODO snellire il codice dell'interpretazione dei dati mqtt
#TODO fornire i dati che vuole Felicia
#TODO impostare un error handler, che reindirizza alla pagina di login/index/selezione
#TODO dati che servono per l'app android in base alla route
#TODO fixare i timestamp
#DONE testare l'update snellito
#TODO Content-ID dell'header LOGIN-APP,REGISTER-APP,SELECT-APP,LOGOUT-APP
#TODO gestione expetions scrittura su db
#TODO gestione mancanza dati form (se serve)
#TODO fixare le view
#REPORT(Testing Login):
#Mostra gli edifici liberi correttamente
#Se una sessione è attiva lo porta in output
#Login funzionante

#REPORT (SelectRoom)

