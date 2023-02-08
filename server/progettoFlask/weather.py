import requests
import datetime
from sqlalchemy import extract
from models import db, weatherReport, zoneToBuildingAssociation, rooms, zones, buildings


def weather_report(id_room):
    id_building = db.session.query(rooms).filter_by(id_room=id_room).first().id_building
    building_name = db.session.query(buildings).filter_by(id_building=id_building).first().city
    id_zone =  db.session.query(zoneToBuildingAssociation).filter_by(id_building=id_building).first().id_zone
    zone = db.session.query(zones).filter_by(id_zone=id_zone).first()
    lon = zone.lon
    lat=zone.lat
    timestamp = datetime.datetime.utcnow()
    report= db.session.query(weatherReport).filter_by(id_zone=id_zone).filter(extract('day', weatherReport.timestamp) == timestamp.day)\
        .filter(extract('month', weatherReport.timestamp)==timestamp.month).filter(extract('year', weatherReport.timestamp)==timestamp.year)\
        .filter(extract('hour', weatherReport.timestamp)>(timestamp.hour-1)).first()
    if report is None:
        url = "http://api.openweathermap.org/data/2.5/weather?lat="+str(lat)+"&lon="+str(lon)+"&APPID=32df44a05a6ca0cb568e21166cf9cd2a&units=metric"
        response = requests.request("GET", url)
        status_code = response.status_code
        if status_code != 200:
            print("Uh oh, there was a problem when accessing the 5 day weather forecast API. Please try again later")
            report= db.session.query(weatherReport).filter_by(id_zone=id_zone).order_by(weatherReport.timestamp.desc()).first()
            if report is None:
                print("printo dati di default")
                return {"temperature": 22, "humidity": 50}
            else:
                print("l'API non funziona! Ho preso i dati dal db!")
                return {"temperature": report.temperature, "humidity": report.humidity}
        else:
            results = response.json()
            db.session.add(weatherReport(id_zone,results["main"]["temp"],results["main"]["humidity"],timestamp))
            db.session.commit()
            print("Prendo i dati dall'API")
            return {"temperature":results["main"]["temp"],"humidity":results["main"]["humidity"]}
    else:
        print("printo dati del DB!")
        return {"temperature":report.temperature,"humidity":report.humidity,"city_name":building_name}