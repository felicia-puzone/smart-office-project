import datetime
import os
import pathlib
import re
from pathlib import Path

from flask_admin.contrib import sqla
from flask_admin.model.template import ViewRowAction, EditRowAction
from itsdangerous import BadSignature
from sqlalchemy import extract
from werkzeug.routing import ValidationError
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt as bcrypt
import requests as requests
import werkzeug
from flask import Flask, request, render_template, session,jsonify
from werkzeug.exceptions import HTTPException
from wtforms import StringField, IntegerField, SelectField, PasswordField, Form
from wtforms.utils import unset_value
from apphandler import app
import geolog
from models import db, digitalTwinFeed, sessions, sessionStates, rooms, professions, actuatorFeeds, buildings, \
    sensorFeeds, zones, User, serializer, serializer_secret
#from flask_mqtt import Mqtt
from flask_cors import CORS
#import paho.mqtt.client as mqtt
from firebase import firebase
from mqtthandler import mqtt
from modelviews import MyHomeView, ZoneAdmin, UserAdmin, JobAdmin, BuildingAdmin, RoomAdmin
from queries import fetchJobs, getFreeBuildings, createAndPopulateDb
from utilities import buildJsonList, calculateUserAge, createABuildingtupleList, createAProfessiontupleList, seconds_between
from flask_admin import Admin, AdminIndexView
from flask_admin import BaseView, expose
from flask_login import current_user, LoginManager, login_user, logout_user, login_required,UserMixin

from flask import Flask, jsonify, make_response, request
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from functools import wraps







login_manager = LoginManager()
login_manager.init_app(app)
#mqtt=Mqtt()
fb_app = firebase.FirebaseApplication('https://smartoffice-4eb51-default-rtdb.europe-west1.firebasedatabase.app/', None)
#admin = Admin(app, name='Dashboard')
db.init_app(app)
mqtt.init_app(app)
#with app.app_context():
    #createAndPopulateDb()
months = ('January','February','March','April','May','June',\
'July','August','September','October','November','December')
colors = ('NONE','RED','ORANGE','YELLOW','GREEN','TEAL','BLUE','INDIGO','VIOLET','RAINBOW')

admin = Admin(app, name='Dashboard',index_view=MyHomeView())
#admin.add_view(MyView(name='My View', menu_icon_type='glyph', menu_icon_value='glyphicon-home'))
admin.add_view(ZoneAdmin(zones, db.session,category='Models'))
admin.add_view(BuildingAdmin(buildings, db.session,category='Models'))
admin.add_view(RoomAdmin(rooms, db.session,category='Models'))
admin.add_view(JobAdmin(professions, db.session,category='Models'))
admin.add_view(UserAdmin(User, db.session,category='Models'))

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
            print(birthday)
            sex = request.form['sex']
            profession=request.form['profession']
            account=db.session.query(User).filter_by(username=username).first()
            job = db.session.query(professions).filter_by(id_profession=profession).first()
            if account:
                msg = 'Utente esistente!'
            if job is None:
                msg = 'Professione non esistente!'
            elif not re.match(r'[A-Za-z0-9]+',username):
                msg='L\'username deve solo contenere lettere e numeri!'
            elif len(password)<8:
                msg = 'inserire almeno 8 caratteri nella password!'
            elif not username or not password:
                msg='Riempire i campi obbligatori!'
            else:
                #hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
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
        brightness = int(request.form['brightness'])
        temperature = int(request.form['temperature'])
        digitalTwin=updateDigitalTwinActuators(id_user, color, brightness, temperature)
        return render_template('index.html',digitalTwin=digitalTwin,username=current_user.get_username())

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

@app.route("/dashboard",methods=['GET','POST'])
@login_required
def dashboard():
    #handleViewPermission(current_user.get_id())
    return "<p>ciao</p>"

@app.route("/buildingDashboard")
@login_required
def building():
    if not handleViewPermission(current_user.get_id()):
        return handleLoggedinUser("")
    #permission=handleViewPermission(True)
    #if permission!=0:
     #   return permission
    return "ciao"
@login_required
@app.route("/buildingregistration")
def buildingregistration():
    if not handleViewPermission(current_user.get_id()):
        return handleLoggedinUser("")
    return "ciao"
@login_required
@app.route("/digitalTwin")
def digitalTwin():
    if not handleViewPermission(current_user.get_id()):
        return handleLoggedinUser("")
    return "ciao"
@login_required
@app.route("/modify")
def modify():
    if not handleViewPermission(current_user.get_id()):
        return handleLoggedinUser("")
    return "ciao"





#TODO metodi non ancora implementati
#TODO da vedere se lo implemento o meno, magari al resume session
def fetchLastSetting(id_session,digitalTwin):
    historyColor = db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action="color").order_by(actuatorFeeds.timestamp).first()
    historyBrightness=db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action="brightness").order_by(actuatorFeeds.timestamp).first()
    historyTemperature=db.session.query(actuatorFeeds).filter_by(id_session=id_session,type_of_action="temperature").order_by(actuatorFeeds.timestamp).first()
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
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(digitalTwin.id_room) + '/status_request', "waiting")
    registerAction('color', led_color, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('brightness', brightness, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    registerAction('temperature', temperature, id_session, timestamp, digitalTwin.id_room, id_building, digitalTwin)
    return 0
#tested
def getAIdata(id_user,digitalTwin):
    account = db.session.query(User).filter_by(id=id_user).first()
    job = db.session.query(professions).filter_by(name=account.profession).first()
    dataToSend = {'user_age': calculateUserAge(account.dateOfBirth), 'user_sex': account.sex - 1, 'user_task': job.category,
                  'ext_temp': 0, 'ext_humidity': 0,
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
            dataFromServer = {'user_temp':21,'user_color':"RAINBOW",'user_light':1}
    return dataFromServer



def renderHomeWeb(id_room):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    return render_template('index.html', digitalTwin=digitalTwin, username=current_user.get_username())

def renderHomeApp(id_room):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    id_building = db.session.query(rooms).filter_by(id_room=digitalTwin.id_room).first().id_building
    return jsonify(logged_in=True, outcome="Active", digitalTwin=digitalTwin.serializedActuators(),
                   id_edificio=id_building, id_room=id_room, username=current_user.get_username())

def renderSelectionWeb():
    return render_template('newselect.html', buildings=buildJsonList(getFreeBuildings()), msg='')

def renderSelectionApp():
    return jsonify(logged_in=True, outcome="Login", username=current_user.get_username(),
                   buildings=buildJsonList(getFreeBuildings()))
def renderHomeAppOnAuth(id_room,token):
    digitalTwin = db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
    id_building = db.session.query(rooms).filter_by(id_room=digitalTwin.id_room).first().id_building
    return jsonify(token=token, logged_in=True, outcome="Active", digitalTwin=digitalTwin.serializedActuators(),
                   id_edificio=id_building, id_room=digitalTwin.id_room, username=current_user.get_username())

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

#TODO testing
def setRoomToSleepMode(id_room,id_building):
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/color', "NONE")
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/brightness', 0)
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/temperature', 20)
    mqtt.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/status_request', "closed")
    return 0

#testato
def buildSessionData(user,room,active_session):
    preValentTemperature = DataHistoryAccountFetch(active_session.id, "temperature")
    preValentColor = DataHistoryAccountFetch(active_session.id, "color")
    preValentBrightness = DataHistoryAccountFetch(active_session.id, "brightness")
    digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=room.id_room).first()
    job = db.session.query(professions).filter_by(name=user.profession).one().name
    age=calculateUserAge(user.dateOfBirth)
    data = {'user_age':age,'user_sex':user.sex,'user_task':job,'room_id':room.id_room,'building_id':room.id_building,
            'date':active_session.timestamp_begin.strftime("%Y/%m/%d"),
            'session_open_time':active_session.timestamp_begin.strftime("%H:%M:%S"),
            'session_close_time':active_session.timestamp_end.strftime("%H:%M:%S"),'ext_temp':digitalTwin.temperature_sensor,
            'ext_humidity':digitalTwin.humidity_sensor,'ext_light':digitalTwin.light_sensor,
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




@app.after_request
def remove_if_invalid(response):
    if "__invalidate__" in session:
        response.delete_cookie(app.session_cookie_name)
    return response



if __name__ =="__main__":
    #db.init_app(app)
    #mqtt.init_app(app)

    #with app.app_context():
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
    geolog.geoMarker("Manzolino","Via Giovanni Acerbi","Italia")
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
    #TODO dashboard impostare il riconoscimento della richiesta edificio/stanza e id
    #TODO idee per il sensore di luminosità giornaliero(ogni ora o mezz'ora),mensile(ogni giorno) e settimanale(ogni mezza giornata)
    #TODO grafico attuatori istogramma per colore, ESCLUSO NONE
    #TODO grafico attuatore d'intensità della luce, linea + istogramma
    #TODO grafico temperatura
    #IDEA alla fine di ogni sessione prendendo i dati prevalenti della sessione e li mettiamo per il report (bho)
    #TODO per evitare lunghi tempi di computazione creiamo report giornalieri
    #TODO impostare restrizioni di visione
    #TODO scegliere la piattaforma
    #TODO meteo tramite lat e lon
    #TODO togliere humidity e temperature sensor
#TODO gestire status_respond (forse con i websocket e attributi current user, si può fare)
#TODO fixare le view
    # TODO sistemare lo zoom nella mappa di selezione, magari la media delle zone
    # TODO gestione mancanza dati form (se serve)
    # TODO gestione expetions scrittura su db
    # TODO mettere un buon css
#TODO testing aggiornamento dati utente (include il compleanno utente)
#TODO rerouting degli admin oppure creare una estensione delle pagine normali
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
#REPORT(Testing Login):
#Mostra gli edifici liberi correttamente
#Se una sessione è attiva lo porta in output
#Login funzionante
#REPORT (SelectRoom)



