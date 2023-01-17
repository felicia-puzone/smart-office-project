<<<<<<< HEAD
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
months = ('January','February','March','April','May','June',\
'July','August','September','October','November','December')
colors = ('NONE','RED','ORANGE','YELLOW','GREEN','TEAL','BLUE','INDIGO','VIOLET','RAINBOW')
brightness_values = ('LOW','MEDIUM','HIGH')


def formatName(name):
    return name.title()

=======
from datetime import datetime
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
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
<<<<<<< HEAD
    return new_list
def buildSensorList(list):
    new_list=[]
    for element in list:
        new_list.append(element.value)
    return new_list
def buildTimeStampList(list):
    new_list=[]
    for element in list:
        new_list.append(element.timestamp)
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
        new_list.append((int(element['id_building']), str(element['city'])+ " " + str(element['address'])))
    return new_list


def createAProfessiontupleList(query):
    new_list = []
    for element in query:
        element = element.serialize()
        print(element)
        new_list.append((int(element['id_profession']),str(element['name'])))
    return new_list

#tested
def seconds_between(d1, d2):
    return abs((d2 - d1).total_seconds())


def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    # Radius of earth in kilometers is 6371
    km = 6371* c
    return km
=======
    return new_list
>>>>>>> 211ed61d3cb06cf4b567dbe2af230f1e4f4796fd
