from Script.Operators import GlobalDataOperator as gdo

global_op = gdo.Operator()

users_json_path = '../Data/Users/users.json'
sessions_json_path = '../Data/Sessions/train_sessions.json'
train_path = '../Data/Sessions/TrainSessions'

full_fields = ['session_id', 'date', 'open_time', 'close_time',
               'zone_id', 'building_id', 'user_id',
               'user_age', 'user_sex', 'user_task',
               'ext_temp', 'ext_humidity', 'ext_light',
               'user_color', 'user_light', 'user_temp']

# train_sessions = global_op.from_json(train_path, 'sessions')
# unique_temps = global_op.get_unique_values(train_sessions, 'user_temp')
# print(" *** unique_temps: " + str(unique_temps))

yeet = global_op.from_flask_idx(0)
print(" *** yeet: " + str(yeet))
