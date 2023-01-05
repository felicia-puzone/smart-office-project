import csv
from datetime import datetime
def calculateUserAge(born):
    today = datetime.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))
#testato
def appendDataToJson(jsonObj,keys,values): #testing
    for k,v in (keys,values):
        jsonObj[k]=v
    return jsonObj

def buildJsonList(list):
    new_list=[]
    for element in list:
        new_list.append(element.serialize())
    return new_list

def translateLEDValue(value):
    if value == "RED":
        return 1
    elif value == "BLUE":
        return 2

def createABuildingtupleList(query):
    new_list = []
    for element in query:
        element = element.serialize()
        print(element)
        new_list.append((element['id_building'],str(element['city'])+ " " + str(element['route']) +" " +str(element['number'])))
    return new_list


def createAProfessiontupleList(query):
    new_list = []
    for element in query:
        element = element.serialize()
        print(element)
        new_list.append((element['id_profession'],str(element['name'])))
    return new_list



#TODO testing
def createSensorFeedCSV(path,query,date):
        name=str(path)+"/"+"sensors_data_"+str(date.strftime("%d_%m_%y"))+".csv"
        with open(name, 'w') as f:
            out = csv.writer(f)
            out.writerow([b'idroom', b'sensor',b'value',b'timestamp'])
            for item in query:
                out.writerow([item.id_room, item.type_of_sensor,item.value,item.timestamp])


#TODO testing
def createActuatorFeedCSV(query,date,users,sessionsStates,jobs):
    name = "actuator_data_" + str(date.strftime("%d_%m_%y")) + ".csv"
    with open(name, 'w') as f:
        out = csv.writer(f)
        out.writerow([b'idroom', b'age', b'sex', b'job',b'actuator', b'value', b'timestamp'])
        for item in query:
            sessionState=sessionsStates.filter_by(id_session=item.id_session).first()
            user = users.filter_by(id_user=sessionState.id_user).first()
            age = calculateUserAge(user.dateOfBirth)
            job = jobs.filter_by(id_profession=user.profession).first().name
            out.writerow([sessionState.id_room, age, user.sex,job,item.type_of_action, item.value, item.timestamp])

#TODO testing
def createSessionsCSV(query,type,date,users,sessionsStates,jobs):
    if type =="sessions":
        name = "sessions_data_" + str(date.strftime("%d_%m_%y")) + ".csv"
        with open(name, 'w') as f:
            out = csv.writer(f)
            out.writerow([b'idroom',  b'age', b'sex', b'job',b'timestamp_begin',b'timestamp_end'])
            for item in query:
                sessionState = sessionsStates.filter_by(id_session=item.id_session).first()
                user = users.filter_by(id_user=sessionState.id_user).first()
                age = calculateUserAge(user.dateOfBirth)
                job = jobs.filter_by(id_profession=user.profession).firt().name
                out.writerow([sessionState.id_room, age, user.sex, job, item.timestamp_begin,item.timestamp_begin])