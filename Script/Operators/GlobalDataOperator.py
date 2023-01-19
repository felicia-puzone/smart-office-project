import json
import os

import numpy as np
from Script.Operators import UserDataOperator as udo

nv_path = './Data/OpData/NormValues.json'
uq_path = './Data/OpData/UniqueValues.json'

user_op = udo.Operator()


class Operator:

    def __init__(self):
        print(" *** GLOBAL DATA OPERATOR LOADED SUCCESSFULLY *** ")

    def encoder(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj

    def data_to_dict(self, values, fields):
        # script che funziona in tandem con quello per la conversione in json
        data_dict = {}
        for idx in range(0, len(values)):
            data_dict[fields[idx]] = self.encoder(values[idx])
        return data_dict

    def from_json(self, path, cat):
        output = []
        for filename in os.listdir(path):
            print(" *** filename: " + str(filename))
            f = os.path.join(path, filename)
            # checking if it is a file
            if os.path.isfile(f):
                curr_file = open(f)
                data = json.load(curr_file)
                for obj in data[cat]:
                    output.append(obj)
                curr_file.close()
        return output

    def ref_labels(self, array):
        # crazione di un dict dinamico
        unique_labels = list(set(array))
        ref_labels = []
        labels_dict = {}
        for idx in range(0, len(unique_labels)):
            if unique_labels[idx] not in labels_dict.keys():
                labels_dict[unique_labels[idx]] = idx

        for val in array:
            ref_labels.append(labels_dict[val])

        return ref_labels

    def normalize_data(self, array, norm_values):
        norm_array = []
        for idx in range(0, len(array)):
            if isinstance(array[idx], str):
                array[idx] = float(array[idx])
            norm_array.append(round(array[idx] / norm_values[idx], 8))
        return norm_array

    def from_temp_idx(self, idx):
        unique_values = []
        if os.path.isfile(uq_path):
            curr_file = open(uq_path)
            data = json.load(curr_file)
            for obj in data['unique_values']:
                for key in obj.keys():
                    if key == 'unique_temps':
                        unique_values = obj[key]
            curr_file.close()

        fields = []
        for field in np.array(range(0, len(unique_values))):
            fields.append(str(field))

        return self.data_to_dict(unique_values, fields)[str(idx)]

    def from_flask_in(self, data_in, target):
        norm_values = []
        if os.path.isfile(nv_path):
            curr_file = open(nv_path)
            data = json.load(curr_file)
            for obj in data['norm_values']:
                for key in obj.keys():
                    norm_values.append(obj[key])
            curr_file.close()
        else:
            print(" *** file not found *** ")
            return []

        if target == 0:
            conv_data = [user_op.check_user_age(data_in['user_age']),
                         data_in['user_sex'],
                         data_in['user_task'],
                         data_in['ext_temp'],
                         data_in['ext_humidity']]

            return np.array(self.normalize_data(conv_data, norm_values)).reshape(-1, 5)

        elif target == 1:
            conv_data = [user_op.check_user_age(data_in['user_age']),
                         data_in['user_sex'],
                         data_in['user_task'],
                         data_in['ext_light']]

            return np.array(self.normalize_data(conv_data, norm_values)).reshape(-1, 4)

        elif target == 2:
            conv_data = [user_op.check_user_age(data_in['user_age']),
                         data_in['user_sex'],
                         data_in['user_task']]

            return np.array(self.normalize_data(conv_data, norm_values)).reshape(-1, 3)
