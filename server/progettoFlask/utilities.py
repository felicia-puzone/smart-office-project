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

#tested
def seconds_between(d1, d2):
    return abs((d2 - d1).total_seconds())