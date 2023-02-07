"""
    Script used for testing purposes.

    To recursively read the entire Test Dataset uncomment these two lines, where TestSessions
    is the folder containing the .json files with the sessions.

    [test_path] = '../../Data/Sessions/TestSessions'
    test_sessions = global_op.from_json([test_path], 'sessions')

    Use the following format to simulate a json being received as a network input.

    data = {'ext_humidity': '95', 'ext_light': 3, 'ext_temp': '3', 'user_age': 50, 'user_sex': 1, 'user_task': '2'}
"""

from Script.Operators import GlobalDataOperator as gdo,\
    TestModelOperator as tmo, AIOperator as aio
from Script.Generators import ModelSetup as ms

model_op = ms.Network(None)
global_op = gdo.Operator()
test_op = tmo.Operator()
ai_op = aio.Operator()

'''
# uncomment this part if testing the [prev] models
temp_model_prev = '../AI/temp_model.h5'
light_model_prev = '../AI/light_model.h5'
color_model_prev = '../AI/color_model.h5'

nv_path_prev = '../Data/OpData/NormValues.json'
# test_path_prev = '../../Data/Sessions/TestSessions'
# test_sessions = global_op.from_json(test_path_prev, 'sessions')
'''

# uncomment this part if testing the [updated] models
temp_model_upd = '../AI/Update/temp_model.h5'
light_model_upd = '../AI/Update/light_model.h5'
color_model_upd = '../AI/Update/color_model.h5'

nv_path_upd = '../Data/OpData/Update/NormValues.json'

data = {'ext_humidity': '95', 'ext_light': 3, 'ext_temp': '3', 'user_age': 50, 'user_sex': 1, 'user_task': '2'}
# from_flask_in reshapes the data into a model-compatible type

'''
# Data conversion for the [prev] models
temp_data_prev = global_op.from_flask_in(data, 0, nv_path_prev)
light_data_prev = global_op.from_flask_in(data, 1, nv_path_prev)
color_data_prev = global_op.from_flask_in(data, 2, nv_path_prev)
'''

# Data conversion for the [updated] models
temp_data_upd = global_op.from_flask_in(data, 0, nv_path_upd)
light_data_upd = global_op.from_flask_in(data, 1, nv_path_upd)
color_data_upd = global_op.from_flask_in(data, 2, nv_path_upd)

'''
# [Prev] models loading
temp_prev = model_op.load_model(temp_model_prev)
light_prev = model_op.load_model(light_model_prev)
color_prev = model_op.load_model(color_model_prev)
'''

# Upd models loading
temp_upd = model_op.load_model(temp_model_upd)
light_upd = model_op.load_model(light_model_upd)
color_upd = model_op.load_model(color_model_upd)

'''
# Data prediction w/ prev models
t_prev = ai_op.predict_feature(temp_prev, temp_data_prev)
l_prev = ai_op.predict_feature(light_prev, light_data_prev)
c_prev = ai_op.predict_feature(color_prev, color_data_prev)
'''

# Data prediction w/ upd models
t_upd = ai_op.predict_feature(temp_upd, temp_data_upd)
l_upd = ai_op.predict_feature(light_upd, light_data_upd)
c_upd = ai_op.predict_feature(color_upd, color_data_upd)

# print(" *** Prev predictions - Temp: " + str(t_prev) + " - Light: " + str(l_prev) + " - Color: " + str(c_prev))
print(" *** Upd predictions - Temp: " + str(t_upd) + " - Light: " + str(l_upd) + " - Color: " + str(c_upd))
