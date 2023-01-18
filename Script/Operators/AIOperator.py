import json
import numpy as np

class Operator:

    def __init__(self):
        print(" *** AI OPERATOR LOADED SUCCESSFULLY *** ")

    def predict_feature(self, model, features):
        prediction = model.predict([features])
        return np.argmax(prediction)
