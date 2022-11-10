# This is a sample Python script.
import configparser
import datetime
import re
import sqlite3
from sqlite3 import Error, connect

import requests as requests
from flask import Flask, request, render_template, session, redirect, url_for, jsonify
from flask_mqtt import Mqtt
from flask_socketio import SocketIO
from flask_cors import CORS
import paho.mqtt.client as mqtt

appname="IOT main"
app = Flask(appname)
app.secret_key = 'secretkey'
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MQTT_BROKER_URL'] = 'ilvero.davidepalma.it'  # use the free broker from HIVEMQ
app.config['MQTT_BROKER_PORT'] = 80  # default port for non-tls connection
app.config['MQTT_USERNAME'] = 'uni'  # set the username here if you need authentication for the broker
app.config['MQTT_PASSWORD'] = 'more'  # set the password here if the broker demands authentication
app.config['MQTT_KEEPALIVE'] = 5  # set the time interval for sending a ping to the broker to 5 seconds
app.config['MQTT_TLS_ENABLED'] = False  # set TLS to disabled for testing purposes
mqtt=Mqtt(app)
socketio=SocketIO(app)
@mqtt.on_connect()
def handle_connect(client,userdata,flags,rc):
    mqtt.subscribe('provatopic')
    mqtt.publish('provatopic','ciao sono l\'app Flask di Billi')
    print("buenos dias!")
@mqtt.on_message()
def handle_message_mqtt(client,userdata,message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Received message on topic: {topic} with payload: {payload}'.format(**data))
@app.route("/") #percorsi url locali
@app.route('/login',methods = ['GET','POST'])
#le risposte saranno sempre stringhe
def login():
    msg=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = checkCredentials(username, password)
        if account:
            session['loggedin'] = True
            session['username'] = account[0][1]
            session['color'] = account[0][3]
            #richiesta post a un AI fittizia, per ora messa a commento
            #URL = "http://127.0.0.1:8000/query"
            #PARAMS = {'age': 25}
            #r = requests.post(url=URL, params=PARAMS)
            #print(r.text)
            #session['microcontr']= Microcontrollere.(,...,...)
            #mqtt.publish('provatopic',session['username']+" ha loggato!")
            #mqtt.subscribe(session['username']+'movimento')
            msg='Logged in!'
            return render_template('index.html',color=session['color'],username=session['username'])
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html',msg=msg)
@app.route("/loginapp",methods = ['GET', 'POST'])
def loginapp():
    msg = ''
    content=''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = checkCredentials(username, password)
        if account:
            session['loggedin'] = True
            session['username'] = account[0][1]
            session['color'] = account[0][3]
            # richiesta post a un AI fittizia, per ora messa a commento
            # URL = "http://127.0.0.1:8000/query"
            # PARAMS = {'age': 25}
            # r = requests.post(url=URL, params=PARAMS)
            # print(r.text)
            # session['microcontr']= Microcontrollere.(,...,...)
            # mqtt.publish('provatopic',session['username']+" ha loggato!")
            #mqtt.subscribe(session['username'] + 'movimento')
            msg = 'Logged in!'
            content=jsonify(loggedin=session['loggedin'],username=session['username'],color=session['color'],msg=msg)
            #return app.response_class(response=content,status=200,mimetype='application/json')
            #return render_template('index.html', color=session['color'], username=session['username'])
        else:
            msg = 'Incorrect username / password !'
            content=jsonify(loggedin=False,msg=msg)
        return content
        #return app.response_class(response=content,status=200,mimetype='application/json')
    #content=jsonify(application="sus")
    #return content
    #return app.response_class(response=content, status=200, mimetype='application/json')

#richieste logout per pc e app android
@app.route('/logout',methods = ['GET','POST'])
def logout():
    mqtt.unsubscribe(session['username']+'movimento')
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/logoutapp',methods=['GET','POST'])
def logoutapp():
    mqtt.unsubscribe(session['username'] + 'movimento')
    session.pop('loggedin', None)
    session.pop('username', None)
    return jsonify(loggedin="false",msg="logged out safely!")

#richieste che gestiscono la registrazione
@app.route("/register", methods = ['GET','POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        connection=sqlite3.connect('database.db')
        username = request.form['username']
        password = request.form['password']
        CF=request.form['CF']
        Color=request.form['color']
        Birthday=request.form['birthday']

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username =?',(username,))
        connection.commit()
        account=cursor.fetchall()
        cursor.execute('SELECT * FROM accounts WHERE CF =?',(CF,))
        connection.commit()
        cf=cursor.fetchall()
        if account:
            msg = 'Utente esistente!'
        elif cf:
            msg = 'Codice fiscale già associato ad un altro utente!'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg='L\'username deve solo contenere lettere e numeri!'
        elif len(CF)!=16 or not re.match(r'[A-Za-z0-9]+',CF):
            msg = 'Codice fiscale non inserito correttamente!'
        elif len(password)<8:
            msg = 'inserire almeno 8 caratteri nella password!'
        elif not username or not password:
            msg='Riempire i campi obbligatori!'
        else:
            cursor.execute('INSERT INTO accounts (CF,username,password,color,dateofbirth) VALUES( ?, ?,?,?,?)',(CF,username,password,Color,Birthday))
            connection.commit()
            msg = 'Ti sei registrato con successo!'
    elif request.method == 'POST':
        msg = 'Riempire i campi obbligatori!'
    return render_template('register.html',msg=msg)
@app.route("/registerapp", methods = ['GET','POST'])
def registerapp():
    msg = ''
    signedUp=False
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        connection=sqlite3.connect('database.db')
        username = request.form['username']
        password = request.form['password']
        CF=request.form['CF']
        Color=request.form['color']
        Birthday=request.form['birthday']

        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username =?',(username,))
        connection.commit()
        account=cursor.fetchall()
        cursor.execute('SELECT * FROM accounts WHERE CF =?',(CF,))
        connection.commit()
        cf=cursor.fetchall()
        if account:
            msg = 'Utente esistente!'
        elif cf:
            msg = 'Codice fiscale già associato ad un altro utente!'
        elif not re.match(r'[A-Za-z0-9]+',username):
            msg='L\'username deve solo contenere lettere e numeri!'
        elif len(CF)!=16 or not re.match(r'[A-Za-z0-9]+',CF):
            msg = 'Codice fiscale non inserito correttamente!'
        elif len(password)<8:
            msg = 'inserire almeno 8 caratteri nella password!'
        elif not username or not password:
            msg='Riempire i campi obbligatori!'
        else:
            cursor.execute('INSERT INTO accounts (CF,username,password,color,dateofbirth) VALUES( ?, ?,?,?,?)',(CF,username,password,Color,Birthday))
            connection.commit()
            signedUp=True
            msg = 'Ti sei registrato con successo!'
    elif request.method == 'POST':
        msg = 'Riempire i campi obbligatori!'
    return jsonify(signedUp=signedUp,msg=msg)
@app.route("/update",  methods = ['GET','POST'])
def update():
    if request.method == 'POST':
        color=request.form['color']
        if color != session['color']:
            connection = sqlite3.connect('database.db')
            cursor=connection.cursor()
            cursor.execute('UPDATE accounts SET color=? WHERE username=?', (color, session['username']))
            connection.commit()
            session['color']=color
            mqtt.publish('provatopic',session['username'] + " ha cambiato il colore del LED a " + session['color'])
    return render_template('index.html',color=session['color'],username=session['username'])
@app.route("/updateapp",methods=['GET','POST'])
def updateApp():
    if request.method == 'POST' and session.get('logged_in'):
        color=request.form['color']
        if color != session['color']:
            connection = sqlite3.connect('database.db')
            cursor=connection.cursor()
            cursor.execute('UPDATE accounts SET color=? WHERE username=?', (color, session['username']))
            connection.commit()
            session['color']=color
            mqtt.publish('provatopic',session['username'] + " ha cambiato il colore del LED a " + session['color'])
            content=jsonify(color=session['color'],username=session['username'])
            return content

    #return render_template('index.html',color=session['color'],username=session['username'])
#funzione che crea il database
#nota per il futuro: magari salvare i dati in un file di testo per
#popolare il database in modo efficiente


#app error handlers


def create_db():
    conn=None
    try:
        conn = sqlite3.connect('database.db')
        conn.execute("CREATE TABLE 'accounts' (CF VARCHAR(16) UNIQUE,username VARCHAR(20) NOT NULL PRIMARY KEY,password VARCHAR(20) NOT NULL,color VARCHAR(20) NOT NULL,dateofbirth VARCHAR(20) NOT NULL);")
        conn.execute("CREATE TABLE 'sessions' (ID_ROOM VARCHAR(16),username VARCHAR(20),active BOOLEAN, timestamp_begin VARCHAR(20), timestamp_end VARCHAR(20));")
        conn.execute("CREATE TABLE 'rooms' (ID_ROOM INTEGER PRIMARY KEY, ID_BUILDING INTEGER);")
        conn.execute("CREATE TABLE 'buildings' (ID_BUILDING INTEGER PRIMARY KEY);")
        #tabella storico LED timestamp colore id_account numero da 1 a 3
        #tabella luoghi ID LUOGO NOME LUOGO
        #tabella professioni ID PROFESSIONE NOME SETTORE
        #tabella per digital twin
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
#codice generalizzato per il controllo di credenziali
#così non ripetiamo codice
def checkCredentials(username, password):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM accounts WHERE username =? AND password=?', (username, password))
    connection.commit()
    account = cursor.fetchall()
    return account


#funzione che assegna una stanza a un account che ne ha fatto richiesta
#sepcificando l'edificio
#output previsti:
# return -1 se non ci sono stanze disponibili
# return -2 se ha già una sessione attiva
# return id della stanza assegnata
def assignRoom(username,building):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM sessions WHERE username =? AND EXPIRED=FALSE', (username,))
    connection.commit()
    sessions = cursor.fetchall()
    if sessions:
        return -2 #sessione esistente
    else:
        #cerco le stanze libere
        cursor.execute('SELECT * FROM rooms WHERE ID_ROOM NOT IN (SELECT ID_ROOM FROM sessions WHERE EXPIRED=FALSE) AND ID_BUILDING=?',(building,))
        room=cursor.fetchone() #prenderà sempre la prima stanza disponibile
        if room:
             return room[1] #return id_room
        #return -1
    return -1 # nessuna camera disponibile

#fornisce le condizioni delle stanze tramite nella forma
# del digital twin
def DigitalTwinDisplay():
    return 0
#funzione che permette di ricavare lo storico delle azioni
#di un account
def DataHistoryAccountFetch():
    return 0
#funzione che fornisce dati all'AI
def feedAIData():
    return 0

#health check del microcontrollore
#vede se è sincronizzato con il digital twin oppure se ha problemi tecnici
#
def roomHealthCheck():
    return 0
#chiede all'AI il colore del led e la temperatura, per poi mandare
#i dati al microcontrollore tramite MQTT che è in ascolto al topic stanza
def prepareRoomOnLogin():
    #send account data and room location
    #for heat and led data
    return 0
#funzione che permette di cambiare colore al led tramite APP
#manda istruzione tramite MQTT, salva lo storico e aggiorna il digital twin
def changeLEDColor():
    return 0
#metodo che manda un messaggio al bot telegram
def botTelegramAlert():
    return 0
#oggetto che rappresenta il digital twin della stanza
class RoomDigitalTwin:
    #variabili di classe
    def __init__(self,color,temperature,idRoom,idBuilding):
        #attributi
        self.ledColor='Blue'
        self.temperatureHeathSystem=0
        self.idRoom=0
        self.idBuilding=0
        self.Brightness=0
        self.status='Healthy'
        self.occupied=True
        self.ProximitySensor=0
        self.TemperatureSensor=0
        self.LightSensor=0
    def __init__(self, idroom):
        print(idroom)
        #pensato come costruttore se al momento non si ha niente in mano
    def setLedColor(self,color):
        self.ledColor=color
    def getLedColor(self):
        return self.ledColor
#obj_name.var_name
#Audi.model
#obj_name.method_name()
#Audi.ShowModel();
#obj_name.method_name(parameter_list)
#Audi.ShowModel(100);
class AccountDigitalTwin:
    def __init__(self,username):
        self.username="barfaoui"
        self.job=2
if __name__ =="__main__":
    port=5000
    interface='0.0.0.0'
    #create_connection()

    app.run(host=interface, port=port)
    #mqtt.init_app(app)
    #app.run() #ciclo bloccante che gestisce le richieste





#tabella sessioni
#timestamp username edificio stanza expired