from Script.Operators import AIOperator as aio, GlobalDataOperator as gdo
from Script.Generators import ModelSetup as ms

model_op = ms.Network(None)
global_op = gdo.Operator()
ai_op = aio.Operator()

train_path = '../Data/Sessions/TrainSessions'
dict_path = '../Data/OpData/UniqueValues.json'

unique_fields = ['unique_temps']

train_sessions = global_op.from_json(train_path, 'sessions')

unique_elights = global_op.get_unique_values(train_sessions, 'ext_light')
print(" *** unique_lights: " + str(unique_elights))

'''
unique_dict = global_op.data_to_dict([unique_temps], unique_fields)
print(" *** unique_dict: " + str(unique_dict))
global_op.startupCheck(dict_path, 'unique_values')
global_op.to_json(unique_dict, dict_path, 'unique_values')
'''