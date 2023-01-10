# tested
import datetime



import geolog
from models import sessionStates, rooms, buildings, zones, professions, digitalTwinFeed, User, \
    zoneToBuildingAssociation, db, sensorFeeds


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
    db.session.commit()
