# This is a sample Python script.
import configparser
import re
# Press Maiusc+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import sqlite3, flask_mqtt
from sqlite3 import Error
from flask import Flask, request, render_template, session, redirect, url_for
from flask_mqtt import Mqtt

import json
import paho.mqtt.client as mqtt
appname="IOT main"
app = Flask(appname)
app.secret_key = 'secretkey'
mqtt=Mqtt
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
            session['microcontr']= Microcontrollere.(,...,...)

            msg='Logged in!'
            return render_template('index.html',color=session['color'],username=session['username'])
        else:
            msg = 'Incorrect username / password !'
    return render_template('login.html',msg=msg)
@app.route('/logout',methods = ['GET','POST'])
def logout():
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
        # "CREATE TABLE 'accounts' (CF VARCHAR(16) PRIMARY KEY,username VARCHAR(20) NOT NULL,password VARCHAR(20) NOT NULL,color VARCHAR(20) NOT NULL,dateofbirth VARCHAR(20) NOT NULL);")

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
        #username=session['username']
        if color != session['color']:
            connection = sqlite3.connect('database.db')
            cursor=connection.cursor()
            cursor.execute('UPDATE accounts SET color=? WHERE username=?', (color, session['username']))
            connection.commit()
            session['color']=color
    return render_template('index.html',color=session['color'],username=session['username'])


class MQTTComm():
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.setupMQTT()


    def setupMQTT(self):
        self.clientMQTT = mqtt.Client()
        self.clientMQTT.on_connect = self.on_connect
        self.clientMQTT.on_message = self.on_message
        self.clientMQTT.username_pw_set(self.config.get("MQTT", "BrokerUsername", fallback="admin"),
                                        self.config.get("MQTT", "BrokerPassword", fallback="admin"))
        print("connecting to MQTT broker...")
        server = self.config.get("MQTT", "Server", fallback="localhost")
        port = self.config.getint("MQTT", "Port", fallback=1883)
        self.clientMQTT.connect(server, port, 60)
        self.clientMQTT.loop_start()


    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code " + str(rc))
        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.clientMQTT.subscribe("mylight")

    # The callback for when a PUBLISH message is received from the server.


    def on_message(self, client, userdata, msg):
        print(msg.topic + " " + str(msg.payload))
        if msg.topic == 'mylight':
            self.ser.write(msg.payload)

def create_connection():
    conn=None
    try:
        conn = sqlite3.connect('database.db')
        conn.execute("CREATE TABLE 'accounts' (CF VARCHAR(16) UNIQUE,username VARCHAR(20) NOT NULL PRIMARY KEY,password VARCHAR(20) NOT NULL,color VARCHAR(20) NOT NULL,dateofbirth VARCHAR(20) NOT NULL);")
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()
if __name__ =="__main__":
    port=8000
    interface='0.0.0.0'
    #create_connection()
    app.run(host=interface, port=port)
    #app.run() #ciclo bloccante che gestisce le richieste

#comando flask run
#servizio dns gratuito dns.net
#associa temporaneamente un ip temporaneo
