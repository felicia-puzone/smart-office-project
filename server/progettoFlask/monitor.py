import datetime

import schedule
import sqlalchemy
import pandas as pd

iterations = 0
room_size = 5 * 5 * 2.5
max_consumption = 240000 #Scritto in kw
max_consumption_rate = 10000 #Scritto in kw
timestamp_origin = datetime.datetime.utcnow()
begin_timestamp = timestamp_origin - datetime.timedelta(hours=1)
end_timestamp = timestamp_origin
db=sqlalchemy.create_engine('sqlite:///instance/database.db') # ensure this is the correct path for the sqlite file.
brightness_tuple = ('LOW','MEDIUM','HIGH')
zones=[]
#ogni 24 iterazioni la disponibilità viene resettata
def hour_count():
    global iterations
    global begin_timestamp
    global end_timestamp
    global max_consumption
    global max_consumption_rate
    hour_consumption = 0

    actions_to_send = [('id_stanza','azione','ammontare')] #azioni da mandare
    end_timestamp = datetime.datetime.utcnow() # calcolo ultimo istante da controllare
    #print(hours_between(begin_timestamp, end_timestamp))
    print("I'm working...")
    print("lavoro sulle sessioni accadute dalle ore "+ str(begin_timestamp)+ " a "+ str(end_timestamp))
    print("lavoro dall'ora:"+str(iterations)+ "all'ora "+str(iterations + 1) )
    actuator_temperature_actions =  pd.read_sql('select '
    'actuator_feeds.ID_SESSION, actuator_feeds.type_of_action, actuator_feeds.value, actuator_feeds.timestamp,'
    'session_states.ID_ROOM, session_states.active AS active,rooms.id_building,zone_to_building_association.id_zone,temperature AS weather_temp,'
    'sessions.timestamp_end '
    'from actuator_feeds '
    'join session_states ON (actuator_feeds.id_session = session_states.id_session) '
    'join rooms ON (session_states.id_room = rooms.id_room)'
    'join sessions ON (sessions.id_session = actuator_feeds.id_session AND sessions.id_session=session_states.id_session)'
    'join zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
    'JOIN (SELECT id_zone,temperature, MAX(timestamp) FROM weather_report GROUP BY id_zone) x ON (x.id_zone = zone_to_building_association.id_zone)'
    'where (actuator_feeds.timestamp BETWEEN "'+str(begin_timestamp)+'" AND "'+str(end_timestamp)+'")'
    'AND actuator_feeds.type_of_action!="brightness" AND actuator_feeds.type_of_action!="color"',db)



    actuator_brightness_actions = pd.read_sql('select '
    'actuator_feeds.ID_SESSION, actuator_feeds.type_of_action, actuator_feeds.value, actuator_feeds.timestamp,'
    'session_states.ID_ROOM, session_states.active,rooms.id_building,zone_to_building_association.id_zone,sessions.timestamp_end '
    'from actuator_feeds '
    'join session_states ON (actuator_feeds.id_session = session_states.id_session) '
    'join rooms ON (session_states.id_room = rooms.id_room)'
    'join sessions ON (sessions.id_session = actuator_feeds.id_session AND sessions.id_session=session_states.id_session)'
    'join zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
    'where (actuator_feeds.timestamp BETWEEN "' + str(begin_timestamp) + '" AND "' + str(end_timestamp) + '")'
    'AND actuator_feeds.type_of_action="brightness"',db)


    #ultime azioni delle sessioni attive che non hanno fatto niente in questo range temporaneo
    actuator_posterior_temperature_action = pd.read_sql('select session_states.id_session, type_of_action, value, MAX(timestamp) as timestamp,'
     ' temperature as weather_temp,rooms.id_room,rooms.id_building,zone_to_building_association.id_zone '
     ' FROM  actuator_feeds join session_states ON (session_states.id_session=actuator_feeds.id_session)'
     ' JOIN rooms ON (rooms.id_room=session_states.id_room)' 
     ' JOIN zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
     ' JOIN (SELECT id_zone,temperature, MAX(timestamp) FROM weather_report GROUP BY id_zone) x ON (x.id_zone = zone_to_building_association.id_zone)'                                                   
     ' WHERE timestamp <"' + str(begin_timestamp) + '" AND active=TRUE AND actuator_feeds.type_of_action!="brightness" AND actuator_feeds.type_of_action!="color"'
     ' AND session_states.id_session NOT IN (SELECT id_session FROM actuator_feeds WHERE timestamp BETWEEN "'+str(begin_timestamp)+'" AND "'+str(end_timestamp)+'")'
     ' GROUP BY session_states.id_session,type_of_action',db)

    actuator_posterior_brightness_action = pd.read_sql(
        'select session_states.id_session, type_of_action, value, MAX(timestamp) as timestamp,'
        'rooms.id_room,rooms.id_building,zone_to_building_association.id_zone '
        ' FROM  actuator_feeds join session_states ON (session_states.id_session=actuator_feeds.id_session)'
        ' JOIN rooms ON (rooms.id_room=session_states.id_room)'
        ' JOIN zone_to_building_association ON (rooms.id_building=zone_to_building_association.id_building)'
        ' WHERE timestamp <"' + str(begin_timestamp) + '" AND active=TRUE AND actuator_feeds.type_of_action="brightness"'
        ' AND session_states.id_session NOT IN (SELECT id_session FROM actuator_feeds WHERE timestamp BETWEEN "' + str(begin_timestamp) + '" AND "' + str(end_timestamp) + '")'
        ' GROUP BY session_states.id_session,type_of_action',db)

    hour_consumption += calculate_posterior_query_consumption("temperature", actuator_posterior_temperature_action)
    hour_consumption += calculate_posterior_query_consumption("brightness", actuator_posterior_brightness_action)
    hour_consumption += calculate_query_consumption("temperature",actuator_temperature_actions)
    hour_consumption += calculate_query_consumption("brightness",actuator_brightness_actions)
    if max_consumption_rate < hour_consumption:
        print("abbiamo consumato più del dovuto")
    print("la consumazione in questa ora è :"+str(hour_consumption)+" watt!")
    begin_timestamp = end_timestamp #calcolo l'inizio della prossima iterazione
    if (iterations == 23):
        iterations = 0
        max_consumption = 240000
        max_consumption_rate = 10000
    else:
        iterations += 1
    max_consumption-=hour_consumption
    max_consumption_rate = max_consumption/(24-iterations)
    print("ratio di consumo attuale:"+str(max_consumption_rate))
    return 0

def calculate_query_consumption(type,actuator_actions):
    hour_consumption=0
    counter=0
    for value,timestamp,active in zip(actuator_actions.value,actuator_actions.timestamp,actuator_actions.active):
        action_duration = 0
        print("counter:"+str(counter))
        print("len:"+str(len(actuator_actions.type_of_action) -1))
        if counter <(len(actuator_actions.type_of_action) -1) : #se non è l'ultimo elemento
            #print(actuator_actions['timestamp'][counter])
            action_duration += hours_between(datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S.%f'),\
                                             datetime.datetime.strptime(actuator_actions['timestamp'][counter+1], '%Y-%m-%d %H:%M:%S.%f'))
        else:
            if  active is False:
                #print(actuator_temperature_actions['timestamp_end'][1])
                end_session_timestamp=actuator_actions['timestamp_end'][counter]
                action_duration += hours_between(datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S.%f'), datetime.datetime.strptime(end_session_timestamp,'%Y-%m-%d %H:%M:%S.%f'))
                #action_duration += hours_between(timestamp,end_session_timestamp)
            else:
                action_duration += hours_between(datetime.datetime.strptime(timestamp,'%Y-%m-%d %H:%M:%S.%f'), end_timestamp)

        if type == "brightness":
            hour_consumption += 5 * (1 + brightness_tuple.index(value)) * action_duration
            print("hour_consumption:"+ str(hour_consumption))
            print("ho tenuto la lampadia accessa per :"+str(action_duration)+"ore")
        else:
            pass
            #1,204 è la densità dell'aria
            #1.006 calore specifico dell'aria
            print("temperatura ambiente:"+actuator_actions['weather_temp'][counter])
            print("temperatura riscaldamento:" + value)
            print("durata:"+str(action_duration))
            hour_consumption+=abs(int(float(actuator_actions['weather_temp'][counter]))-int(value)) * (1.204 * room_size) * 1.006 * action_duration #consumazione in ora giusto per vedere
            print("hour_consumption:" + str(hour_consumption))
        print(counter)
        counter+=1
    return hour_consumption



def calculate_posterior_query_consumption(type,actuator_actions):
    hour_consumption=0
    counter=0
    for value in zip(actuator_actions.value):
        #la durata viene contata dall'inizio del range alla fine del range
        action_duration = hours_between(begin_timestamp,end_timestamp)
        if type == "brightness":
            print(value)
            print("prova a posteriori")
            hour_consumption += 5 * (1 + brightness_tuple.index(value[0])) * action_duration
            print("hour_consumption:"+ str(hour_consumption))
            print("ho tenuto la lampadia accessa per :"+str(action_duration)+"ore")
        else:
            print("temperatura ambiente:"+actuator_actions['weather_temp'][counter])
            print("temperatura riscaldamento:" + str(value[0]))
            print("durata:"+str(action_duration))
            hour_consumption+=abs(int(float(actuator_actions['weather_temp'][counter]))-int(value[0])) * (1.204 * room_size) * 1.006 * action_duration #consumazione in ora giusto per vedere
            print("hour_consumption:" + str(hour_consumption))
        print(counter)
        counter+=1
    return hour_consumption



def hours_between(d1, d2):
    return abs((d2 - d1).total_seconds()/(60*60))


schedule.every(5).seconds.do(hour_count)
while True:
    schedule.run_pending()
    #time.sleep(60) # wait one minute



#TEST piano
#creaimo un insieme di dati di finte sessioni
#una volta fatto ciò creeremo delle dei casi e  vedere se funziona in modo giusto
#caso 1: tutto nella norma
#caso 2: over
#caso 3: tutto normale, ma in questo caso vedere come se la cava dopo aver preso provvedimenti
#caso 4: over di nuovo
#caso 5: tutto nella norma
#caso 6: vedere se il reset è fatto bene
#caso 7: testare la comunicazione con il server Flask




