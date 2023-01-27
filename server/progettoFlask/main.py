import datetime
import re
from itsdangerous import BadSignature
import requests as requests
from flask import  render_template, session, json
from werkzeug.exceptions import HTTPException
from apphandler import app
from models import db, digitalTwinFeed, sessions, sessionStates, rooms, professions, actuatorFeeds, buildings, \
    zones, User, serializer, serializer_secret, weatherReport, zoneToBuildingAssociation, telegram
from firebase import firebase
from mqtthandler import mqtt
from modelviews import ZoneAdmin, UserAdmin, JobAdmin, BuildingAdmin, RoomAdmin, MyHomeView, TelegramAdmin
from queries import fetchJobs, getFreeBuildings, createAndPopulateDb, buildRoomLightSensorGraph, buildRoomColorGraph, \
    buildRoomBrightnessGraph, buildRoomTemperatureGraph, buildBuildingLightSensorGraph, buildZoneWeatherGraph, \
    buildZoneWeatherHumidityGraph, buildRoomDailyConsumptionReport, buildRoomMonthlyConsumptionReport, \
    buildBuildingDailyConsumptionReport, buildBuildingMonthlyConsumptionReport, buildZoneDailyConsumptionReport, \
    buildZoneMonthlyConsumptionReport, fetchMontlhyReport
from utilities import buildJsonList, calculateUserAge, \
    seconds_between, colors, brightness_values
from flask_admin import Admin
from flask_login import current_user, LoginManager, login_user, logout_user, login_required
from flask import  jsonify, request
from weather import weather_report

login_manager = LoginManager()
login_manager.init_app(app)
fb_app = firebase.FirebaseApplication('https://smartoffice-4eb51-default-rtdb.europe-west1.firebasedatabase.app/', None)
db.init_app(app)
mqtt.init_app(app)
'''with app.app_context():
    createAndPopulateDb()'''

admin = Admin(app, name='Spazio Admin',index_view=MyHomeView())
admin.add_view(ZoneAdmin(zones, db.session))
admin.add_view(BuildingAdmin(buildings, db.session))
admin.add_view(RoomAdmin(rooms, db.session))
admin.add_view(JobAdmin(professions, db.session))
admin.add_view(UserAdmin(User, db.session))
admin.add_view(TelegramAdmin(telegram, db.session))
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







@app.route("/") #percorsi url locali
def homepage():
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
@login_required
def logout():
    content=request.headers.get("Content-ID")
    logout_user()
    if content == "Logout-APP":
        return jsonify(loggedout=True)
    else:
        session.pop("Auth-token")
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
            birthday= request.form['birthday']
            sex = request.form['sex']
            profession=request.form['profession']
            account=db.session.query(User).filter_by(username=username).first()
            job = db.session.query(professions).filter_by(id_profession=profession).first()
            if account:
                msg = 'Utente esistente!'
            elif job is None:
                msg = 'Professione non esistente!'
            elif not re.match(r'[A-Za-z0-9]+',username):
                msg='L\'username deve solo contenere lettere e numeri!'
            elif len(password)<8:
                msg = 'inserire almeno 8 caratteri nella password!'
            elif not username or not password:
                msg='Riempire i campi obbligatori!'
            else:
                #hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
                if (datetime.datetime.utcnow()-datetime.datetime.strptime(birthday,"%Y-%m-%d")).days/365.25 < 18:
                    birthday=datetime.datetime.utcnow() - datetime.timedelta(days=(18*366))
                    account = User(username=username,password=password,profession=job.name,sex=sex,dateOfBirth=birthday)
                else:
                    account = User(username=username,password=password,profession=job.name,sex=sex,dateOfBirth=datetime.datetime.strptime(birthday,"%Y-%m-%d"))
                db.session.add(account)
                db.session.commit()
                msg = 'Ti sei registrato con successo!'
                signedUp=True
        else:
            msg = 'Riempire i campi obbligatori!'
        if content == "REGISTER-APP":
            return jsonify(signedUp=signedUp,msg=msg)
        else:
            return render_template('register.html', msg=msg, jobs=jobs)
    else:
        if content == "REGISTER-APP":
            jobs = buildJsonList(jobs)
            return jsonify(jobs=jobs)
        else:
            return render_template('register.html', msg=msg, jobs=jobs)
######################################################################################################################
#testato

@app.route("/update",  methods = ['POST'])
@login_required
def update():
    content=request.headers.get("Content-ID")
    if content == "UPDATE-APP":
        data=request.get_json(silent=True)
        id_user = current_user.get_id()
        color=data['color_val']
        brightness=data['brightness_val']
        temperature=data['temp_val']
        digitalTwin=updateDigitalTwinActuators(id_user,color,brightness,temperature)
        return jsonify(changes=True,digitalTwin=digitalTwin.serializedActuators())
    else:
        id_user = current_user.get_id()
        color = colors[int(request.form['color'])]
        brightness = brightness_values[int(request.form['brightness'])]
        temperature = int(request.form['temperature'])
        digitalTwin=updateDigitalTwinActuators(id_user, color, brightness, temperature)
        return render_template('index.html',digitalTwin=digitalTwin,username=current_user.get_username(),admin=int(current_user.is_admin()))

#testato

@app.route("/selectRoom",methods = ['POST'])
@login_required
def occupyRoom():
    content=request.headers.get("Content-ID")
    #id_room=-1
    id_user=0
    building=0
    if content == "SELECT-APP":
        data = request.get_json(silent=True)
        id_user = current_user.get_id()
        building = data['building_id']
    else:
        #prendo dati dal form e sessione
        building = request.form['building']
        id_user=current_user.get_id()
        #id_room = tryToAssignRoom(session['id_user'], building)
    return handleRoomAssignment(id_user,content,building)




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
        return render_template('newselect.html', buildings=buildJsonList(getFreeBuildings()), msg='',admin=int(current_user.is_admin()))





@app.route("/dashboardroom",methods=['POST'])
@login_required
def dashboardroom():
    if not handleViewPermission():
        print("current user is not Admin")
        return handleLoggedinUser("")
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
    # GRAFICO CONSUMI
    graphs.append(buildRoomDailyConsumptionReport(id_room))
    graphs.append(buildRoomMonthlyConsumptionReport(id_room))
    return render_template('dashboard.html', graphsJSON=graphs, header=header,link=link)

@app.route("/dashboardbuilding",methods=['POST'])
@login_required
def dashboardbuilding():
    if not handleViewPermission():
        print("current user is not Admin")
        return handleLoggedinUser("")
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
    # GRAFICO CONSUMI
    graphs.append(buildBuildingDailyConsumptionReport(id_building))
    graphs.append(buildBuildingMonthlyConsumptionReport(id_building))
    return render_template('dashboard.html', graphsJSON=graphs, header=header,link=link)



@app.route("/dashboardzone",methods=['POST'])
@login_required
def dashboardzone():
    if not handleViewPermission():
        print("current user is not Admin")
        return handleLoggedinUser("")
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
    # GRAFICO CONSUMI
    graphs.append(buildZoneDailyConsumptionReport(id_buildings))
    graphs.append(buildZoneMonthlyConsumptionReport(id_buildings))
    return render_template('dashboard.html', graphsJSON=graphs, header=header,link=link)


@app.route('/botAuth', methods=['POST'])
def auth():
    key = request.json['key']
    key_check = db.session.query(telegram).filter_by(telegram_key=key).first()
    if key_check is not None:
        return jsonify({'status': 'AUTHENTICATED'})
    else:
        return jsonify({'status': 'NOT-AUTHENTICATED'})


@app.route('/botReport', methods=['GET'])
def report():
    return jsonify({'report': fetchMontlhyReport()})
#################################################################################


#handle totale

#fa un redirect altrimenti lascia scorrere
#fa return 0 se passa i check
#per mobile controlliamo solo che è loggato e magari ripariamo i dati di sessione
#i dati di sessione utilizzati sono id_user loggedin, id_room e id_buidling non sono usati
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





def handleViewPermission():
    return current_user.is_admin()


#testato
def StartListening():
    with app.app_context():
        fetchedRooms=rooms.query.all()
        for room in fetchedRooms:
            mqtt.subscribe('smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors/#')
            print("mi sono iscritto al topic "+'smartoffice/building_'+str(+room.id_building)+'/room_'+str(room.id_room)+'/sensors')
    return 0
#testato

#testato
def updateDigitalTwinActuators(id_user, color, brightness, temperature):
    actualSession=db.session.query(sessionStates).filter_by(id_user=id_user,active=True).first()
    IdRoomOfActualSession=actualSession.id_room
    IdBuildingOfActualRoom=db.session.query(rooms).filter_by(id_room=IdRoomOfActualSession).first().id_building
    IdSessionOfActualSession = actualSession.id_session
    timestamp=datetime.datetime.utcnow()
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
    timestamp = datetime.datetime.utcnow()
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(digitalTwin.id_room) + '/status_request', "waiting",retain=True)
    registerAction('color', led_color, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('brightness', brightness, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('temperature', temperature, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    return 0
#tested
def getAIdata(id_user,digitalTwin):
    account = db.session.query(User).filter_by(id=id_user).first()
    job = db.session.query(professions).filter_by(name=account.profession).first()
    weather_data = weather_report(digitalTwin.id_room)
    external_light=0
    if digitalTwin.light_sensor <250:
        external_light = 3
    elif digitalTwin.light_sensor < 500:
        external_light = 2
    elif digitalTwin.light_sensor < 750:
        external_light = 1
    user_age=calculateUserAge(account.dateOfBirth)
    if user_age < 18:
        user_age = 18
    dataToSend = {'user_age': user_age, 'user_sex': account.sex - 1, 'user_task': job.category,
                  'ext_temp': weather_data["temperature"], 'ext_humidity': weather_data["humidity"],
                  'ext_light': external_light}
    try:
        res_temp = requests.post('http://54.86.207.49:5000/getUserTemp/',data=json.dumps(dataToSend))
        res_brightness = requests.post('http://54.86.207.49:5000/getUserLight/', data=json.dumps(dataToSend))
        res_color = requests.post('http://54.86.207.49:5000/getUserColor/', data=json.dumps(dataToSend))
        print('response from server:', res_temp.text)
        print('response from server:', res_brightness.text)
        print('response from server:', res_color.text)
        dataFromServer = {'user_temp':int(res_temp.text),'user_color':colors[int(res_color.text)],'user_light':brightness_values[int(res_brightness.text)]}
    except requests.exceptions.RequestException as e:
        print("c'è stato un errore! Prenderò i dati dall'AI locale!")
        try:
            res = requests.post('http://localhost:5001/AI', json=dataToSend)
            print('response from server:', res.text)
            dataFromServer = res.json()
            print(dataFromServer)
        except requests.exceptions.RequestException as e:
            print("c'è stato un errore! Prenderò dati di Default!")
            default_temp=17
            if int (float(weather_data['temperature']))>30:
                default_temp=30
            elif int (float(weather_data['temperature'])) > 17:
                default_temp = int(float(weather_data['temperature']))
            dataFromServer = {'user_temp':default_temp,'user_color':"RAINBOW",'user_light':'MEDIUM'}
    return dataFromServer



def renderHomeWeb(id_room):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    return render_template('index.html', digitalTwin=digitalTwin, username=current_user.get_username(),admin=int(current_user.is_admin()))

def renderHomeApp(id_room):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    id_building = db.session.query(rooms).filter_by(id_room=digitalTwin.id_room).first().id_building
    weather_data = weather_report(id_room)
    return jsonify(logged_in=True, outcome="Active", digitalTwin=digitalTwin.serializedActuators(),
                   id_edificio=id_building, id_room=id_room, username=current_user.get_username(),weather=weather_data)

def renderSelectionWeb():
    return render_template('newselect.html', buildings=buildJsonList(getFreeBuildings()), msg='',admin=int(current_user.is_admin()))

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



def hasRoomAssigned(id_user):
    actual_sessionState = db.session.query(sessionStates).filter_by(id_user=id_user,active=True).first()
    if actual_sessionState is not None:
        return True
    else:
        return False
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
            now = datetime.datetime.utcnow()
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
            return render_template('newselect.html', buildings=buildJsonList(getFreeBuildings()), msg=msg,admin=int(current_user.is_admin()))
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
#tested
def tryToGetAssignedRoom(id_user):
    actualSessions = db.session.query(sessionStates).filter_by(id_user=id_user, active=True).first()
    if actualSessions:
        #session["id_room"] = actualSessions.id_room
        #session["building"] = db.session.query(rooms).filter_by(id_room=actualSessions.id_room).first().id_building
        return actualSessions.id_room
    else:
        return -1  #sessione non esistente
#testato
def tryToFreeRoom(id_user):
    active_sessionState = db.session.query(sessionStates).filter_by(id_user=id_user, active=True).first()
    active_session=db.session.query(sessions).filter_by(id=active_sessionState.id_session).first()
    room = db.session.query(rooms).filter_by(id_room=active_sessionState.id_room).first()
    user = db.session.query(User).filter_by(id=id_user).first()
    now = datetime.datetime.utcnow()
    active_sessionState.active=False
    active_session.timestamp_end=now
    db.session.commit()
    data=buildSessionData(user,room,active_session)
    setRoomToSleepMode(room.id_room,room.id_building)
    feedAIData(data)
    return 0

def setRoomToSleepMode(id_room,id_building):
    #weather_data = weather_report(id_room)
    #mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/temperature', round(int(float(weather_data['temperature']))),retain=True)
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/status_request', "closed",retain=True)
    digital_twin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    #digital_twin.set_to_sleep_mode(round(int(float(weather_data['temperature']))))
    return 0

#testato
def buildSessionData(user,room,active_session):
    preValentTemperature = DataHistoryAccountFetch(active_session.id, "temperature")
    preValentColor = DataHistoryAccountFetch(active_session.id, "color")
    preValentBrightness = DataHistoryAccountFetch(active_session.id, "brightness")
    digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=room.id_room).first()
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
def DataHistoryAccountFetch(id_session,type):
    maxDuration=0
    maxValue=0
    timestamp_end = db.session.query(sessions).filter_by(id=id_session).one().timestamp_end
    actions=db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action=type).all()
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
def feedAIData(data):
    fb_app.post('/sessionHistory',data)
    return 0

#tested
def registerAction(type, value,session_id,timestamp,id_room,id_building,digitalTwin):
    db.session.add(actuatorFeeds(session_id, type, value, timestamp))
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuators/'+type, value,retain=True)
    print('smartoffice/building_' + str(id_building) + '/room_'+str(id_room)+'/actuators/'+type)
    if type=="temperature":
        digitalTwin.temperature_actuator = value
    elif type=="color":
        digitalTwin.led_actuator = value
    elif type=="brightness":
        digitalTwin.led_brightness = value
    db.session.commit()
    return 0








if __name__ =="__main__":
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
    #DONE COLLEGARE ADMIN E HOME CON LINK VISIBILI SOLO DALL'ADMIN (passiamo una boolean tipo admin=User.id_admin)
    #DONE mettere a posto il bottone della dashboard che ha come nome checkout payment ew
        #DONE Link che ritorna alla pagina precedente
    #DONE SCHERMATA ADMIN impostare restrizioni di visione
    #CONSUMO DI UNA STANZA RISCALDATA WATT = AREA X ALTEZZA X 1,25
#DONE controllare valore sensori, solo int e niente strighe!



#TODO RISPARMIO ENERGETICO
    #DONE fixare bug monitor (non era un bug, ma un errore della costante di tempo)
    #TODO stress test del monitor
    #TODO test bot telegram
    #TODO test report telegram
    #TODO vedere se la prima action è lontana dall'inizio
    #DONE per evitare lunghi tempi di computazione creiamo report giornalieri
    #DONE GRAFICO CONSUMI
    #DONE testare se la dashoard è funzionante
    #DONE calibrare la dashboard
    #DONE route che fornisce il report di consumi
    #DONE script che calcola il consumo energetico ogni giorno
    #DONE scrive azione e manda messaggio mqtt
# DONE fixare l'intensità del led perchè passo una stringa
#TODO verificare che i topic mqtt corrispondono
#TODO fixare le view
    # TODO togliere librerie inutilizzate
    # TODO sistemare lo zoom nella mappa di selezione, magari la media delle zone
    # TODO gestione mancanza dati form (se serve)
    # TODO mettere un buon css
    #TODO trovare una soluzione per la homepage dell'admin (Magari un div di bottoni per azione che può fare selezione/home logout)
    #TODO sistemare view della dashboard
# TODO commentare
#DONE AI locale impostare un If else
#DONE dati default, la temperatura la mettiamo vicino a quella d'ambiente
#DONE COMUNICAZIONE CON L'AI
    #DONE IMPOSTARE ETA' MINIMA A 18 ANNI
    #DONE IMPOSTARE LE RICHIESTE
    #DONE testare le richieste
#DONE testare il settaggio in risparmio energetico a fine sessione utente
#DONE gestire status_respond (forse con i websocket e attributi current user, si può fare)
#CANCELED testing aggiornamento dati utente (include il compleanno utente)
#CANCELED (METTIAMO UN LINK)rerouting degli admin oppure creare una estensione delle pagine normali
#DONE impostare l'indirizzo per l'AI
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
#REPORT(Testing Login):
#Mostra gli edifici liberi correttamente
#Se una sessione è attiva lo porta in output
#Login funzionante
#REPORT (SelectRoom)



