# This is a sample Python script.
import configparser
import datetime
import re
import sqlite3
from sqlite3 import Error, connect

import requests as requests
from flask import Flask, request, render_template, session, redirect, url_for
from flask_mqtt import Mqtt
from flask_socketio import SocketIO

import paho.mqtt.client as mqtt
appname="IOT main"
app = Flask(appname)
app.secret_key = 'secretkey'
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
        connection = sqlite3.connect('database.db')
        username = request.form['username']
        password = request.form['password']
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username =? AND password=?',(username,password))
        connection.commit()
        account = cursor.fetchall()
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
            mqtt.publish('provatopic',session['username']+" ha loggato!")
            mqtt.subscribe(session['username']+'movimento')
            msg='Logged in!'
            return render_template('index.html',color=session['color'],username=session['username'],pippo=1)
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html',msg=msg)
@app.route('/logout',methods = ['GET','POST'])
def logout():
    mqtt.unsubscribe(session['username']+'movimento')
    session.pop('loggedin', None)
    session.pop('username', None)
    return redirect(url_for('login'))

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


def create_connection():
    conn=None
    try:
        conn = sqlite3.connect('database.db')
        conn.execute("CREATE TABLE 'accounts' (CF VARCHAR(16) UNIQUE,username VARCHAR(20) NOT NULL PRIMARY KEY,password VARCHAR(20) NOT NULL,color VARCHAR(20) NOT NULL,dateofbirth VARCHAR(20) NOT NULL);")
        conn.execute("CREATE TABLE 'sessions' (ID_ROOM VARCHAR(16),username VARCHAR(20),active BOOLEAN, timestamp_begin VARCHAR(20), timestamp_end VARCHAR(20));")
        conn.execute("CREATE TABLE 'rooms' (ID_ROOM INTEGER PRIMARY KEY, ID_BUILDING INTEGER);")
        conn.execute("CREATE TABLE 'buildings' (ID_BUILDING INTEGER PRIMARY KEY);")
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
if __name__ =="__main__":
    port=5000
    interface='0.0.0.0'
    #create_connection()

    app.run(host=interface, port=port)
    #mqtt.init_app(app)
    #app.run() #ciclo bloccante che gestisce le richieste





#tabella sessioni
#timestamp username edificio stanza expired