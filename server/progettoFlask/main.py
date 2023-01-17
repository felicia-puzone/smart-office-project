import datetime
import re
<<<<<<< HEAD
from itsdangerous import BadSignature

import requests as requests
from flask import Flask, request, render_template, session,jsonify
from werkzeug.exceptions import HTTPException

from apphandler import app
import geolog
from models import db, digitalTwinFeed, sessions, sessionStates, rooms, professions, actuatorFeeds, buildings, \
    zones, User, serializer, serializer_secret, weatherReport, zoneToBuildingAssociation
from firebase import firebase
from mqtthandler import mqtt
from modelviews import ZoneAdmin, UserAdmin, JobAdmin, BuildingAdmin, RoomAdmin, MyHomeView
from queries import fetchJobs, getFreeBuildings, createAndPopulateDb, buildRoomLightSensorGraph, buildRoomColorGraph, \
    buildRoomBrightnessGraph, buildRoomTemperatureGraph, buildBuildingLightSensorGraph, buildZoneWeatherGraph, \
    buildZoneWeatherHumidityGraph
from utilities import buildJsonList, calculateUserAge, createABuildingtupleList, createAProfessiontupleList, \
    seconds_between, colors, brightness_values
from flask_admin import Admin
from flask_login import current_user, LoginManager, login_user, logout_user, login_required,UserMixin
from flask import Flask, jsonify, make_response, request
from weather import weather_report

login_manager = LoginManager()
login_manager.init_app(app)
fb_app = firebase.FirebaseApplication('https://smartoffice-4eb51-default-rtdb.europe-west1.firebasedatabase.app/', None)
db.init_app(app)
mqtt.init_app(app)
#with app.app_context():
 #   createAndPopulateDb()

admin = Admin(app, name='Spazio Admin',index_view=MyHomeView())
admin.add_view(ZoneAdmin(zones, db.session))
admin.add_view(BuildingAdmin(buildings, db.session))
admin.add_view(RoomAdmin(rooms, db.session))
admin.add_view(JobAdmin(professions, db.session))
admin.add_view(UserAdmin(User, db.session))

#Questo decorator gestisce tutti di errore, se la sessione utente
#è attiva, reidirizza a handleLoggedInUser
#altrimenti reindirizza alla homepage 'login.html'
@app.errorhandler(HTTPException)
def handle_bad_request(e):
    print('bad request!', 400)
    if current_user.is_authenticated:
        return handleLoggedinUser("")
    else:
        return render_template('login.html',msg='')



@login_manager.request_loader
def load_user_from_request(request):
        if request.headers.get('Auth-token'):
            token = request.headers.get('Auth-token')
            return token_check(token)
        else:
            if session.get("Auth-token"):
                token = session["Auth-token"]
                return token_check(token)
            return None

def token_check(token):
    max_age = 10000000
    try:
        data = serializer.loads(token, salt=serializer_secret, max_age=max_age)
        username = data[0]
        password_hash = data[1]
        found_user = db.session.query(User).filter_by(username=username).first()
        found_password = found_user.password
        if found_user and found_password == password_hash:
            return found_user
        else:
            return None
    except BadSignature as e:
        return None


#tested
@login_manager.unauthorized_handler
def unauthorized_callback():
    content = request.headers.get("Content-ID")
    print(content)
    if content is not None:
        return "Not logged in", 401
    return render_template('login.html',msg='')





=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd


@app.route("/") #percorsi url locali
def homepage():
<<<<<<< HEAD
    if current_user.is_authenticated:
        return handleLoggedinUser("")
    else:
        return render_template('login.html',msg='')

@app.route("/professions",methods=['GET'])
def fetchprofessions():
    return buildJsonList(fetchJobs())

#/Login
#Metodi accettati POST
#Si
@app.route('/login',methods = ['POST'])
def login():
    content = request.headers.get("Content-ID")
    msg=''
    if 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = db.session.query(User).filter_by(username=username).first()
        if account and account.verify_password(password) :
            login_user(account)
            token=account.get_auth_token(username,account.password)
            return handleAuthenticatedUserResponse(content,token)
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
        else:
            msg = 'Incorrect username / password !'
    else:
        msg='Riempire i campi!'
    if content!="LOGIN-APP":
        return render_template('login.html',msg=msg)
    else:
        return jsonify(logged_in=False)
<<<<<<< HEAD

#testato

@app.route('/logout',methods = ['POST'])
@login_required
def logout():
    content=request.headers.get("Content-ID")
    logout_user()
    if content == "Logout-APP":
        return jsonify(loggedout=True)
    else:
        session.pop("Auth-token")
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
            birthday= request.form['birthday']
            sex = request.form['sex']
            profession=request.form['profession']
            account=db.session.query(User).filter_by(username=username).first()
            job = db.session.query(professions).filter_by(id_profession=profession).first()
            if account:
                msg = 'Utente esistente!'
            elif job is None:
                msg = 'Professione non esistente!'
=======
            birthday=request.form['birthday']
            sex = request.form['sex']
            profession=request.form['profession']
            account=db.session.query(accounts).filter_by(username=username).first()
            if account:
                msg = 'Utente esistente!'
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
            elif not re.match(r'[A-Za-z0-9]+',username):
                msg='L\'username deve solo contenere lettere e numeri!'
            elif len(password)<8:
                msg = 'inserire almeno 8 caratteri nella password!'
            elif not username or not password:
                msg='Riempire i campi obbligatori!'
            else:
<<<<<<< HEAD
                #hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                account = User(username=username,password=password,profession=job.name,sex=sex,dateOfBirth=datetime.datetime.strptime(birthday,"%Y-%m-%d"))
=======
                account = accounts(username=username,password=password,profession=profession,sex=sex,dateOfBirth=datetime.strptime(birthday,"%Y-%m-%d"))
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
                db.session.add(account)
                db.session.commit()
                msg = 'Ti sei registrato con successo!'
                signedUp=True
        else:
            msg = 'Riempire i campi obbligatori!'
        if content == "REGISTER-APP":
<<<<<<< HEAD
            return jsonify(signedUp=signedUp,msg=msg)
=======
            jobs = buildJsonList(jobs)
            return jsonify(signedUp=signedUp,msg=msg,jobs=jobs)
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
        else:
            return render_template('register.html', msg=msg, jobs=jobs)
    else:
        if content == "REGISTER-APP":
            jobs = buildJsonList(jobs)
            return jsonify(jobs=jobs)
        else:
            return render_template('register.html', msg=msg, jobs=jobs)
######################################################################################################################
<<<<<<< HEAD
#testato

@app.route("/update",  methods = ['POST'])
@login_required
=======
#Fine route che ritornano una view

#testato
@app.route("/update",  methods = ['POST'])
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
def update():
    content=request.headers.get("Content-ID")
    if content == "UPDATE-APP":
        data=request.get_json(silent=True)
<<<<<<< HEAD
        id_user = current_user.get_id()
=======
        id_user=data['id_utente']
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
        color=data['color_val']
        brightness=data['brightness_val']
        temperature=data['temp_val']
        digitalTwin=updateDigitalTwinActuators(id_user,color,brightness,temperature)
        return jsonify(changes=True,digitalTwin=digitalTwin.serializedActuators())
    else:
<<<<<<< HEAD
        id_user = current_user.get_id()
        color = colors[int(request.form['color'])]
        brightness = brightness_values[int(request.form['brightness'])]
        temperature = int(request.form['temperature'])
        digitalTwin=updateDigitalTwinActuators(id_user, color, brightness, temperature)
        return render_template('index.html',digitalTwin=digitalTwin,username=current_user.get_username())

#testato

@app.route("/selectRoom",methods = ['POST'])
@login_required
=======
        id_user = session['id_user']
        color = int(request.form['color'])
        brightness = int(request.form['brightness'])
        temperature = int(request.form['temperature'])
        digitalTwin=updateDigitalTwinActuators(id_user, color, brightness, temperature)
        return render_template('index.html',digitalTwin=digitalTwin,username=session['username'])

#testato
@app.route("/selectRoom",methods = ['POST'])
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
def occupyRoom():
    content=request.headers.get("Content-ID")
    #id_room=-1
    id_user=0
    building=0
    if content == "SELECT-APP":
<<<<<<< HEAD
        data = request.get_json(silent=True)
        id_user = current_user.get_id()
        building = data['building_id']
    else:
        #prendo dati dal form e sessione
        building = request.form['building']
        id_user=current_user.get_id()
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
        #id_room = tryToAssignRoom(session['id_user'], building)
    return handleRoomAssignment(id_user,content,building)


<<<<<<< HEAD


#testato
@app.route("/freeRoom",methods=['POST'])
@login_required
def freeRoom():
    content=request.headers.get("Content-ID")
    if content == "FREEROOM-APP":
        #data = request.get_json(silent=True)
        id_user=current_user.get_id()
        tryToFreeRoom(id_user)
        return jsonify(outcome="Freed",buildings=buildJsonList(getFreeBuildings()))
    else:
        tryToFreeRoom(current_user.get_id())
        return render_template('newselect.html', buildings=buildJsonList(getFreeBuildings()), msg='')


#TODO testing
@app.route("/userpage",methods=['GET','POST'])
@login_required
def userpage():
    content=request.headers.get("Content-ID")
    if content is None:
        content=""
    return handleLoggedinUser(content)

#TODO testing
@app.route("/updatecredentials", methods = ['POST','GET'])
@login_required
def updatecredentials():
    msg = ''
    outcome=False
    jobs = fetchJobs()
    content=request.headers.get("Content-ID")
    if request.method == 'POST':
        if 'password'in request.form and 'new_password' in request.form and 'new_password_confirm' in request.form:
            password = request.form['password']
            new_password = request.form['new_password']
            new_password_confirm = request.form['new_password_confirm']
            token=current_user.get_auth_token(current_user.username,current_user.password)
            print("new_passsword:" + str(new_password))
            print("new_password confirm:" + str(new_password_confirm))
            if current_user.new_password(password,new_password,new_password_confirm):
                msg = "Credenziali inserite con successo!"
                outcome= True
            else:
                msg = 'Credenziali inserite incorrettamente!'
            if content== "NEW-CREDENTIALS-APP":
                return {' outcome':outcome,'token':token, 'msg':msg}
            else:
                session["Auth-token"] = token
                return render_template('newcredentials.html', msg=msg, jobs=jobs)
        if content == "NEW-CREDENTIALS-APP":
            return {' outcome': outcome}
        else:
            return handleLoggedinUser("")
    else:
        return render_template('newcredentials.html', msg=msg, jobs=jobs)
#TODO testing
@app.route("/updateuserdata", methods = ['GET','POST'])
@login_required
def updateuserdata():
    msg = ''
    jobs = fetchJobs()
    content=request.headers.get("Content-ID")
    if request.method == 'POST':
        if 'birthday'in request.form and 'sex'in request.form and 'profession'in request.form:
            birthday=request.form['birthday']
            sex = request.form['sex']
            profession=request.form['profession']
            job = db.session.query(professions).filter_by(id_profession=profession).first()
            current_user.set_birthday(datetime.datetime.strptime(birthday,"%Y-%m-%d"))
            current_user.set_sex(sex)
            current_user.set_profession(job.name)
            if content == "USER-DATA-APP":
                return {'job':job.name,'sex':sex,'job_id':job.id_profession}
            else:
                return render_template('newuserdata.html', msg=msg, jobs=jobs,user=current_user)
        else:
            if content == "USER-DATA-APP":
                return {'outcome':False}
            else:
                return handleLoggedinUser("")
    else:
        return render_template('newuserdata.html', msg=msg, jobs=jobs, user=current_user)


########################################################################################################################
#TODO view che permette la registrazione all'Admin
#TODO controllo per consentire l'accesso solo all'admin

@app.route("/dashboardroom",methods=['POST','GET'])
@login_required
def dashboardroom():
    id_room = request.form['id_room']
    graphs=[]
    link="/admin/rooms"
    header="Dashboard della stanza con id:" + str(id_room)
    start_date = datetime.datetime.today() - datetime.timedelta(days = 30)
    session_states = db.session.query(sessionStates.id_session).filter_by(id_room=id_room).filter_by(active=False)
    sessions_to_plot = db.session.query(sessions.id).filter(
        sessions.id.in_(session_states)).filter(sessions.timestamp_end >= start_date)
    ##GRAFICO SENSORE DI LUCE
    graphs.append(buildRoomLightSensorGraph(id_room))
    #GRAFICO COLORI
    graphs.append(buildRoomColorGraph(sessions_to_plot))
    ##GRAFICO LUMINOSITA' LED
    graphs.append(buildRoomBrightnessGraph(sessions_to_plot))
    #GRAFICO TEMPERATURA
    graphs.append(buildRoomTemperatureGraph(sessions_to_plot))
    return render_template('dashboard.html', graphsJSON=graphs, header=header,link=link)

@app.route("/dashboardbuilding",methods=['POST','GET'])
@login_required
def dashboardbuilding():
    id_building = request.form['building_id']
    graphs=[]
    link = "/admin/buildings"
    header="Dashboard dell'edificio' con id:" + str(id_building)
    start_date = datetime.datetime.today() - datetime.timedelta(days = 30)
    rooms_of_building = db.session.query(rooms.id_building).filter_by(id_building=id_building)
    session_states = db.session.query(sessionStates.id_session).filter_by(active=False).filter(
        sessionStates.id_room.in_(rooms_of_building))
    sessions_to_plot = db.session.query(sessions.id).filter(
        sessions.id.in_(session_states)).filter(sessions.timestamp_end >= start_date)
    ##GRAFICO SENSORE DI LUCE
    graphs.append(buildBuildingLightSensorGraph(rooms_of_building))
    #GRAFICO COLORI
    graphs.append(buildRoomColorGraph(sessions_to_plot))
    ##GRAFICO LUMINOSITA' LED
    graphs.append(buildRoomBrightnessGraph(sessions_to_plot))
    #GRAFICO TEMPERATURA
    graphs.append(buildRoomTemperatureGraph(sessions_to_plot))
    return render_template('dashboard.html', graphsJSON=graphs, header=header,link=link)



@app.route("/dashboardzone",methods=['POST','GET'])
@login_required
def dashboardzone():
    id_zone = request.form['zone_id']
    graphs=[]
    link = "/admin/zones"
    header="Dashboard della zona con id:" + str(id_zone)
    id_buildings = db.session.query(zoneToBuildingAssociation.id_building).filter_by(id_zone=id_zone)
    start_date = datetime.datetime.today() - datetime.timedelta(days = 30)
    rooms_of_zone = db.session.query(rooms.id_room).filter(rooms.id_building.in_(id_buildings))
    session_states = db.session.query(sessionStates.id_session).filter_by(active=False).filter(
        sessionStates.id_room.in_(rooms_of_zone))
    sessions_to_plot = db.session.query(sessions.id).filter(
        sessions.id.in_(session_states)).filter(sessions.timestamp_end >= start_date)

    weatherReport_feed = db.session.query(weatherReport).filter_by(id_zone=id_zone) \
        .filter(weatherReport.timestamp >= start_date).order_by(weatherReport.timestamp.desc()).all()
    #GRAFICO TEMPERATURA METEO
    graphs.append(buildZoneWeatherGraph(weatherReport_feed))
    #GRAFICO UMIDITA'
    graphs.append(buildZoneWeatherHumidityGraph(weatherReport_feed))
    ##GRAFICO SENSORE DI LUCE
    graphs.append(buildBuildingLightSensorGraph(rooms_of_zone))
    #GRAFICO COLORI
    graphs.append(buildRoomColorGraph(sessions_to_plot))
    ##GRAFICO LUMINOSITA' LED
    graphs.append(buildRoomBrightnessGraph(sessions_to_plot))
    #GRAFICO TEMPERATURA
    graphs.append(buildRoomTemperatureGraph(sessions_to_plot))
    return render_template('dashboard.html', graphsJSON=graphs, header=header,link=link)
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd




<<<<<<< HEAD
#TODO metodi non ancora implementati
#TODO da vedere se lo implemento o meno, magari al resume session
def fetchLastSetting(id_session,digitalTwin):
    historyColor = db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action="color").order_by(actuatorFeeds.timestamp).first()
    historyBrightness=db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action="brightness").order_by(actuatorFeeds.timestamp).first()
    historyTemperature=db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action="temperature").order_by(actuatorFeeds.timestamp).first()
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD


#handle totale

#fa un redirect altrimenti lascia scorrere
#fa return 0 se passa i check
#per mobile controlliamo solo che è loggato e magari ripariamo i dati di sessione
#i dati di sessione utilizzati sono id_user loggedin, id_room e id_buidling non sono usati
#TODO testing
def handleLoggedinUser(content):
    id_room = tryToGetAssignedRoom(current_user.get_id())
    if id_room != -1:  # stanza già assegnata
        if content != "":
            return renderHomeApp(id_room)
        else:
            return renderHomeWeb(id_room)
    else:  # nessuna stanza assegnata
        if content != "":
            return renderSelectionApp()
        else:
            return renderSelectionWeb()

def handleAuthenticatedUserResponse(content,token):
    id_room = tryToGetAssignedRoom(current_user.get_id())
    if id_room != -1:  # stanza già assegnata
        if content == "LOGIN-APP":
            return renderHomeAppOnAuth(id_room, token)
        else:
            session["Auth-token"] = token
            return renderHomeWeb(id_room)
    else:  # nessuna stanza assegnata
        if content == "LOGIN-APP":
            return renderSelectionAppOnAuth(token)
        else:
            session["Auth-token"] = token
            return renderSelectionWeb()




#TODO testing
def handleViewPermission():
    if current_user.is_admin:
        return True
    else:
        return False
#TODO
def hasPermission(id_user):
    return False

=======
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
#testato
def StartListening():
    with app.app_context():
        fetchedRooms=rooms.query.all()
        for room in fetchedRooms:
            mqtt.subscribe('smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors/#')
            print("mi sono iscritto al topic "+'smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors')
    return 0
#testato
<<<<<<< HEAD

=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
#testato
def updateDigitalTwinActuators(id_user, color, brightness, temperature):
    actualSession=db.session.query(sessionStates).filter_by(id_user=id_user,active=True).first()
    IdRoomOfActualSession=actualSession.id_room
    IdBuildingOfActualRoom=db.session.query(rooms).filter_by(id_room=IdRoomOfActualSession).first().id_building
    IdSessionOfActualSession = actualSession.id_session
<<<<<<< HEAD
    timestamp=datetime.datetime.utcnow()
=======
    timestamp=datetime.utcnow()
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
    timestamp = datetime.datetime.utcnow()
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(digitalTwin.id_room) + '/status_request', "waiting",retain=True)
=======
    timestamp = datetime.utcnow()
    #ew
    #digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=digitalTwin.id_room).first()
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
    registerAction('color', led_color, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('brightness', brightness, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('temperature', temperature, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    return 0
#tested
def getAIdata(id_user,digitalTwin):
<<<<<<< HEAD
    account = db.session.query(User).filter_by(id=id_user).first()
    job = db.session.query(professions).filter_by(name=account.profession).first()
    weather_data = weather_report(digitalTwin.id_room)
    dataToSend = {'user_age': calculateUserAge(account.dateOfBirth), 'user_sex': account.sex - 1, 'user_task': job.category,
                  'ext_temp': weather_data["temperature"], 'ext_humidity': weather_data["humidity"],
=======
    account = db.session.query(accounts).filter_by(id=id_user).first()
    job = db.session.query(professions).filter_by(id_profession=account.profession).first()
    dataToSend = {'user_age': calculateUserAge(account.dateOfBirth), 'user_sex': account.sex, 'user_task': job.name,
                  'ext_temp': digitalTwin.temperature_sensor, 'ext_humidity': digitalTwin.humidity_sensor,
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
            dataFromServer = {'user_temp':21,'user_color':"RAINBOW",'user_light':'MEDIUM'}
    return dataFromServer



def renderHomeWeb(id_room):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    return render_template('index.html', digitalTwin=digitalTwin, username=current_user.get_username())

def renderHomeApp(id_room):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    id_building = db.session.query(rooms).filter_by(id_room=digitalTwin.id_room).first().id_building
    weather_data = weather_report(id_room)
    return jsonify(logged_in=True, outcome="Active", digitalTwin=digitalTwin.serializedActuators(),
                   id_edificio=id_building, id_room=id_room, username=current_user.get_username(),weather=weather_data)

def renderSelectionWeb():
    return render_template('newselect.html', buildings=buildJsonList(getFreeBuildings()), msg='')

def renderSelectionApp():
    return jsonify(logged_in=True, outcome="Login", username=current_user.get_username(),
                   buildings=buildJsonList(getFreeBuildings()))
def renderHomeAppOnAuth(id_room,token):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    id_building = db.session.query(rooms).filter_by(id_room=digitalTwin.id_room).first().id_building
    weather_data = weather_report(id_room)
    return jsonify(token=token, logged_in=True, outcome="Active", digitalTwin=digitalTwin.serializedActuators(),
                   id_edificio=id_building, id_room=digitalTwin.id_room, username=current_user.get_username(),weather=weather_data)

def renderSelectionAppOnAuth(token):
    return jsonify(token=token, logged_in=True, outcome="Login",username=current_user.get_username(),
                   buildings=buildJsonList(getFreeBuildings()))


#TODO testing
def hasRoomAssigned(id_user):
    actual_sessionState = db.session.query(sessionStates).filter_by(id_user=id_user,active=True).first()
    if actual_sessionState is not None:
        return True
    else:
        return False
=======
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


>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
            now = datetime.datetime.utcnow()
=======
            now = datetime.utcnow()
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
            return render_template('newselect.html', buildings=buildJsonList(getFreeBuildings()), msg=msg)
    elif data["outcome"] == -2: #stanza esistente
        if content=="SELECT-APP":
            return renderHomeApp(data["session_state"].id_room)
        else:
            return renderHomeWeb(data["session_state"].id_room)
    else:#stanza assegnata
        digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=data["session_state"].id_room).first()
        prepareRoom(id_user,data["session_state"].id_session,digitalTwin,building)
        if content=="SELECT-APP":
            return renderHomeApp(data["session_state"].id_room)
        else:
            return renderHomeWeb(data["session_state"].id_room)
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
#tested
def tryToGetAssignedRoom(id_user):
    actualSessions = db.session.query(sessionStates).filter_by(id_user=id_user, active=True).first()
    if actualSessions:
<<<<<<< HEAD
        #session["id_room"] = actualSessions.id_room
        #session["building"] = db.session.query(rooms).filter_by(id_room=actualSessions.id_room).first().id_building
=======
        session["id_room"] = actualSessions.id_room
        session["building"] = db.session.query(rooms).filter_by(id_room=actualSessions.id_room).first().id_building
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
        return actualSessions.id_room
    else:
        return -1  #sessione non esistente
#testato
def tryToFreeRoom(id_user):
    active_sessionState = db.session.query(sessionStates).filter_by(id_user=id_user, active=True).first()
    active_session=db.session.query(sessions).filter_by(id=active_sessionState.id_session).first()
    room = db.session.query(rooms).filter_by(id_room=active_sessionState.id_room).first()
<<<<<<< HEAD
    user = db.session.query(User).filter_by(id=id_user).first()
    now = datetime.datetime.utcnow()
=======
    user = db.session.query(accounts).filter_by(id=id_user).first()
    now = datetime.utcnow()
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
    active_sessionState.active=False
    active_session.timestamp_end=now
    db.session.commit()
    data=buildSessionData(user,room,active_session)
<<<<<<< HEAD
    setRoomToSleepMode(room.id_room,room.id_building)
    feedAIData(data)
    return 0

#TODO testing
def setRoomToSleepMode(id_room,id_building):
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/color', "NONE",retain=True)
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/brightness', 'LOW',retain=True)
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/temperature', 20,retain=True)
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/status_request', "closed",retain=True)
    digital_twin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    digital_twin.set_to_sleep_mode()
    return 0

=======
    feedAIData(data)
    return 0

>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
#testato
def buildSessionData(user,room,active_session):
    preValentTemperature = DataHistoryAccountFetch(active_session.id, "temperature")
    preValentColor = DataHistoryAccountFetch(active_session.id, "color")
    preValentBrightness = DataHistoryAccountFetch(active_session.id, "brightness")
    digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=room.id_room).first()
<<<<<<< HEAD
    job = db.session.query(professions).filter_by(name=user.profession).one().name
    age=calculateUserAge(user.dateOfBirth)
    weather_data = weather_report(id_room=room.id_room)
    data = {'user_age':age,'user_sex':user.sex,'user_task':job,'room_id':room.id_room,'building_id':room.id_building,
            'date':active_session.timestamp_begin.strftime("%Y/%m/%d"),
            'session_open_time':active_session.timestamp_begin.strftime("%H:%M:%S"),
            'session_close_time':active_session.timestamp_end.strftime("%H:%M:%S"),'ext_temp':weather_data["temperature"],
            'ext_humidity':weather_data["humidity"],'ext_light':digitalTwin.light_sensor,
            'user_temp': preValentTemperature, 'user_color': preValentColor, 'user_light': preValentBrightness}
    return data

#Testat0o
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
def DataHistoryAccountFetch(id_session,type):
    maxDuration=0
    maxValue=0
    timestamp_end = db.session.query(sessions).filter_by(id=id_session).one().timestamp_end
<<<<<<< HEAD
    actions=db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action=type).all()
=======
    actions=db.session.query(histories).filter_by(id_session=id_session,type_of_action=type).all()
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD

=======
#tested
def seconds_between(d1, d2):
    return abs((d2 - d1).total_seconds())
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd

#tested
def feedAIData(data):
    fb_app.post('/sessionHistory',data)
    return 0

#tested
def registerAction(type, value,session_id,timestamp,id_room,id_building,digitalTwin):
<<<<<<< HEAD
    db.session.add(actuatorFeeds(session_id, type, value, timestamp))
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuators/'+type, value,retain=True)
=======
    db.session.add(histories(session_id, type, value, timestamp))
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuators/'+type, value)
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
    print('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuators/'+type)
    if type=="temperature":
        digitalTwin.temperature_actuator = value
    elif type=="color":
        digitalTwin.led_actuator = value
    elif type=="brightness":
        digitalTwin.led_brightness = value
    db.session.commit()
    return 0

<<<<<<< HEAD



@app.after_request
def remove_if_invalid(response):
    if "__invalidate__" in session:
        response.delete_cookie(app.session_cookie_name)
    return response
=======
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




>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd



if __name__ =="__main__":
<<<<<<< HEAD
    #db.init_app(app)
    #mqtt.init_app(app)

    #with app.app_context():
        #db.session.add(weatherReport(1, 6, 70, datetime.datetime.utcnow()))
        #db.session.commit()
        #sensorFeedToCovert = db.session.query(sensorFeeds)
       # createRoomCSV(sensorFeedToCovert,"sensors",datetime.today(),"")
        #hashed_password = bcrypt.hashpw("18121996".encode("utf-8"), bcrypt.gensalt())
        #db.session.add(User(username="BArfaoui",password="password",profession=8,sex=1,dateOfBirth=datetime.datetime.utcnow().date()))
        #db.session.add(sensorFeeds(1,"light",1,datetime.datetime.utcnow()))
        #db.session.add(sensorFeeds(1, "light", 1, datetime.datetime.utcnow()))
        #db.session.add(sensorFeeds(1, "light", 1, datetime.datetime.utcnow()))
        #db.session.add(sensorFeeds(1, "light", 1, datetime.datetime.utcnow()))
        #db.session.commit()
    #geolog.isAddressValid("ajejebrazov")
    #geolog.geoMarker("Manzolino","Via Giovanni Acerbi","Italia")
=======
    db.init_app(app)
    mqtt.init_app(app)
    #with app.app_context():
     #   createAndPopulateDb()
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
#DONE snellire il codice dell'interpretazione dei dati mqtt
#DONE fixare i timestamp (UTC NOW) gli orari saranno in orario standard utc now
#DONE testare l'update snellito
#DONE Content-ID dell'header LOGIN-APP,REGISTER-APP,SELECT-APP,LOGOUT-APP
#done testare il sensorFeed, mentre il digitaltwinfeed terrà l'ultimo valore dei sensori e attuatori
#OBBIETTIVO 9 GENNAIO
#DONE testing gestione anonymous user (wrappare le view in @login_required oppure if current_user.is_authenticated:)
#DONE testing modelview
    #DONE testing grant permessi
    #DONE vedere se le categorie di profession sono giuste
    #DONE testing creazione,modifica,eliminazione jobs
    #DONE testing creazione,elimazione zone (id_zone non esiste)
    #DONE alla creazione/modifica della stanza, fare subscribe se la building è cambiata (dovrebbe iscriversi e disicriversi)
    #DONE testare alla creazione della stanza non viene aggiunto il digital twin
    #DONE testing stanze
    #DONE testing edifici
    #DONE testare aggiornato getFreeBuildings con l'available (dovrebbe funzionare comunque)
    #DONE testing impostare il formato dell'indirizzo in modo da evitare dati duplicati
    #Combinazione città indirizzo lat e lon  (Zone è univoco)
    #building è univoco per forza
    #DONE testare che tutti gli edifici sono univoci
    #DONE testare link per dashboard Zona, Palazzo e Stanza
    #DONE testare aggiungere un attributo "Available" a Palazzo e Stanza
    #DONE ISSUE guardo faccio grant dei permessi cambia professione (CASCADE)
#DONE permessi di visione solo a admin e super user, delle view/pagine dashboard e admin



#OBBIETTIVO 10 gennaio
    #DONE dashboard impostare il riconoscimento della richiesta edificio/stanza e id
        #DONE RICONOSCIMENTO DASHBOARD STANZA
        #DONE DASHBOARD STANZA
        #DONE PRENDERE DATI DEGLI ULTIMI 30 GIORNI
        #DONE SNELLIRE CODICE
        #DONE DASHBOARD EDIFICIO
    #DONE grafico attuatori istogramma per colore, ESCLUSO NONE
    #DONE grafico attuatore d'intensità della luce, linea + istogramma
    #DONE grafico temperatura
    #IDEA alla fine di ogni sessione prendendo i dati prevalenti della sessione e li mettiamo per il report (bho)
    #DONE scegliere la piattaforma
    #DONE meteo tramite lat e lon
    #DONE togliere humidity e temperature sensor


#OBBIETTIVO 13 GENNAIO
    #TODO COLLEGARE ADMIN E HOME CON LINK VISIBILI SOLO DALL'ADMIN (passiamo una boolean tipo admin=User.id_admin)
    #TODO mettere a posto il bottone della dashboard che ha come nome checkout payment ew
    #TODO trovare una soluzione per la homepage dell'admin (Magari un div di bottoni per azione che può fare selezione/home logout)
    #TODO sistemare view della dashboard
        #DONE Link che ritorna alla pagina precedente
        #TODO la grafica fa schifo lol
    #TODO SCHERMATA ADMIN impostare restrizioni di visione
    #CONSUMO DI UNA STANZA RISCALDATA WATT = AREA X ALTEZZA X 1,25
#TODO controllare valore sensori, solo int e niente strighe!
#TODO RISPARMIO ENERGETICO
    #TODO per evitare lunghi tempi di computazione creiamo report giornalieri
    #TODO GRAFICO CONSUMI
    #TODO route che fornisce il report di consumi
    #TODO script che calcola il consumo energetico ogni giorno
#TODO gestire status_respond (forse con i websocket e attributi current user, si può fare)
#TODO fixare le view
    # TODO togliere librerie inutilizzate
    # DONE fixare l'intensità del led perchè passo una stringa
    # TODO sistemare lo zoom nella mappa di selezione, magari la media delle zone
    # TODO gestione mancanza dati form (se serve)
    # TODO gestione expetions scrittura su db
    # TODO mettere un buon css
#CANCELED testing aggiornamento dati utente (include il compleanno utente)
#CANCELED (METTIAMO UN LINK)rerouting degli admin oppure creare una estensione delle pagine normali
#TODO testare il settaggio in risparmio energetico a fine sessione utente
#TODO commentare
#TODO impostare l'indirizzo per l'AI
#DONE testing ISSUE mandare la lista di edifici al freeroom
#DONE testing ISSUE colori led Stringa MQTT
#DONE ISSUE rimuovere noise sensor
#DONE testare Flask-login con credenziali e meccaniche di logout
    #DONE testare le redirect (al momento fa redirect alla home per quando non si è loggati)
    #DONE encrypt della registrazione/login
    #DONE togliere la session
    #DONE (Flask-Login e admin hanno comperto questo problema) creare metodo isLoggedin, che controlla se l'utente è loggato e se ha i permessi di accesso alla pagina
    #DONE testare error handler, che reindirizza alla pagina di login/index/selezione
    #DONE integrare Flask-Login
#DONE impostare la scelta dell'edificio tramite mappa
#DONE Testato le zone dinamiche e  il serialize
=======
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
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
#REPORT(Testing Login):
#Mostra gli edifici liberi correttamente
#Se una sessione è attiva lo porta in output
#Login funzionante
<<<<<<< HEAD
#REPORT (SelectRoom)



=======

#REPORT (SelectRoom)

>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
