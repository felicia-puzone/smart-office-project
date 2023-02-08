from geopy import Nominatim

from utilities import haversine


def geoMarker(city,route,state):
    geolocator = Nominatim(user_agent='smartoffice')
    address=""
    if  route == "":
        print("111111Via non trovata")
        address=city.strip()+" "+state.strip()
    else:
        address=city.strip()+" "+route.strip()+" "+state.strip()
    print("mando all'API questo indirizzo:"+address)
    location = geolocator.geocode(address, exactly_one=True)
    if location is None:
        print("Via non trovata")
        address = city.strip() + " " + state.strip()
        location = geolocator.geocode(address, exactly_one=True)
        if location is None:
            return None

    marker = {'city':city,'route':route,'address': address, 'lat': location.latitude, 'lon': location.longitude}
    print(marker)
    return marker
def geoNearest(zone_candidates,building):
    nearest_zone=zone_candidates.first()
    min_distance = haversine(int(float(nearest_zone.lon)),int(float(nearest_zone.lat)),int(float(building.lon)),int(float(building.lat)))
    for zone in zone_candidates:
        distance = haversine(int(float(zone.lon)),int(float(zone.lat)),int(float(building.lon)),int(float(building.lat)))
        if distance < min_distance:
            nearest_zone = zone
            min_distance=distance
    return nearest_zone
    #>> > gn.geocode("Cleveland, OH", exactly_one=False)[0]
    #(u'Cleveland, OH, US', (41.4994954, -81.6954088))
#def isAddressValid():


#def reverseGetMarker():
 #   url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
 #   response = requests.get(url).json()
 #   print(response[0]["lat"])
 #   print(response[0]["lon"])
 #   marker=[
 #       {
 #       'name':address,
 #       'lat':response[0]["lat"],
 #       'lon':response[0]["lon"],
 #       }
 #   ]
  #  return marker