import datetime
import re
from flask_mqtt import Mqtt

from apphandler import app
from models import db, digitalTwinFeed, sensorFeeds

mqtt=Mqtt()
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

        value=data.get('payload')
        print("con valore:"+str(value))
        updateDigitalTwinSensors(identifiers[1],sensor[4],value)
        #sendDataToAdafruitFeed(data.get)



def updateDigitalTwinSensors(id_room,sensor,value):
    if sensor != "noise_sensor":
        with app.app_context():
            digitalTwin=db.session.query(digitalTwinFeed).filter_by(id_room=id_room).first()
            timestamp=datetime.datetime.utcnow()
            sensorFeed = sensorFeeds(digitalTwin.id_room,sensor,value,timestamp)
            if sensor == "light_sensor":
                digitalTwin.light_sensor=value
                db.session.add(sensorFeed)
                db.session.commit()
    return 0