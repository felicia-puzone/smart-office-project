import os
import random

import numpy as np

import TemporalDataOperator as tdo
import GlobalDataOperator as gdo
import LocationDataOperator as ldo
import SessionDataOperator as sdo
import UserDataOperator as udo
import WorldDataOperator as wdo

tempdata_op = tdo.Operator()
location_op = ldo.Operator()
session_op = sdo.Operator()
global_op = gdo.Operator()
user_op = udo.Operator()
world_op = wdo.Operator()

sessions_path = '../Data/sessions.csv'
users_path = '../Data/users.csv'
users_json_path = '../Data/users.json'
sessions_json_path = '../Data/sessions.json'

''' 
Script used to simulate sensor-acquired data and user-selected data

    ext_temp: integer in range [-10, + 40]
    ext_humidity: integer in range [0, 100]
    ext_light: integer in range [0, 3]
        - 0: night time (off-ish)
        - 1: low_light
        - 2: medium_light
        - 3: strong_light

    user_temp: integer in range [18, 30]
    user_light: intger in range [0, 3]
        - 0: off (off-ish)
        - 1: low_light
        - 2: medium_light
        - 3: strong_light

    user_color: integer in range [0, 9]
        - 0: no color (used when the room is empty)
        - 1: red
        - 2: orange
        - 3: yellow
        - 4: green
        - 5: aqua
        - 6: blue
        - 7: purple
        - 8: fuchsia
        - 9: rgb 

'''

'''
    Supponiamo di avere 5 zone
    0: Modena 
    1: Milano
    2: Torino
    3: Roma
    4: Napoli
    
    All'interno di ogni zona ci sono x palazzi, es. 10

Facciamo il sampling delle temperature su Modena e modifichiamo gli altri accordingly

'''

''' 
    supponiamo che il sampling della temperatura avvenga 4 volte al giorno, due al mattimo e due la sera,
    la random temp è riferita alla prima temperatura registrata, le altre 3 sono mock in real time
'''

month_idx = 1

days = tempdata_op.check_days(month_idx)

# Informazioni generali, attenzione al parametro temps_range, serve tweaking
# GENERATE AN ARRAY OF 30 VALUES CONTAINING 4 TEMPS AND 4 HUMIDITY MEASURES FOR EACH DAY
temps_range = tempdata_op.get_temps_from_season(month_idx)
humidity_range = tempdata_op.get_humidity_from_season(month_idx)

# field used to retrieve data about the user from the db
user_fields = ['user_id', 'user_age', 'user_sex', 'user_task', 'user_color']

# fields used to retrieve data about the session from the db
session_fields = ['session_id', 'date', 'open_time', 'close_date',
                  'zone_id', 'building_id', 'room_id',
                  'ext_temp', 'ext_humidity', 'ext_light']

# fields used to write the full tuple to json
full_fields = ['session_id', 'date', 'open_time', 'close_time',
               'building_id', 'office_id', 'user_id',
               'user_age', 'user_sex', 'user_task',
               'ext_temp', 'ext_humidity', 'ext_light',
               'user_color', 'user_light', 'user_temp']

# n_zones = 5
zones = world_op.create_world(5)

# we select all the users from the db, then we shuffle the whole array
users = global_op.get_data_from_db(users_path, user_fields)
np.random.shuffle(users)

users_for_zone = user_op.select_users_for_zone(users, len(zones))
# lista di robe

# algoritmo per creare le varie sessioni
for day in range(1, days + 1):
    date = tempdata_op.format_date(2022, month_idx, day)
    print(" *** date: " + str(date))

    for zone_idx in range(0, len(zones)):
        local_buildings = zones[zone_idx]
        local_users = users_for_zone[zone_idx]
        ext_temp = location_op.get_temp_from_location(zone_idx, temps_range)
        ext_hum = location_op.get_hum_from_location(zone_idx, humidity_range)

        for building_idx in range(0, len(local_buildings)):
            local_rooms = local_buildings[building_idx].rooms
            local_sessions = session_op.create_sessions(date, building_idx, local_rooms, ext_temp, ext_hum)

            # for idx in range(0, len(local_users)):
            for idx in range(0, min(len(local_users), len(local_sessions))):
                curr_user = local_users[idx]
                curr_session = local_sessions[idx]

                user_temp = user_op.get_user_temp(curr_session.ext_temp,
                                                  curr_user["user_age"],
                                                  curr_user["user_sex"],
                                                  curr_user["user_task"])

                user_light = user_op.get_user_intensity(curr_session.ext_light,
                                                        curr_user["user_age"],
                                                        curr_user["user_sex"],
                                                        curr_user["user_task"])

                curr_session_fields = [curr_session.id, curr_session.date, curr_session.open_time,
                                       curr_session.close_time,
                                       np.int64(idx), np.int64(building_idx), curr_user["user_id"],
                                       curr_user["user_age"],
                                       curr_user["user_sex"], curr_user["user_task"], np.float64(curr_session.ext_temp),
                                       np.int64(curr_session.ext_humidity), np.int64(curr_session.ext_light),
                                       curr_user["user_color"], user_light, user_temp]

                curr_session_dict = {}
                for val in range(0, len(curr_session_fields)):
                    curr_session_dict[full_fields[val]] = curr_session_fields[val]

                global_op.convert_data_to_json([curr_session_dict], sessions_json_path, "sessions")