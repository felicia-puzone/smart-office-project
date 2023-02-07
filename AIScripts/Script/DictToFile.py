"""
    Script used to build the "NormValues.json" and "UniqueValues.json" files,
    used for normalizing data (NormValues) and retrieving real values after
    performing inference on the temp_model (UniqueValues)

*** UPDATE: 06/02/2023
    The core scripts have been implemented into the CreateDB.py script
    This file remains available for further testing purposes
"""

from Script.Operators import GlobalDataOperator as gdo

global_op = gdo.Operator()

sessions_path = '../Data/Sessions/TrainSessionsUpdate'
nv_path = '../Data/OpData/Update/NormValues.json'
uq_path = '../Data/OpData/Update/UniqueValues.json'

unique_fields = ['unique_temps']

train_sessions = global_op.from_json(sessions_path, 'sessions')

nv_columns = ['tot_ages', 'tot_sexes', 'tot_tasks', 'tot_elight', 'tot_etemp', 'tot_ehum']

nv_values = [sum(global_op.get_unique_values(train_sessions, 'user_age')),
             sum(global_op.get_unique_values(train_sessions, 'user_sex')),
             sum(global_op.get_unique_values(train_sessions, 'user_task')),
             sum(global_op.get_unique_values(train_sessions, 'ext_light')),
             sum(global_op.get_unique_values(train_sessions, 'ext_temp')),
             sum(global_op.get_unique_values(train_sessions, 'ext_humidity'))]

nv_dict = global_op.data_to_dict(nv_values, nv_columns)
print("  *** nv_dict" + str(nv_dict))

global_op.check_file(nv_path, 'norm_values')
global_op.to_json(nv_dict, nv_path, 'norm_values')

unique_temps = global_op.get_unique_values(train_sessions, 'user_temp')
print(" *** unique_[user]temps: " + str(unique_temps))

unique_dict = global_op.data_to_dict([unique_temps], unique_fields)
print(" *** unique_dict: " + str(unique_dict))

global_op.check_file(uq_path, 'unique_fields')
global_op.to_json(unique_dict, uq_path, 'unique_fields')
