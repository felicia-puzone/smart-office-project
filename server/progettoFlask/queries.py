# tested
import datetime
import random

from sqlalchemy import extract

import geolog
from models import sessionStates, rooms, buildings, zones, professions, digitalTwinFeed, User, \
    zoneToBuildingAssociation, db, sensorFeeds, actuatorFeeds, weatherReport, dailyRoomconsumptionReport, \
    monthlyRoomconsumptionReport, dailyBuildingconsumptionReport, monthlyBuildingconsumptionReport, telegram
import pandas as pd
import json
import plotly
import plotly.express as px

from utilities import colors, brightness_values


def getFreeBuildings():
    activeSessionStates = db.session.query(sessionStates.id_room).filter_by(active=True)
    freeRoomsBuildings = db.session.query(rooms.id_building).filter(
        rooms.id_room.notin_(activeSessionStates)).filter_by(available=True)
    freeBuildings = db.session.query(buildings).filter(buildings.id_building.in_(freeRoomsBuildings)).filter_by(
        available=True)
    return freeBuildings


def tryToAssignZone(city, state):
    zone = db.session.query(zones).filter_by(city=city, state=state).first()
    # se la zona non esiste, la creiamo
    if zone is None:
        zone = zones(city, state)
        db.session.add(zone)
        db.session.commit()
        if zone.id_zone is None:
            db.session.refresh(zone)
    return zone


# testato
def getBuildings():
    return buildings.query.all()


# testato
def fetchJobs():
    return db.session.query(professions).filter(professions.name != "Administrator").all()


# Formato Indirizzo Città,Via/Viale+Via+Numero,Stato


# TODO testing
# TODO ogni stanza avrà un digitalTwin
def createNewBuilding(city, route, number, state, numberofrooms):
    # Modena, Giuseppe Verdi 11/a, State
    address = str(city).title() + ", " + str(route).title() + " " + str(number).title() + ", " + str(state).title()
    if geolog.isAddressValid(address):
        # indirizzo valido
        zone = db.session.query(zones).filter_by(state=state, city=city).first()
        if zone:
            # esiste già
            building = buildings(city, route, number, state, zone.id_zone)
            db.session.add(building)
            db.session.refresh()
            addrooms(numberofrooms, building.id_building)
        else:
            building = buildings(city, route, number, state)
            db.session.add(building)
            db.session.refresh()
            addrooms(numberofrooms, building.id_building)
    else:
        return False
    # in questo metodo prendiamo in input l'indirizzo e
    # mettiamo i dati in un formato tale da non poter creare dati duplicati
    # Città Via Numero (Prima lettera maiuscola, il resto minuscolo)
    return True


# TODO testing
def addrooms(numberofrooms, id_building):
    for _ in numberofrooms:
        room = rooms(id_building)
        db.session.add(room)
        db.session.commit()
        db.session.refresh()
        if room:
            db.session.add(digitalTwinFeed(room.id_room))
            db.session.refresh()
    return 0


# TODO testing
def removerooms(id_building, number):
    roomsFetched = db.session.query(rooms).filter_by(id_building=id_building)
    for _ in number:
        digitalTwinToRemove = db.session.query(digitalTwinFeed).filter_by(id_room=roomsFetched.last().id_room)
        db.session.delete(roomsFetched.last())
        db.session.delete(digitalTwinToRemove)
        db.session.refresh()
    return 0


def updateBuilding():
    # città #indirizzo #zona
    # numero di stanze 2 casi più stanze o meno stanze
    return 0


# TODO testing
def deleteBuilding(id_building):
    building = db.session.query(buildings).filter_by(id_building=id_building).first()
    roomsToDelete = db.session.query(rooms).filter_by(id_building=id_building)
    db.session.delete(building)
    for room in roomsToDelete:
        digitalTwinToDelete = db.session.query(digitalTwinFeed).filter_by(id_room=room.id_room).first()
        db.session.delete(room)
        db.session.delete(digitalTwinToDelete)
        db.session.refresh()
    if building is None:
        if roomsToDelete is None:
            return True
    return False

#def queryLightSensorRoom(id_room):
 #   light_sensor_feed = db.session.query(sensorFeeds).filter_by(id_room=id_room).filter_by(type_of_sensor="light")



def createAndPopulateDb():
    db.drop_all()
    db.create_all()
    user = User(username="Admin", password="Admin", profession="Administrator", sex=3,
                dateOfBirth=datetime.datetime.utcnow().date())
    user.super_user = True
    user.admin = True

    db.session.add(user)
    db.session.commit()
    db.session.refresh(user)
    telegram_key = telegram(user.id,''.join(random.choice('0123456789') for _ in range(6)))
    db.session.add(telegram_key)
    db.session.add(User(username="BArfaoui", password="password", profession="Administrator", sex=1,
                        dateOfBirth=datetime.datetime.utcnow().date()))
    # db.session.add(User(username="BArfaoui",password="18121996",profession=8,sex=1,dateOfBirth=datetime.utcnow().date()))
    # db.session.add(User(username="PFelica", password="99669966", profession=8, sex=2,
    #                       dateOfBirth=datetime.utcnow().date()))
    # db.session.add(User(username="Vincenzo", password="66996699", profession=8, sex=1,
    #                      dateOfBirth=datetime.utcnow().date()))
    # db.session.add(User(username="HLoredana", password="EmiliaBestWaifu", profession=10,  sex=2,
    #                       dateOfBirth=datetime.utcnow().date()))
    # db.session.add(User(username="IValeria",  password="DarthVal", profession=12,sex=2,
    #                       dateOfBirth=datetime.utcnow().date()))
    # db.session.add(User(username="Nicolò", password="11223344", profession=1, sex=3,
    #                       dateOfBirth=datetime.strptime("2000-12-1","%Y-%m-%d")))
    building = buildings(city="Modena", route='', number='', state='Italia')
    zone = tryToAssignZone("Modena", "Italia")
    db.session.add(building)
    db.session.commit()
    db.session.refresh(building)
    db.session.refresh(zone)
    db.session.add(zoneToBuildingAssociation(zone.id_zone, building.id_building))
    db.session.commit()
    # db.session.add(buildings(city="Roma",route='',number='',state='Italia'))
    # db.session.add(buildings(city="Napoli",route='',number='',state='Italia'))
    # db.session.add(buildings(city="Bologna",route='',number='',state='Italia'))
    # db.session.add(buildings(city="Milano",route='',number='',state='Italia'))
    # db.session.add(buildings(city="Genova",route='',number='',state='Italia'))
    # db.session.add(buildings(city="Manzolino",route='via Giovanni archi',number='',state='Italia'))
    db.session.add(rooms(id_building=1))
    db.session.add(digitalTwinFeed(1, 0, 0, 0, 0))
    db.session.add(rooms(id_building=1))
    db.session.add(digitalTwinFeed(2, 0, 0, 0, 0))
    db.session.add(rooms(id_building=1))
    db.session.add(digitalTwinFeed(3, 0, 0, 0, 0))
    '''    db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=1))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=2))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=3))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=4))
       db.session.add(rooms(id_building=5))
       db.session.add(rooms(id_building=5))
       db.session.add(rooms(id_building=5))'''
    '''db.session.add(digitalTwinFeed(2, 0,0, 0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(3, 0,0, 0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(4, 0,0, 0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(5,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(6, 0, 0,0, 0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(7, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(8, 0, 0, 0,0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(9,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(10, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(11, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(12, 0, 0, 0, 0, 0,0, 0, True))
       db.session.add(digitalTwinFeed(13,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(14, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(15, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(16, 0, 0, 0,0, 0, 0, 0, True))
       db.session.add(digitalTwinFeed(17,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(18, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(19, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(20, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(21,0,0,0,0,0,0,0,True))
       db.session.add(digitalTwinFeed(22, 0, 0, 0, 0,0, 0, 0, True))
       db.session.add(digitalTwinFeed(23, 0, 0, 0, 0, 0,0, 0, True))
       db.session.add(digitalTwinFeed(24, 0, 0, 0, 0, 0,0, 0, True))'''
    db.session.add(professions(name="Administrator", category=5))
    db.session.add(professions(name="Streamer", category=0))
    db.session.add(professions(name="Blogger", category=0))
    db.session.add(professions(name="Televendite", category=0))
    db.session.add(professions(name="Professore/Istruttore", category=1))
    db.session.add(professions(name="Seminarista", category=1))
    db.session.add(professions(name="Snake oil seller", category=1))
    db.session.add(professions(name="Assistenza telefonica", category=2))
    db.session.add(professions(name="Programmatore", category=2))
    db.session.add(professions(name="Contabile", category=2))
    db.session.add(professions(name="Manager", category=2))
    db.session.add(professions(name="Elettricista", category=3))
    db.session.add(professions(name="Sistemista", category=3))
    db.session.add(professions(name="Colf/Badante", category=4))
    db.session.add(professions(name="Babysitter", category=4))
    db.session.add(professions(name="Operatore CAF/CISL", category=5))
    db.session.add(professions(name="Operatore NASPI", category=5))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("17-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("16-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("15-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("14-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("13-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("12-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("1-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("17-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("16-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("15-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("14-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("13-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("12-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("1-01-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-12-2023","%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-11-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-10-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-09-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-08-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-07-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-06-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-05-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-04-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-03-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-02-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-01-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-12-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-11-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-10-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-09-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-08-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-07-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-06-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-05-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-04-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-03-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-02-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-01-2023", "%d-%m-%Y")))



    #EDIFICIO 3
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("17-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("16-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("15-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("14-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("13-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("12-01-2023", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("1-01-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-12-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-11-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-10-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-09-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-08-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-07-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-06-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-05-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-04-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-03-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-02-2023", "%d-%m-%Y")))
    db.session.add(monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-01-2023", "%d-%m-%Y")))

    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-12-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-11-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-10-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-09-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-08-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-07-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-06-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-05-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-04-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-03-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-02-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-01-2023", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("16-01-2023", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("17-01-2023", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("18-01-2023", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(2, 20000, 150, datetime.datetime.strptime("19-01-2023", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("20-01-2023", "%d-%m-%Y")))
    #STANZA 3
    db.session.add(dailyRoomconsumptionReport(3, 20000, 150, datetime.datetime.strptime("16-01-2023", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(3, 20000, 150, datetime.datetime.strptime("20-01-2023", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(3, 20000, 150, datetime.datetime.strptime("21-01-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-12-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-11-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-10-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-09-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-08-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-07-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-06-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-05-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-04-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-03-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-02-2023", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-01-2023", "%d-%m-%Y")))
    
    
    
    #2022
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("17-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("16-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("15-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("14-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("13-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("12-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(1, 20000, 5000, datetime.datetime.strptime("1-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("17-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("16-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("15-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("14-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("13-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("12-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(2, 20000, 5000, datetime.datetime.strptime("1-01-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-12-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-11-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-10-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-09-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-08-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-07-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-06-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-05-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-04-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-03-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-02-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(2, 2000000, 5000, datetime.datetime.strptime("28-01-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-12-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-11-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-10-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-09-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-08-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-07-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-06-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-05-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-04-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-03-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-02-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(1, 2000000, 5000, datetime.datetime.strptime("28-01-2022", "%d-%m-%Y")))

    # EDIFICIO 3
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("17-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("16-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("15-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("14-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("13-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("12-01-2022", "%d-%m-%Y")))
    db.session.add(dailyBuildingconsumptionReport(3, 20000, 5000, datetime.datetime.strptime("1-01-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-12-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-11-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-10-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-09-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-08-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-07-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-06-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-05-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-04-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-03-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-02-2022", "%d-%m-%Y")))
    db.session.add(
        monthlyBuildingconsumptionReport(3, 2000000, 5000, datetime.datetime.strptime("28-01-2022", "%d-%m-%Y")))

    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-12-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-11-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-10-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-09-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-08-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-07-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-06-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-05-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-04-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-03-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-02-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(2, 200000, 150, datetime.datetime.strptime("28-01-2022", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("16-01-2022", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("17-01-2022", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("18-01-2022", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(2, 20000, 150, datetime.datetime.strptime("19-01-2022", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(1, 20000, 150, datetime.datetime.strptime("20-01-2022", "%d-%m-%Y")))
    # STANZA 3
    db.session.add(dailyRoomconsumptionReport(3, 20000, 150, datetime.datetime.strptime("16-01-2022", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(3, 20000, 150, datetime.datetime.strptime("20-01-2022", "%d-%m-%Y")))
    db.session.add(dailyRoomconsumptionReport(3, 20000, 150, datetime.datetime.strptime("21-01-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-12-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-11-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-10-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-09-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-08-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-07-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-06-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-05-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-04-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-03-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-02-2022", "%d-%m-%Y")))
    db.session.add(monthlyRoomconsumptionReport(3, 200000, 150, datetime.datetime.strptime("28-01-2022", "%d-%m-%Y")))
    db.session.commit()



def buildRoomLightSensorGraph(id_room):
    light_sensor_feed = db.session.query(sensorFeeds).filter_by(id_room=id_room).order_by(
        sensorFeeds.timestamp.desc()).all()
    list_values = []
    list_times = []
    if light_sensor_feed is not None:
        for light_sensor in light_sensor_feed:
            list_values.append(1000 - int(light_sensor.value))
            list_times.append(light_sensor.timestamp)
    df = {"time": list_times, "values": list_values}
    fig = px.line(df, x="time", y="values", title='Sensore di luce',)
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def buildBuildingLightSensorGraph(rooms_of_building):
    light_sensor_feed = db.session.query(sensorFeeds).order_by(
        sensorFeeds.timestamp.desc()).filter(
        sensorFeeds.id_room.in_(rooms_of_building)).all()
    list_values = []
    list_times = []
    if light_sensor_feed is not None:
        for light_sensor in light_sensor_feed:
            list_values.append(1000 - int(light_sensor.value))
            list_times.append(light_sensor.timestamp)
    df = {"time": list_times, "values": list_values}
    fig = px.line(df, x="time", y="values", title='Sensore di luce')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildRoomTemperatureGraph(session_states):
    temperature_actuator_feed = db.session.query(actuatorFeeds).filter(
        actuatorFeeds.id_session.in_(session_states)).filter_by(type_of_action="temperature") \
        .order_by(actuatorFeeds.timestamp.desc()).all()
    list_values = []
    list_times = []
    if temperature_actuator_feed is not None:
        for temperature_actuator in temperature_actuator_feed:
            list_values.append(int(temperature_actuator.value))
            list_times.append(temperature_actuator.timestamp)
    df = {"time": list_times, "values": list_values}
    fig = px.line(df, x="time", y="values", title='Riscaldamento della stanza')
    fig.update_layout(plot_bgcolor = "rgba(0,0,0,0)")
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildRoomColorGraph(session_states):
    led_color_query = db.session.query(actuatorFeeds).filter(actuatorFeeds.id_session.in_(session_states)).filter_by(
        type_of_action="color")
    color_list = []
    color_number_list = []
    for color in colors:  # scorro i color
        if color != "NONE":
            color_list.append(color)
            color_number_list.append(led_color_query.filter_by(value=color).count())
    df = pd.DataFrame({
        "Colors": color_list,
        "Amount": color_number_list,
    })
    fig = px.bar(df, x="Colors", y="Amount", barmode="group", title='Colori LED')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def buildRoomBrightnessGraph(session_states):
    brightness_actuator_feed = db.session.query(actuatorFeeds).filter(
        actuatorFeeds.id_session.in_(session_states)).filter_by(type_of_action="brightness") \
        .order_by(actuatorFeeds.timestamp.desc()).all()
    list_values = []
    list_times = []
    if brightness_actuator_feed is not None:
        for brightness_actuator in brightness_actuator_feed:
            list_values.append(brightness_values.index(brightness_actuator.value))
            list_times.append(brightness_actuator.timestamp)

    df = {"time": list_times, "values": list_values}
    fig = px.line(df, x="time", y="values", title='Intensità del LED')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildZoneWeatherGraph(weatherReport_feed):
    list_values = []
    list_times = []
    if weatherReport_feed is not None:
        for weather in weatherReport_feed:
            list_values.append(int(float(weather.temperature)))
            list_times.append(weather.timestamp)

    df = {"time": list_times, "values": list_values}
    fig = px.line(df, x="time", y="values", title='Temperatura meteo della zona')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildZoneWeatherHumidityGraph(weatherReport_feed):
    list_values = []
    list_times = []
    if weatherReport_feed is not None:
        for weather in weatherReport_feed:
            list_values.append(int(float(weather.humidity)))
            list_times.append(weather.timestamp)

    df = {"time": list_times, "values": list_values}
    fig = px.line(df, x="time", y="values", title='Umidità nella zona')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

def buildRoomDailyConsumptionReport(id_room):
    timestamp=datetime.datetime.utcnow()
    daily_report = db.session.query(dailyRoomconsumptionReport).filter_by(id_room=id_room)\
    .order_by(dailyRoomconsumptionReport.timestamp.desc()).filter(extract('month', dailyRoomconsumptionReport.timestamp)==timestamp.month)\
    .filter(extract('year', dailyRoomconsumptionReport.timestamp)==timestamp.year).all()
    list_values = []
    list_times = []
    list_types = []
    if daily_report is not None:
        for report in daily_report:
            list_values.append(float(report.temperature)/1000)
            list_types.append("AIR CONDITIONING in Kw")
            list_values.append(float(report.light)/1000)
            list_types.append("LED BRIGHTNESS in Kw")
            list_times.append(report.timestamp.strftime("%d-%m-%Y"))
            list_times.append(report.timestamp.strftime("%d-%m-%Y"))
    df = pd.DataFrame({
        "time": list_times,
        "values": list_values,
        "type": list_types,
    })
    fig = px.bar(df, x="time", y="values",color="type", barmode="group", title='Consumi giornalieri della stanza')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildRoomMonthlyConsumptionReport(id_room):
    timestamp = datetime.datetime.utcnow()
    monthly_report = db.session.query(monthlyRoomconsumptionReport).filter_by(id_room=id_room)\
    .order_by(monthlyRoomconsumptionReport.timestamp.desc()).filter(extract('year', monthlyRoomconsumptionReport.timestamp)==timestamp.year).all()
    list_values = []
    list_times = []
    list_types = []
    if monthly_report is not None:
        for report in monthly_report:
            list_values.append(float(report.temperature)/1000)
            list_types.append("AIR CONDITIONING in Kw")
            list_values.append(float(report.light)/1000)
            list_types.append("LED BRIGHTNESS in Kw")
            list_times.append(report.timestamp.strftime("%m-%Y"))
            list_times.append(report.timestamp.strftime("%m-%Y"))
    df = pd.DataFrame({
        "time": list_times,
        "values": list_values,
        "type": list_types,
    })
    fig = px.bar(df, x="time", y="values",color="type", barmode="group", title='Consumi mensili della stanza')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildBuildingDailyConsumptionReport(id_building):
    timestamp = datetime.datetime.utcnow()
    daily_report = db.session.query(dailyBuildingconsumptionReport).filter_by(id_building=id_building) \
        .order_by(dailyBuildingconsumptionReport.timestamp.desc()).filter(
        extract('month', dailyBuildingconsumptionReport.timestamp) == timestamp.month) \
        .filter(extract('year', dailyBuildingconsumptionReport.timestamp) == timestamp.year).all()
    list_values = []
    list_times = []
    list_types = []
    if daily_report is not None:
        for report in daily_report:
            list_values.append(float(report.temperature)/1000)
            list_times.append(report.timestamp.strftime("%d-%m-%Y"))
            list_types.append("AIR CONDITIONING in Kw")
            list_values.append(float(report.light)/1000)
            list_types.append("LED BRIGHTNESS in Kw")
            list_times.append(report.timestamp.strftime("%d-%m-%Y"))
    df = pd.DataFrame({
        "time": list_times,
        "values": list_values,
        "type": list_types,
    })
    fig = px.bar(df, x="time", y="values", color="type", barmode="group", title='Consumi giornalieri dell\'edificio')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildBuildingMonthlyConsumptionReport(id_building):
    timestamp = datetime.datetime.utcnow()
    monthly_report = db.session.query(monthlyBuildingconsumptionReport).filter_by(id_building=id_building) \
        .order_by(monthlyBuildingconsumptionReport.timestamp.desc())\
        .filter(extract('year', monthlyBuildingconsumptionReport.timestamp) == timestamp.year).all()
    list_values = []
    list_times = []
    list_types = []
    if monthly_report is not None:
        for report in monthly_report:
            list_values.append(float(report.temperature)/1000)
            list_types.append("AIR CONDITIONING in Kw")
            list_values.append(float(report.light)/1000)
            list_types.append("LED BRIGHTNESS in Kw")
            list_times.append(report.timestamp.strftime("%m-%Y"))
            list_times.append(report.timestamp.strftime("%m-%Y"))
    df = pd.DataFrame({
        "time": list_times,
        "values": list_values,
        "type": list_types,
    })
    fig = px.bar(df, x="time", y="values", color="type", barmode="group", title='Consumi mensili della stanza')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildZoneDailyConsumptionReport(buildings):
    timestamp = datetime.datetime.utcnow()
    daily_report = db.session.query(dailyBuildingconsumptionReport).filter(dailyBuildingconsumptionReport.id_building.in_(buildings)) \
        .order_by(dailyBuildingconsumptionReport.timestamp.desc()).filter(
        extract('month', dailyBuildingconsumptionReport.timestamp) == timestamp.month) \
        .filter(extract('year', dailyBuildingconsumptionReport.timestamp) == timestamp.year).all()
    list_values = []
    list_times = []
    list_types = []
    if daily_report is not None:
        for report in daily_report:
            list_values.append((float(report.temperature) + float(report.light))/1000)
            list_times.append(report.timestamp)
            list_types.append("CONSUMO IN Kw EDIFICIO ID:" + str(report.id_building))
    df = pd.DataFrame({
        "time": list_times,
        "values": list_values,
        "type": list_types,
    })
    fig = px.bar(df, x="time", y="values", color="type", barmode="group", title='Consumi giornalieri dell\'edificio')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
def buildZoneMonthlyConsumptionReport(buildings):
    timestamp = datetime.datetime.utcnow()
    monthly_report = db.session.query(monthlyBuildingconsumptionReport).filter(monthlyBuildingconsumptionReport.id_building.in_(buildings)) \
        .order_by(monthlyBuildingconsumptionReport.timestamp.desc())\
        .filter(extract('year', monthlyBuildingconsumptionReport.timestamp) == timestamp.year).all()
    list_values = []
    list_times = []
    list_types = []
    if monthly_report is not None:
        for report in monthly_report:
            list_values.append((float(report.temperature) + float(report.light))/1000)
            list_times.append(report.timestamp)
            list_types.append("CONSUMO IN Kw EDIFICIO ID:"+str(report.id_building))
            #list_types.append("AIR CONDITIONING")
            #list_values.append(float(report.light))
            #list_types.append("LED BRIGHTNESS")
            #list_times.append(report.timestamp)
    df = pd.DataFrame({
        "time": list_times,
        "values": list_values,
        "type": list_types,
    })
    fig = px.bar(df, x="time", y="values", color="type", barmode="group", title='Consumi mensili della stanza')
    return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)


def fetchMontlhyReport():
    #report dei consumi delle zone di questo mese
    Report = ""
    timestamp = datetime.datetime.utcnow() - datetime.timedelta(days=(31))
    zones_for_report = db.session.query(zones).all()
    for zone in zones_for_report:
        building_ids = db.session.query(zoneToBuildingAssociation.id_building).filter_by(id_zone=zone.id_zone)
        monthly_report = db.session.query(monthlyBuildingconsumptionReport).filter(
        monthlyBuildingconsumptionReport.id_building.in_(building_ids)) \
        .order_by(monthlyBuildingconsumptionReport.timestamp.desc()) \
        .filter(extract('year', monthlyBuildingconsumptionReport.timestamp) == timestamp.year)\
        .filter(extract('month', monthlyBuildingconsumptionReport.timestamp) == timestamp.month).all()
        zone_name = zone.city + " " + zone.state
        sum=0
        if monthly_report is not None:
            #Report += "Zona id:" + str(zone.id_zone) + " " + zone_name + "\n"
            for report_building in monthly_report:
                #amount = str(float(report_building.temperature) + float(report_building.light)) + " Watt\n"
                #building_for_report = db.session.query(buildings).filter_by(id_building=report_building.id_building).first()
                #Report +="EDIFICIO ID:" + str(report_building.id_building) + " Indirizzo" + building_for_report.city + " " + building_for_report.address + ":\n"
                #Report +=amount
                sum+=float(report_building.temperature) + float(report_building.light)
        if sum > 0:
            Report += "\n🏙️ " + zone_name + " 🏙️\n"
            Report += "Consumo totale: "+str(sum) +" Watt ⚡\n"
    if Report == "":
        return "(Al momento non ci sono report di consumi disponibili. Prova più tardi.)"
    return Report