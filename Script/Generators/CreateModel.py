import ModelSetup as ms
import numpy as np

from Script.Operators import GlobalDataOperator as gdo

model_op = ms.Network(None)
global_op = gdo.Operator()

# train_path = '../Data/Sessions/train_sessions.json'
# test_path = '../Data/Sessions/test_sessions.json'

train_path = '../../Data/Sessions/TrainSessions/'
test_path = '../../Data/Sessions/TestSessions/'

temp_model = '../AI/temp_model.h5'
light_model = '../AI/light_model.h5'
color_model = '../AI/color_model.h5'

# 1. Leggere sessioni dal disco (creazione sample)
train_sessions = global_op.from_json(train_path, 'sessions')

# test_sessions = global_op.from_json(test_path, 'sessions')

# 2. Estrarre dati per testing e dump su disco
print(" *** train_sessions: " + str(len(train_sessions)))
# print(" *** test_sessions: " + str(len(test_sessions)))

# 2. Estrazione e normalizzazione di samples e labels
#   0: estrazione dati per user_temp
#   1: estrazione dati per user_light
#   2: estrazione dati per user_color

# temp_samples, temp_labels = global_op.convert_data(train_sessions, 0)
# print(" *** temp samples shape: " + str(np.array(temp_samples).shape))
# light_samples, light_labels = global_op.convert_data(train_sessions, 1)
# print(" *** light samples shape: " + str(np.array(light_samples).shape))
color_samples, color_labels = global_op.convert_data(train_sessions, 2)
print(" *** color samples shape: " + str(np.array(color_samples).shape))

# 3. Costruzione del modello
# temp_model = model_op.manage_network(temp_samples, temp_labels, temp_model)
# print(" *** temp_model ready *** ")
# light_model = model_op.manage_network(light_samples, light_labels, light_model)
# print(" *** light_model ready *** ")
color_model = model_op.manage_network(color_samples, color_labels, color_model)
print(" *** color_model ready *** ")
