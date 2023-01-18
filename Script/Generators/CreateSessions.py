import numpy as np

from Script.Operators import TemporalDataOperator as tdo, \
    WorldDataOperator as wdo, GlobalDataOperator as gdo, \
    LocationDataOperator as ldo, \
    UserDataOperator as udo, \
    SessionDataOperator as sdo

tempdata_op = tdo.Operator()
location_op = ldo.Operator()
session_op = sdo.Operator()
global_op = gdo.Operator()
user_op = udo.Operator()
world_op = wdo.Operator()

db_type = '.json'

users_path = '../../Data/Users/'
train_sessions_path = '../Data/Sessions/train_sessions'
test_sessions_path = '../Data/Sessions/test_sessions'

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

    Il sampling della temperatura avviene 4 volte al giorno, due al mattimo e due la sera,
    la random temp è riferita alla prima temperatura registrata, le altre 3 sono mock in real time
'''

# field used to retrieve data about the user from the db
user_fields = ['user_id',
               'user_age',
               'user_sex',
               'user_task',
               'user_color']

# fields used to retrieve data about the session from the db
session_fields = ['session_id',
                  'date',
                  'open_time',
                  'close_date',
                  'zone_id',
                  'building_id',
                  'room_id',
                  'ext_temp',
                  'ext_humidity',
                  'ext_light']

# fields used to write the full tuple to json
full_fields = ['session_id',
               'date',
               'open_time',
               'close_time',
               'zone_id',
               'building_id',
               'user_id',
               'user_age',
               'user_sex',
               'user_task',
               'ext_temp',
               'ext_humidity',
               'ext_light',
               'user_color',
               'user_light',
               'user_temp']

# n_zones = 5
zones = world_op.create_world(5)
print(" *** len_zones: " + str(len(zones)))

# we select all the users from the db, then we shuffle the whole array
# users = global_op.get_data_from_db(users_path, user_fields)

upath = users_path + db_type
print(" *** upath: " + str(upath))

users = global_op.from_json(users_path, 'users')

print(" *** users: " + str(len(users)))

np.random.shuffle(users)

# sessions = session_op.

users_for_zone = user_op.select_users_for_zone(users, len(zones))
print(" *** users for zone: " + str(len(users_for_zone)))
print(" *** users for zone: " + str(np.array(users_for_zone).shape))

month_idx = 1
train_sessions, test_sessions = session_op.create_sessions(month_idx, zones, users_for_zone, full_fields)

print(" *** train sessions created: " + str(len(train_sessions)))
print(" *** test sessions created: " + str(len(test_sessions)))

print(" *** converting train_sessions to json")
global_op.data_to_json(train_sessions, train_sessions_path, db_type, "sessions")

print(" *** converting test_sessions to json")
global_op.data_to_json(test_sessions, test_sessions_path, db_type, "sessions")
# global_op.convert_data_to_json([curr_session_dict], test_sessions_json_path, "sessions")
