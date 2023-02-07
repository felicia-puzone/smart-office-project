"""
    Python Script that loads the [sessions] dataset from disk, then trains the models.

*** UPDATE: 06/02/2023
    The core scripts have been implemented into the CreateDB.py script
    This file remains available for further testing purposes
"""
import os
import ModelSetup as ms
from Script.Operators import GlobalDataOperator as gdo

model_op = ms.Network(None)
global_op = gdo.Operator()

# working paths may be modified accordingly
train_path = '../../Data/Sessions/TrainSessions/'
test_path = '../../Data/Sessions/TestSessions/'

temp_model = '../../AI/temp_model.h5'
light_model = '../../AI/light_model.h5'
color_model = '../../AI/color_model.h5'

nv_path = '../../Data/OpData/NormValues.json'
uq_path = '../../Data/OpData/UniqueValues.json'

# 0. file check for nv_path and uq_path
if os.path.exists(nv_path):
    os.remove(nv_path)

if os.path.exists(uq_path):
    os.remove(uq_path)

# 1. Load [train sessions] from local drive (or remote DB)
train_sessions = global_op.from_json(train_path, 'sessions')

# 2. "NormValues.json" and "UniqueValues.json" creation
session_col = ['user_age', 'user_sex', 'user_task', 'ext_light', 'ext_temp', 'ext_humidity']
nv_col = ['tot_ages', 'tot_sexes', 'tot_tasks', 'tot_elight', 'tot_etemp', 'tot_ehum']
uq_fields = ['unique_temps']

nv_values = [sum(global_op.get_unique_values(train_sessions, session_col[0])),
             sum(global_op.get_unique_values(train_sessions, session_col[1])),
             sum(global_op.get_unique_values(train_sessions, session_col[2])),
             sum(global_op.get_unique_values(train_sessions, session_col[3])),
             sum(global_op.get_unique_values(train_sessions, session_col[4])),
             sum(global_op.get_unique_values(train_sessions, session_col[5]))]

nv_dict = global_op.data_to_dict(nv_values, nv_col)

global_op.check_file(nv_path, 'norm_values')
global_op.to_json(nv_dict, nv_path, 'norm_values')

unique_temps = global_op.get_unique_values(train_sessions, 'user_temp')
unique_dict = global_op.data_to_dict([unique_temps], uq_fields)

global_op.check_file(uq_path, 'unique_fields')
global_op.to_json(unique_dict, uq_path, 'unique_fields')

print(" *** [train]_sessions: " + str(len(train_sessions)))

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


