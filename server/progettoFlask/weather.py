import requests
import datetime
from time import strftime
# Use Geolocation API to fetch long/lat of target location
longitude = 20
latitude = 43

# Now use 5 day weather forecast API to fetch weather data based on the returned long/lat coordinates
url = "https://api.openweathermap.org/data/2.5/weather?lat=44.5384728&lon=10.9359608705307&appid=32df44a05a6ca0cb568e21166cf9cd2a&units=metric"
#url = "https://api.openweathermap.org/data/2.5/forecast?lat=" + str(latitude) + "&lon=" + str(
 #   longitude) + "&appid={32df44a05a6ca0cb568e21166cf9cd2a}&units=metric"
response = requests.request("GET", url)
status_code = response.status_code
if status_code != 200:
    print("Uh oh, there was a problem when accessing the 5 day weather forecast API. Please try again later")
    quit()

results = response.json()

output = ""

for result in results["list"]:
    time = datetime.datetime.fromtimestamp(result["dt"]).strftime("%a %d %b %H:%M %p")
    temperature = result["main"]["temp"]
    weather = result["weather"][0]["description"]

    output += time + " " + str(temperature) + " " + str(weather) + "\n"

print(output)