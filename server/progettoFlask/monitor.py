import datetime
import schedule
import sqlalchemy
import paho.mqtt.client as mqtt


#TODO TEST piano
#TODO Testare i 2 fix
#TODO Testare il last action
#TODO Testare il past actions nuovo
#DONE CALIBRAZIONE CONSUMI
#creaimo un insieme di dati di finte sessioni
#una volta fatto ciò creeremo delle dei casi e  vedere se funziona in modo giusto
#caso 1: tutto nella norma
#caso 2: over
#caso 3: tutto normale, ma in questo caso vedere come se la cava dopo aver preso provvedimenti
9#caso 4: over di nuovo
#caso 5: tutto nella norma
#caso 6: vedere se il reset è fatto bene
def on_connect(client, userdata, flags, rc):
    if rc == 0:

        print("Connected to broker")

        global Connected  # Use global variable
        Connected = True  # Signal connection

    else:

        print("Connection failed")
Connected = False

#Formula consumi (200 * (numero persone) + dimesioni stanza * 125)
AC_consumption=1500 #Espresso in watt fonte https://www.omnicalculator.com/construction/air-conditioner-room-size
                    #Ogni grado consumerà 3% - 5% in più cercare meglio
client = mqtt.Client()
client.on_connect= on_connect
client.connect("broker.hivemq.com",1883)
client.loop_start()
iterations = 0
room_size = 5 * 5 * 2.5
#number_of_rooms=1
#max_consumption_rate = 2000 * number_of_rooms #Scritto in w
#max_consumption = max_consumption_rate * 24  #Scritto in w
original_max=170000
consumption_leakage=0.03
reduction_constant=9.5
max_consumption = original_max
max_consumption_rate=max_consumption/24
time_constant=  1*60*2 #espresso in ore
timestamp_origin = datetime.datetime.utcnow()
begin_timestamp = timestamp_origin
end_timestamp = timestamp_origin
db=sqlalchemy.create_engine('sqlite:///instance/database.db') # ensure this is the correct path for the sqlite file.
db_report=sqlalchemy.create_engine('sqlite:///instance/monitor_database.db') # ensure this is the correct path for the sqlite file.


brightness_tuple = ('LOW','MEDIUM','HIGH')
ZONE_ID=1
ACTIVE_SESSION_REPORT=[]
weather_temperature=0
#db_report.execute("CREATE TABLE deltaT ( id_session  int, value int,PRIMARY KEY (id_session))")
#db_report.execute("CREATE TABLE active_session_report ( id_session  int)")
#db_report.execute("DROP TABLE active_session_report")
#db_report.execute("CREATE TABLE active_session_report ( id_session  int, id_room int, id_building int, temperature VARCHAR (20), light VARCHAR (20), PRIMARY KEY (id_session))")
#ogni 24 iterazioni la disponibilità viene resettata
def hour_count():
    global iterations
    global begin_timestamp
    global end_timestamp
    global max_consumption
    global max_consumption_rate
    global ZONE_ID
    global weather_temperature
    global number_of_rooms
    db_report.execute("DELETE FROM active_session_report")
    db_report.execute("DELETE FROM deltaT")
    hour_consumption = 0
    print("I'm working...")
    end_timestamp = datetime.datetime.utcnow() # calcolo ultimo istante da controllare
    weather_query= db.execute("SELECT temperature FROM weather_report WHERE ID_ZONE="+str(ZONE_ID)+
    " ORDER BY timestamp DESC").fetchone()
    number_of_rooms_query=fetchZoneNumberOfrooms().fetchone()
    if weather_query is not None and number_of_rooms_query is not None:
        #weather_temperature=int(float(weather_query[0]))
        weather_temperature=5
        if iterations == 0: #SETUP INIZIO ITERAZIONI
            '''print("Iterazione iniziale, ricalcolo...")
            number_of_rooms = int(float(number_of_rooms_query[0]))
            max_consumption_rate = 2500 * number_of_rooms
            max_consumption = max_consumption_rate * 24
            print("Max consumption iniziale:" + str(max_consumption))
            print("Max consumption rate iniziale:" + str(max_consumption_rate))'''
            max_consumption=original_max
            max_consumption_rate=max_consumption/24
        else:#AGGIORNAMENTO DATI PER ITERAZIONI
            '''print("ratio di consumo attuale:" + str(max_consumption_rate))
            print("max consumption attuale:"+str(max_consumption))
            print("Ricalcolo per l'iterazione "+str(iterations))
            old_number_of_rooms=number_of_rooms
            number_of_rooms = int(float(number_of_rooms_query[0]))
            print("numero stanze vecchie: "+str(old_number_of_rooms))
            print("numero stanze nuove: " + str(number_of_rooms))
            if old_number_of_rooms<number_of_rooms:
                #aggiorniamo il max
                rooms_to_add = number_of_rooms - old_number_of_rooms
                print("dobbiamo aggiungere " + str(rooms_to_add * (24 - iterations) * 2500) + " watt per le " + str(
                    rooms_to_add) + " stanze per le prossime " + str(24 - iterations) + " iterazioni")
                max_consumption = max_consumption + rooms_to_add * (24 - iterations)*2500
            elif old_number_of_rooms>number_of_rooms:
                # aggiorniamo il max
                rooms_to_remove=old_number_of_rooms-number_of_rooms
                print("dobbiamo togliere "+ str(rooms_to_remove * (24 - iterations)*max_consumption_rate)+" watt per le "+str(rooms_to_remove)+" stanze per le prossime "+str(24-iterations)+" iterazioni")
                max_consumption = max_consumption - rooms_to_remove * (24 - iterations)*max_consumption_rate'''
            max_consumption_rate = (max_consumption)/(24 - iterations)
        print("---INIZIO ITERAZIONE----------------------------------------------------------------------")
        print("#lavoro sulle sessioni accadute dalle ore " + str(begin_timestamp) + " a " + str(end_timestamp))
        print("#lavoro dall'ora:" + str(iterations) + "all'ora " + str(iterations + 1))
        print("#la temperatura nella zona è:"+str(weather_temperature))
        actuator_temperature_actions = fetchTemperatureActions().fetchall()
        actuator_brightness_actions = fetchBrightnessActions().fetchall()
        print("####################################Azioni all'interno del range#################################################")
        print(actuator_temperature_actions)
        print(actuator_brightness_actions)
        actuator_past_action = fetchPastActions().fetchall()
        print("###################################################Azioni di sessioni passate#####################################")
        print(actuator_past_action)
        print("##################################################################################################################")
        hour_consumption += calculate_past_query_consumption( actuator_past_action)
        hour_consumption += calculate_query_consumption(actuator_brightness_actions)
        hour_consumption += calculate_query_consumption(actuator_temperature_actions)
        print("-la consumazione totale in questa ora è :" + str(hour_consumption) + " watt!")
        max_consumption -= hour_consumption
        if max_consumption_rate < hour_consumption:
            print("***************************abbiamo consumato più del dovuto*********************")
            adjustConsumption(abs(max_consumption_rate-hour_consumption))

        if max_consumption < 0: #per coprire il caso di sforamento totale
            print("ALERT! ABBIAMO SFORATO IL CONSUMO MASSIMO GIORNALIERO!!!!")
            print("ALERT! ABBIAMO SFORATO IL CONSUMO MASSIMO GIORNALIERO!!!!")
            print("ALERT! ABBIAMO SFORATO IL CONSUMO MASSIMO GIORNALIERO!!!!")
            print("ALERT! ABBIAMO SFORATO IL CONSUMO MASSIMO GIORNALIERO!!!!")
            print("ALERT! ABBIAMO SFORATO IL CONSUMO MASSIMO GIORNALIERO!!!!")
            iterations=23
    db_report.execute("DELETE FROM active_session_report")
    db_report.execute("DELETE FROM deltaT")
    #FUORI DALL'IF
    #NON Interferisce con la max consumption
    if (iterations == 23): #RESET
            iterations = 0 #A inizio ciclo farà un reset
    else:#AGGIORNAMENTO
            iterations += 1
    begin_timestamp = end_timestamp  # calcolo l'inizio della prossima iterazione
    return 0

def calculate_query_consumption(actuator_actions):
    global begin_timestamp
    time_active = 0
    hour_consumption=0
    counter=0
    check_sessions_temp=[]
    check_sessions_bright=[]
    print("*********************************Calcolo di queste azioni*********************************************")
    print(actuator_actions)
    print("******************************************************************************************************")
    for row in actuator_actions:
        action_duration = 0
        active = bool(int(row[5]))
        id_session=row[0]
        type = row[1]
        value = row[2]
        timestamp_action = row[3]
        id_room=row[4]
        id_building=row[6]
        timestamp_end=row[7]
        if counter <(len(actuator_actions) -1) : #se non è l'ultimo elemento
            i = counter
            found=False
            while i < (len(actuator_actions) -1) and found == True:
                if id_session == actuator_actions[i+1][0]:
                        action_duration += hours_between(datetime.datetime.strptime(timestamp_action,'%Y-%m-%d %H:%M:%S.%f'),datetime.datetime.strptime(actuator_actions[i+1][3], '%Y-%m-%d %H:%M:%S.%f'))
                        found = True
                i+=1
            if found == False:
                if active is False:  # se la sessione è chiusa e non ha
                    action_duration += hours_between(
                        datetime.datetime.strptime(timestamp_action, '%Y-%m-%d %H:%M:%S.%f'),
                        datetime.datetime.strptime(timestamp_end, '%Y-%m-%d %H:%M:%S.%f'))
                else:
                    action_duration += hours_between(
                        datetime.datetime.strptime(timestamp_action, '%Y-%m-%d %H:%M:%S.%f'), end_timestamp)
        else:
            if active is False:#se la sessione è chiusa e non ha
                action_duration += hours_between(datetime.datetime.strptime(timestamp_action,'%Y-%m-%d %H:%M:%S.%f'), datetime.datetime.strptime(timestamp_end,'%Y-%m-%d %H:%M:%S.%f'))
            else:
                action_duration += hours_between(datetime.datetime.strptime(timestamp_action,'%Y-%m-%d %H:%M:%S.%f'), end_timestamp)
        if action_duration > 1:
            action_duration=1
        if type == "brightness":
            light_consumption =5 * (1 + brightness_tuple.index(value)) * action_duration
            hour_consumption += light_consumption
            time_active += action_duration
            if active:
                upsertSessionReport(id_session, id_room, id_building, 0, light_consumption)
            upsertConsumptionReport(id_building, id_room, datetime.datetime.strptime(timestamp_action,'%Y-%m-%d %H:%M:%S.%f'), 0, light_consumption)
            if id_session not in check_sessions_bright:
                #print(hours_between(datetime.datetime.strptime(timestamp_action, '%Y-%m-%d %H:%M:%S.%f'),begin_timestamp))
                if hours_between(datetime.datetime.strptime(timestamp_action,'%Y-%m-%d %H:%M:%S.%f'),begin_timestamp)>0:
                    hour_consumption+=fetchLastAction(int(id_session),timestamp_action,"brightness")
                check_sessions_bright.append(id_session)
        else:
            deltaT = weather_temperature-int(value)
            temperature_consumption = (1 + consumption_leakage * abs(deltaT)) * AC_consumption *  action_duration  # consumazione in ora giusto per vedere
            #print("La sessione ha consumato: "+ str(temperature_consumption))
            hour_consumption += temperature_consumption
            print("#La sessione "+ str(id_session) + " ha tenuto la temperatura " + str(value) + "per "+str(action_duration)+ "ore")
            if active:
                upsertSessionReport(id_session, id_room, id_building, temperature_consumption, 0)
                upsertDeltaT(id_session, deltaT)
            time_active+=action_duration
            upsertConsumptionReport(id_building, id_room, datetime.datetime.strptime(timestamp_action,'%Y-%m-%d %H:%M:%S.%f'), temperature_consumption, 0)
            if id_session not in check_sessions_temp:
                #print(hours_between(datetime.datetime.strptime(timestamp_action, '%Y-%m-%d %H:%M:%S.%f'),begin_timestamp))
                if hours_between(datetime.datetime.strptime(timestamp_action, '%Y-%m-%d %H:%M:%S.%f'),begin_timestamp) > 0:
                    hour_consumption+=fetchLastAction(int(id_session),timestamp_action,"temperature")
                check_sessions_temp.append(id_session)
        #print(counter)

        counter+=1
    print("Ore di attività totale è " + str(time_active) + " ORE")
    return hour_consumption
def calculate_past_query_consumption(actuator_actions):
    hour_consumption=0
    counter=0
    for row in actuator_actions:
        id_session=row[0]
        type=row[1]
        value=row[2]
        id_room= row[4]
        id_building=row[5]
        #id_session 0, type 1, value 2, timestamp 3,id_room 4,id_building 5
        #la durata viene contata dall'inizio del range alla fine del range
        if type == "brightness":
            print("*Sessione:" + str(id_session))
            print("*HA TENUTO LA LUCE "+str(value)+" PER 1 ORA")
            light_consumption = 5 * (1 + brightness_tuple.index(value))
            hour_consumption += light_consumption
            upsertSessionReport(id_session, id_room,id_building, 0, light_consumption)
            upsertConsumptionReport(id_building, id_room, begin_timestamp, 0, light_consumption)
        else:
            deltaT=weather_temperature - int(value)
            # temperature_consumption= abs(deltaT) * (1.204 * room_size) * 1.006 * action_duration #consumazione in ora giusto per vedere
            temperature_consumption = (1 + consumption_leakage * abs(deltaT)) * AC_consumption   # consumazione in ora giusto per vedere
            print("*Sessione:" + str(id_session))
            print("*La sessione ha tenuto la temperatura: " + str(value)+" per 1 ora")
            hour_consumption+=  temperature_consumption
            upsertSessionReport(id_session, id_room,id_building, temperature_consumption, 0)
            upsertConsumptionReport(id_building, id_room, begin_timestamp, temperature_consumption, 0)
            upsertDeltaT(id_session, deltaT)
        counter+=1
    return hour_consumption
def upsertConsumptionReport(id_building,id_room, timestamp, temperature, light):
    month=str(timestamp.date().strftime("%Y-%m"))
    day=str(timestamp.date().strftime("%Y-%m-%d"))
    db.execute("INSERT INTO dailyBuildingconsumptionReport (id_building, timestamp,temperature, light)"
               " VALUES(" + str(id_building) + ", '" + day + "', "
               + str(temperature) + ","+str(light)+" ) ON CONFLICT(id_building,timestamp) DO UPDATE SET   temperature=temperature+" + str(temperature) +
               ", light=light+"+str(light))
    db.execute("INSERT INTO dailyRoomconsumptionReport (id_room, timestamp,temperature, light)"
               " VALUES(" + str(id_room) + ", '" + day + "', "
               + str(temperature) + ","+str(light)+" ) ON CONFLICT(id_room,timestamp) DO UPDATE SET   temperature=temperature+" + str(temperature) +
               ", light=light+"+str(light))
    db.execute("INSERT INTO monthlyBuildingconsumptionReport (id_building, timestamp,temperature, light)"
               " VALUES(" + str(id_building) + ", '" + month + "-28', "
               + str(temperature) + ","+str(light)+" ) ON CONFLICT(id_building,timestamp) DO UPDATE SET   temperature=temperature+" + str(temperature) +
               ", light=light+"+str(light))
    db.execute("INSERT INTO monthlyRoomconsumptionReport (id_room, timestamp,temperature, light)"
               " VALUES(" + str(id_room) + ", '" + month + "-28', "
               + str(temperature) + ","+str(light)+" ) ON CONFLICT(id_room,timestamp) DO UPDATE SET   temperature=temperature+" + str(temperature) +
               ", light=light+"+str(light))
    return 0
def upsertSessionReport(id_session, id_room, id_building, temperature, light):
    db_report.execute("INSERT INTO active_session_report (id_session , id_room , id_building, temperature, light)"
               " VALUES("+str(id_session)+ ", "+ str(id_room) + ", " + str(id_building) + ","
               + str(temperature)+", "+str(light)+") ON CONFLICT(id_session) DO UPDATE SET   temperature=temperature+" + str(temperature)
               +", light=light+"+str(light))
    return 0
def upsertDeltaT(id_session,deltaT):
    db_report.execute("INSERT INTO deltaT (id_session , value ) VALUES(" + str(id_session) + ", " + str(deltaT) + ") "
                      " ON CONFLICT(id_session) DO UPDATE SET   value=" + str(deltaT))
    return 0
def hours_between(d1, d2):
    return abs((d2 - d1).total_seconds()/(60*60))*time_constant
def insertNewAction(id_session,id_room,id_building, timestamp,type,value):
    client.publish('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/' + type,
                   value, retain=True)
    print("Ho scitto in mqtt")
    print('smartoffice/building_' + str(id_building) + '/room_' + str(id_room) + '/actuators/' + type)
    db.execute("INSERT INTO actuator_feeds (ID_SESSION, type_of_action,	value,	timestamp)"
                      " VALUES(" + str(id_session) + ", '" + str(type) + "', '" + str(value) + "','"
                      + str(timestamp) + "')")
    if type == "brightness":
        db.execute("UPDATE digital_twin_feed SET led_brightness='"+str(value)+"' WHERE ID_ROOM="+str(id_room))
    else:
        db.execute("UPDATE digital_twin_feed SET temperature_actuator='"+str(value)+"' WHERE ID_ROOM="+str(id_room))
    return 0
def fetchBrightnessActions():
    return  db.execute('select '
    'actuator_feeds.ID_SESSION, actuator_feeds.type_of_action, actuator_feeds.value, actuator_feeds.timestamp,'
    'session_states.ID_ROOM, session_states.active AS active,rooms.id_building,'
    'sessions.timestamp_end '
    'from actuator_feeds '
    'join session_states ON (actuator_feeds.id_session = session_states.id_session) '
    'join rooms ON (session_states.id_room = rooms.id_room)'
    'join sessions ON (sessions.id_session = actuator_feeds.id_session AND sessions.id_session=session_states.id_session)'
    'join zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
    'where (actuator_feeds.timestamp BETWEEN "'+str(begin_timestamp)+'" AND "'+str(end_timestamp)+'")'
    'AND zone_to_building_association.id_zone='+str(ZONE_ID)+' '
    'AND actuator_feeds.type_of_action!="color" AND actuator_feeds.type_of_action!="temperature"')


def fetchTemperatureActions():
    return  db.execute('select '
    'actuator_feeds.ID_SESSION, actuator_feeds.type_of_action, actuator_feeds.value, actuator_feeds.timestamp,'
    'session_states.ID_ROOM, session_states.active AS active,rooms.id_building,'
    'sessions.timestamp_end '
    'from actuator_feeds '
    'join session_states ON (actuator_feeds.id_session = session_states.id_session) '
    'join rooms ON (session_states.id_room = rooms.id_room)'
    'join sessions ON (sessions.id_session = actuator_feeds.id_session AND sessions.id_session=session_states.id_session)'
    'join zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
    'where (actuator_feeds.timestamp BETWEEN "'+str(begin_timestamp)+'" AND "'+str(end_timestamp)+'")'
    'AND zone_to_building_association.id_zone='+str(ZONE_ID)+' '
    'AND actuator_feeds.type_of_action!="color" AND actuator_feeds.type_of_action!="brightness"')



def fetchPastActions():#se fai un azione nel range non prende il resto
                       #al momento dovrebbe essere safe se cambi colore nel range
    return db.execute('select session_states.id_session, type_of_action, value, MAX(timestamp) as timestamp,'
     'rooms.id_room,rooms.id_building'
     ' FROM  actuator_feeds join session_states ON (session_states.id_session=actuator_feeds.id_session)'
     ' JOIN rooms ON (rooms.id_room=session_states.id_room)' 
     ' JOIN zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'                                                 
     ' WHERE timestamp <"' + str(begin_timestamp) + '" AND active=TRUE AND actuator_feeds.type_of_action!="color"'
     ' AND session_states.id_session NOT IN (SELECT id_session '
     ' FROM actuator_feeds WHERE type_of_action!="color" AND timestamp BETWEEN "'+str(begin_timestamp)+'" AND "'+str(end_timestamp)+'")'
     ' AND zone_to_building_association.id_zone='+str(ZONE_ID)+' '
     ' GROUP BY session_states.id_session,type_of_action')


def fetchZoneNumberOfrooms():
    return db.execute(" SELECT COUNT(*) FROM rooms WHERE id_building IN "
                      "(SELECT zone_to_building_association.id_building FROM zone_to_building_association "
                      " JOIN  buildings ON (zone_to_building_association.id_building = buildings.id_building)"
                      " WHERE id_zone="+str(ZONE_ID)+" AND  available=True) AND  available=True")
def adjustConsumption(over_consumption):
    print("#Abbiamo sforato di "+str(over_consumption))
    consumption_session_reports=db_report.execute("SELECT * FROM active_session_report").fetchall()
    deltaTs=db_report.execute("SELECT * FROM deltaT").fetchall()
    number_of_sessions= len(consumption_session_reports)
    for row in consumption_session_reports:
        id_building=int(row[2])
        id_room=int(row[1])
        id_session = int(row[0])
        temp_consumption=float(row[3])
        light_consumption=float(row[4])
        consumption_factor=1/number_of_sessions
        #consumption_factor=(temp_consumption+light_consumption)/total_active_sessions_consumption
        print("##############################CALCOLO SESSIONE: "+str(id_session)+" #######################################àà")
        print("#Il fattore di consumazione della sessione è "+str(consumption_factor*100)+"%")
        consumption_reduction=over_consumption * consumption_factor
        print("#dobbiamo ridurre i consumi della sessione di "+str(consumption_reduction)+" watt")
        light_intensity=int(round(light_consumption/5))
        timestamp_invertion=datetime.datetime.utcnow()
        print("#L'intensità media del LED è " + brightness_tuple[light_intensity - 1 ])
        if  (light_intensity - 1) > 0:
            consumption_reduction-= (5 * (light_intensity) -5)
            print("#abbiamo ridotto il consumo del LED di "+str(5 * (light_intensity) -5)+ " watt")
            insertNewAction(id_session,id_room,id_building, timestamp_invertion, "brightness",brightness_tuple[round(int((5 * (light_intensity) -5)/5))])
        if round(consumption_reduction) > 0: #per vedere se ha ancora da ridurre
            deltaT=0
            new_room_temp = 0
            for line in deltaTs:
                if int(line[0]) == id_session:
                    deltaT=float(line[1])
            room_temp = weather_temperature - deltaT
            real_consumption_reduction=temp_consumption-consumption_reduction
            new_room_temp=(real_consumption_reduction/AC_consumption -1 + 0.03*weather_temperature)/0.03
            #denominator=AC_consumption*(deltaT*consumption_leakage + 1)
           # new_DeltaT = round((consumption_reduction /denominator)*reduction_constant)
            '''print("#Temperatura precendente della sessione: "+str(room_temp))
            print("#New_Delta "+str(new_DeltaT))
            print("#Vecchio deltaT "+str(deltaT))
            if deltaT > 0:#fuori è più freddo
                print("#Alziamo la temperatura")
                #riduco la temperatura (RAFFREDAMENTO)
                new_room_temp = room_temp + new_DeltaT
            else:#fuori è più caldo,
                print("#Abbassiamo la temperatura")
                #aumento la temperatura (RISCALDAMENTO)
                new_room_temp = room_temp - new_DeltaT'''

            if new_room_temp < 17:
                new_room_temp=17
            elif new_room_temp >30:
                new_room_temp=30
            print("#Nuova temperatura della sessione sarà:" + str(new_room_temp))
            if int(new_room_temp) != int(room_temp):
                insertNewAction(id_session,id_room,id_building, timestamp_invertion, "temperature", int(new_room_temp))
def fetchLastAction(id_session,timestamp,type):

    if type == "temperature":
        query = db.execute(' select session_states.id_session, type_of_action, value, MAX(timestamp) as timestamp'
                      ' FROM  actuator_feeds join session_states ON (session_states.id_session=actuator_feeds.id_session) '
                      ' JOIN rooms ON (rooms.id_room=session_states.id_room)'
                      ' JOIN zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
                      ' WHERE timestamp <"' + str(begin_timestamp) + '" AND actuator_feeds.type_of_action!="color" AND actuator_feeds.type_of_action!="brightness"'
                      ' AND session_states.id_session='+str(id_session)+
                      ' AND zone_to_building_association.id_zone=' + str(ZONE_ID) +
                      ' GROUP BY session_states.id_session,type_of_action').fetchone()
        if query is not None:
            print("#Azione trovata")
            print(query)
            temperature = int(query[2])
            action_duration = hours_between(datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S.%f'),begin_timestamp)
            deltaT = weather_temperature - int(temperature)
            print("#La temperatura della sessione è:" + str(temperature))
            print("#deltaT della sessione:" + str(deltaT))
            temperature_consumption = (1 + consumption_leakage * abs(deltaT)) * AC_consumption * action_duration  # consumazione in ora giusto per vedere
            print("#Ho consumato dall'inizio:"+str(temperature_consumption) + "per: "+str(action_duration) +" ore")
            return temperature_consumption
            #Calcolo
        return 0
    if type == "brightness":
        query = db.execute('select session_states.id_session, type_of_action, value, MAX(timestamp) as timestamp'
                      ' FROM  actuator_feeds join session_states ON (session_states.id_session=actuator_feeds.id_session)'
                      ' JOIN rooms ON (rooms.id_room=session_states.id_room)'
                      ' JOIN zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
                      ' WHERE timestamp <"' + str(begin_timestamp) + '" AND actuator_feeds.type_of_action!="color" AND actuator_feeds.type_of_action!="temperature"'
                      ' AND session_states.id_session='+str(id_session)+
                      ' AND zone_to_building_association.id_zone=' + str(ZONE_ID) +
                      ' GROUP BY session_states.id_session,type_of_action').fetchone()
        if query is not None:
            print("#Azione trovata")
            print(query)
            brightness = query[2]
            action_duration = hours_between(datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f'),
                                            begin_timestamp)
            # vecchia formula
            # temperature_consumption= abs(deltaT) * (1.204 * room_size) * 1.006 * action_duration #consumazione in ora giusto per vedere
            light_consumption = 5 * (1 + brightness_tuple.index(brightness)) * action_duration
            print("#Ho consumato dall'inizio:"+str(light_consumption) + "per: "+str(action_duration) +" ore")
            return light_consumption
        return 0







schedule.every(30).seconds.do(hour_count)

#schedule.every(60/time_constant).minutes.do(hour_count)
while True:
    schedule.run_pending()








