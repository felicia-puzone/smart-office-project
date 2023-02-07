"""
    Python Script that creates the DB which will be used to train the AI on
    Previously split as "CreateUsers.py" and "CreateSessions.py"
"""
import os

import numpy as np
import ModelSetup as ms

from Script.Operators import TemporalDataOperator as tdo, \
    WorldDataOperator as wdo, GlobalDataOperator as gdo, \
    LocationDataOperator as ldo, \
    UserDataOperator as udo, \
    SessionDataOperator as sdo


temporal_op = tdo.Operator()
location_op = ldo.Operator()
session_op = sdo.Operator()
global_op = gdo.Operator()
user_op = udo.Operator()
world_op = wdo.Operator()

model_op = ms.Network(None)

db_type = '.json'

'''
    The following paths will be used in part [#5] of this code.
    Uncomment that entire part [#5] to be able to save the generated sessions to file,
    otherwise they will be deleted after training the models.
    
'''

# Uncomment this part to create a DB which will be used to simulate the system's update
# Paths may be modified accordingly
train_path = '../../Data/Sessions/TrainSessionsExtra/train_sessions'
test_path = '../../Data/Sessions/TestSessionsExtra/test_sessions'

# fields that will be used in the array to dict conversion
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

'''
First part of the script involves the [Users] creation
'''

# function user_op.generate_users(n) creates n [int] users
raw_users, unique_ages, unique_sexes, unique_tasks = user_op.generate_users(1000)

# values that will be used to assign certain colors to certain user categories
age_values = np.array(range(0, unique_ages))
sex_values = range(0, unique_ages)
task_values = np.array(range(0, unique_tasks))

# color_arr contains 10 elements representing the 10 colors currently set in the DB
color_values = np.array(range(0, 10))

col_users = user_op.assign_colors(raw_users, age_values, task_values, color_values)
user_dicts = user_op.get_user_dicts(col_users, user_fields)
print(" *** users created: " + str(len(user_dicts)))

'''
Second part of the script involves the [Sessions] creation
'''

# function world_op.create_world(n) creates n [int]_zones
zones = world_op.create_world(5)

# we shuffle the previously created user_dicts to add a degree of randomness to the users-zones split
np.random.shuffle(user_dicts)

# sessions = session_op.

users_for_zone = user_op.select_users_for_zone(user_dicts, len(zones))
print(" *** users for zone: " + str(len(users_for_zone)))
print(" *** users for zone: " + str(np.array(users_for_zone).shape))

# month_idx is the month number (1 - 12)
month_idx = 2
train_sessions, test_sessions = session_op.create_sessions(month_idx, zones, users_for_zone, full_fields)

print(" *** [train] sessions: " + str(len(train_sessions)))
print(" *** [test] sessions: " + str(len(test_sessions)))

# disk paths containing the network models
temp_model = '../../AI/temp_model.h5'
light_model = '../../AI/light_model.h5'
color_model = '../../AI/color_model.h5'

nv_path = '../../Data/OpData/Extra/NormValues.json'
uq_path = '../../Data/OpData/Extra/UniqueValues.json'

# 1. file check for nv_path and uq_path
if os.path.exists(nv_path):
    os.remove(nv_path)

if os.path.exists(uq_path):
    os.remove(uq_path)

# 2. "NormValues.json" and "UniqueValues.json" creation

# [mod_col] is an array containing the keys which will be used to extract values from the session dicts
# [nvr_col] is an array containing the keys which will be used to create the NormValues.json dict
# [unq_col] is an array containing the keys which will be used to create the UniqueValues.json dict

mod_col = ['user_age', 'user_sex', 'user_task', 'ext_light', 'ext_temp', 'ext_humidity']
nrv_col = ['tot_ages', 'tot_sexes', 'tot_tasks', 'tot_elight', 'tot_etemp', 'tot_ehum']
unq_col = ['unique_temps']

nv_values = [sum(global_op.get_unique_values(train_sessions, mod_col[0])),
             sum(global_op.get_unique_values(train_sessions, mod_col[1])),
             sum(global_op.get_unique_values(train_sessions, mod_col[2])),
             sum(global_op.get_unique_values(train_sessions, mod_col[3])),
             sum(global_op.get_unique_values(train_sessions, mod_col[4])),
             sum(global_op.get_unique_values(train_sessions, mod_col[5]))]

nv_dict = global_op.data_to_dict(nv_values, nrv_col)

global_op.check_file(nv_path, 'norm_values')
global_op.to_json(nv_dict, nv_path, 'norm_values')

unique_temps = global_op.get_unique_values(train_sessions, 'user_temp')
unique_dict = global_op.data_to_dict([unique_temps], unq_col)

global_op.check_file(uq_path, 'unique_fields')
global_op.to_json(unique_dict, uq_path, 'unique_fields')

print(" *** [train]_sessions generated: " + str(len(train_sessions)))

# 3. Samples and labels extraction/normalization
#   0: target [user_temp]
#   1: target [user_light]
#   2: target [user_color]

temp_samples, temp_labels = global_op.convert_data(train_sessions, 0, nv_path)
light_samples, light_labels = global_op.convert_data(train_sessions, 1, nv_path)
color_samples, color_labels = global_op.convert_data(train_sessions, 2, nv_path)

# 4. Models creation
temp_model = model_op.manage_model(temp_samples, temp_labels, temp_model, 1)
print(" *** [temp_model] ready *** ")
light_model = model_op.manage_model(light_samples, light_labels, light_model, 1)
print(" *** [light_model] ready *** ")
color_model = model_op.manage_model(color_samples, color_labels, color_model, 2)
print(" *** [color_model] ready *** ")

'''
# 5. Train/Test session save to file
print(" *** saving [train] and [test] sessions to json")
global_op.data_to_json(train_sessions, train_path, db_type, "sessions")
global_op.data_to_json(test_sessions, test_path, db_type, "sessions")
print(" *** saving complete *** ")
'''
