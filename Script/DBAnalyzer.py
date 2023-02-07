"""
    Script used for testing purposes
    [loading data from disk, shape check, data fetching, etc.]
"""

from Script.Operators import GlobalDataOperator as gdo

global_op = gdo.Operator()

train_path = '../Data/Sessions/TrainSessions'
test_path = '../Data/Sessions/TestSessions'

session_fields = ['session_id', 'date', 'open_time', 'close_time',
                  'zone_id', 'building_id', 'user_id',
                  'user_age', 'user_sex', 'user_task',
                  'ext_temp', 'ext_humidity', 'ext_light',
                  'user_color', 'user_light', 'user_temp']

train_sessions = global_op.from_json(train_path, 'sessions')
test_sessions = global_op.from_json(test_path, 'sessions')

# unique_temps = global_op.get_unique_values(train_sessions, 'user_temp')
print(" *** train_sessions: " + str(len(train_sessions)))
print(" *** test_sessions: " + str(len(test_sessions)))

