import numpy as np
from Script.Operators import AIOperator as aio, GlobalDataOperator as gdo, TestModelOperator as tmo
from Script.Generators import ModelSetup as ms

model_op = ms.Network(None)
global_op = gdo.Operator()
test_op = tmo.Operator()

train_path = '../Data/Sessions/TrainSessions'
test_path = '../Data/Sessions/TestSessions'

temp_model_path = '../AI/temp_model.h5'
light_model_path = '../AI/light_model.h5'
color_model_path = '../AI/color_model.h5'

test_sessions = global_op.from_json(test_path, 'sessions')
print(" *** test_sessions: " + str(len(test_sessions)))

#   0: user_temp
#   1: user_light
#   2: user_color

test_op.test_model(global_op, model_op, test_sessions, temp_model_path, 0)
test_op.test_model(global_op, model_op, test_sessions, light_model_path, 1)
test_op.test_model(global_op, model_op, test_sessions, color_model_path, 2)
