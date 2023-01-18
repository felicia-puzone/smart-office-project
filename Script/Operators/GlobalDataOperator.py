import csv
import io
import json
import os

import numpy as np
import pandas as pd

from Script.Operators import UserDataOperator as udo
from datetime import datetime

user_op = udo.Operator()

nv_path = '../Data/OpData/NormValues.json'
uq_path = '../Data/OpData/UniqueValues.json'

tnorm_fields = ['tot_ages', 'tot_sexes', 'tot_tasks', 'tot_etemp', 'tot_ehum']
lnorm_fields = ['tot_ages', 'tot_sexes', 'tot_tasks', 'tot_elight']
cnorm_fields = ['tot_ages', 'tot_sexes', 'tot_tasks']

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

    def to_json(self, new_data, filename, cat):
        with open(filename, 'r+') as file:
            # First we load existing data into a dict.
            file_data = json.load(file)
            # Join new_data with file_data inside emp_details
            file_data[cat].append(new_data)
            # Sets file's current position at offset.
            file.seek(0)
            # convert back to json.
            json.dump(file_data, file, indent=4)

    def startupCheck(self, path, cat):
        if os.path.isfile(path) and os.access(path, os.R_OK):
            # checks if file exists
            print(" *** file exists and is readable")
        else:
            print(" *** creating new file: " + str(path))
            with io.open(os.path.join(path), 'w') as db_file:
                db_file.write(json.dumps({cat: []}, indent=4))
        return

    def gen_file_name(self, part, db_type):
        return '_part' + part + db_type

    def check_count(self, write_count, checkpoints, prev_path, json_path, db_type, cat):

        if write_count in checkpoints:
            curr_part = checkpoints.index(write_count)
            print(" *** sample count: " + str(write_count) + " - " + str(curr_part * 10) + "%... ")
            # 10%... 20%... 30%...
            now = datetime.now()
            current_time = now.strftime("%H:%M:%S")
            print(" *** curr_time: " + str(current_time))

            new_path = json_path + self.gen_file_name("" + str(curr_part + 1), db_type)
            self.startupCheck(new_path, cat)
            return new_path
        else:
            return prev_path

    def data_to_dict(self, values, fields):
        # script che funziona in tandem con quello per la conversione in json
        data_dict = {}
        for idx in range(0, len(values)):
            data_dict[fields[idx]] = self.encoder(values[idx])
        return data_dict

    def data_to_json(self, data, json_path, db_type, cat):

        data_len = len(data)
        step = 10
        parts = np.array(range(0, 100, step))
        checkpoints = []
        for part_idx in parts:
            checkpoints.append(int(data_len * part_idx / 100))

        write_count = 0
        prev_path = ""

        for sample in data:
            curr_path = self.check_count(write_count, checkpoints, prev_path, json_path, db_type, cat)
            if curr_path != prev_path:
                prev_path = curr_path

            for key in sample.keys():
                sample[key] = self.encoder(sample[key])

            # sample è quindi già un dict
            self.to_json(sample, prev_path, cat)
            write_count += 1

        return

    def get_local_sessions(self, array, start_idx, end_idx):
        zone_array = []
        for idx in range(start_idx, end_idx):
            zone_array.append(array[idx])
        return zone_array

    def check_world(self, array):
        prev_id = -1
        curr_office_id = 0
        curr_count = 0
        global_pointer = 0
        local_pointer = 0
        zones = []
        for session in array:
            key = session["office_id"]
            if key != curr_office_id:
                prev_id = key
                curr_office_id = key
                curr_count = 0
            if key == 0 and prev_id != -1:
                zone_sessions = self.get_local_sessions(array, global_pointer, local_pointer)
                prev_id = -1
                zones.append(zone_sessions)
                global_pointer = local_pointer
            local_pointer += 1
            curr_count += 1
            if local_pointer == len(array):
                zone_sessions = self.get_local_sessions(array, global_pointer, local_pointer)
                zones.append(zone_sessions)
                break

        return zones

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
        # creiamo un dict dinamico
        unique_labels = list(set(array))
        ref_labels = []
        labels_dict = {}
        for idx in range(0, len(unique_labels)):
            # print(" *** current_idx: " + str(idx))
            if unique_labels[idx] not in labels_dict.keys():
                labels_dict[unique_labels[idx]] = idx

        for val in array:
            ref_labels.append(labels_dict[val])

        return ref_labels

    def normalize_data(self, array, norm_values):
        norm_array = []
        for idx in range(0, len(array)):
            norm_array.append(round(array[idx] / norm_values[idx], 8))
        return norm_array

    def get_norm_values(self, array):
        tot_sum = 0
        for value in array:
            if value >= 0:
                tot_sum += value
        return tot_sum

    def get_unique_values(self, data, value):
        output = []
        for sample in data:
            output.append(sample[value])
        return list(set(output))

    def extract_data(self, array, columns, label):
        samples = []
        labels = []

        for value in array:
            curr_columns = []
            curr_label = value[label]
            for col in columns:
                curr_columns.append(value[col])

            samples.append(curr_columns)
            labels.append(curr_label)

        norm_values = []
        norm_fields = []

        if label == 'user_temp':
            norm_fields = tnorm_fields
        elif label == 'user_light':
            norm_fields = lnorm_fields
        elif label == 'user_color':
            norm_fields = cnorm_fields

        if os.path.isfile(nv_path):
            curr_file = open(nv_path)
            data = json.load(curr_file)
            for obj in data['norm_values']:
                for key in obj.keys():
                    # print(key)
                    if key in norm_fields:
                        # print(" *** in ***")
                        norm_values.append(obj[key])
            curr_file.close()

        norm_samples = []
        for sample in samples:
            norm_samples.append(self.normalize_data(sample, norm_values))

        norm_labels = self.ref_labels(labels)

        return norm_samples, norm_labels

    def convert_data(self, input, target):
        if target == 0:
            # user_temp
            return self.extract_data(input, ['user_age',
                                             'user_sex',
                                             'user_task',
                                             'ext_temp',
                                             'ext_humidity'], 'user_temp')
        elif target == 1:
            # user_light
            return self.extract_data(input, ['user_age',
                                             'user_sex',
                                             'user_task',
                                             'ext_light'], 'user_light')
        elif target == 2:
            # user_color
            return self.extract_data(input, ['user_age',
                                             'user_sex',
                                             'user_task'], 'user_color')

        return

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
        norm_samples = []
        norm_values = []

        if os.path.isfile(nv_path):
            curr_file = open(nv_path)
            data = json.load(curr_file)
            for obj in data['unique_values']:
                for key in obj.keys():
                    if key == 'unique_temps':
                        norm_values = obj[key]
            curr_file.close()

        if target == 0:
            conv_data = [user_op.check_user_age(data_in['user_age']),
                         data_in['user_sex'],
                         data_in['user_task'],
                         data_in['ext_temp'],
                         data_in['ext_humidity']]
            for data in conv_data:
                norm_samples.append(self.normalize_data(data, norm_values[0]))

            return np.array(norm_samples).reshape(-1, 5)

        elif target == 1:
            conv_data = [user_op.check_user_age(data_in['user_age']),
                         data_in['user_sex'],
                         data_in['user_task'],
                         data_in['ext_light']]
            for data in conv_data:
                norm_samples.append(self.normalize_data(data, norm_values[0]))

            return np.array(norm_samples).reshape(-1, 4)

        elif target == 2:
            conv_data = [user_op.check_user_age(data_in['user_age']),
                         data_in['user_sex'],
                         data_in['user_task']]
            for data in conv_data:
                norm_samples.append(self.normalize_data(data, norm_values[0]))

            return np.array(norm_samples).reshape(-1, 3)
