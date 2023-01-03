import requests
import urllib.parse


#TODO testing
#TODO handle errori
def getMarker(address):
    print(address)
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    print("ciao")
    response = requests.get(url).json()
    print(response[0]["lat"])
    print(response[0]["lon"])
    marker= {
        'name':address,
        'lat':str(response[0]["lat"]),
        'lon':str(response[0]["lon"]),
        }
    return marker


#possible values of type:
#administrative
#locality
#neighbourhood
#stop
#bus_stop
#cinema
#etc....
def getMarkerByType(address,type):
    print(address)
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    places = requests.get(url).json()
    marker = {}
    for place in places:
        if place["type"] == type:
            print(place["lat"])
            print(place["lon"])
            marker= {
            'name':address,
            'lat':str(place["lat"]),
            'lon':str(place["lon"]),
            }
            return marker
    return marker

def isAddressValid(address):
    print(address)
    url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(address) + '?format=json'
    response = requests.get(url).json()
    if response == []:
        #print("non esisto lol")
        return False
    return True



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