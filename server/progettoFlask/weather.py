import requests
import datetime
from time import strftime

# Use Geolocation API to fetch long/lat of target location
city = "Modena"
state = "Italia"
country = "Italia"

query_parts = []
if len(city) > 0:
    query_parts.append(city)

if len(state) > 0:
    query_parts.append(state)

if len(country) > 0:
    query_parts.append(country)

query_string = ",".join(query_parts)

url = "http://api.openweathermap.org/geo/1.0/direct?q=" + query_string + "&limit=3&appid={YOUR_API_KEY}"

response = requests.request("GET", url)

status_code = response.status_code

if status_code != 200:
    print("Uh oh, there was a problem when accessing the Geolocation API. Please try again later")
    quit()

results = response.json()

target_location = None
if len(results) > 1:

    message = "There is more than 1 result for your query, please select an option from the list below."
    for index, result in enumerate(results):
        message += "\n Enter (" + str(index + 1) + ") for: " + result["name"] + ", " + result["state"] + ", " + result[
            "country"]
    message += "\n"

    target_location_index = input(message)

    try:
        target_location_index = int(target_location_index)

        if target_location_index < 1 or target_location_index > len(results):
            raise Exception
    except Exception:
        print("Valid option not selected, defaulting to option 1")
        target_location_index = 1

    target_location = results[target_location_index - 1]
else:
    target_location = results[0]

longitude = target_location["lon"]
latitude = target_location["lat"]

# Now use 5 day weather forecast API to fetch weather data based on the returned long/lat coordinates
print(
    "Looking up weather data for " + target_location["name"] + ", " + target_location["state"] + ", " + target_location[
        "country"] + " (with long/lat: " + str(longitude) + "/" + str(latitude) + ")")

url = "https://api.openweathermap.org/data/2.5/forecast?lat=" + str(latitude) + "&lon=" + str(
    longitude) + "&appid={YOUR_API_KEY}&units=metric"

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