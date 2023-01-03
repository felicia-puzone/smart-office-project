import csv
import json

import numpy as np
import pandas as pd

'''
    Script used to write data to and read data from file (csv)
'''


class Operator:

    def __init__(self):
        print(" *** GLOBAL DATA OPERATOR LOADED SUCCESSFULLY *** ")

    def get_value_pairs(self, features, field_names):
        value_dict = {}
        for idx in range(0, len(field_names)):
            value_dict.update({field_names[idx]: features[idx]})
        return value_dict

    def write_data_to_db(self, features, field_names, file_path):
        with open(file_path, 'w') as csv_file:
            csv_writer = csv.DictWriter(csv_file, fieldnames=field_names)
            csv_writer.writeheader()
            for feature_list in features:
                feature_dict = self.get_value_pairs(feature_list, field_names)
                csv_writer.writerow(feature_dict)
            csv_file.close()

    def select_columns(self, columns, fields):
        values = []
        idx = 0
        for col in columns:
            for field in fields:
                if col == field:
                    values.append(idx)
                    idx += 1
        return values

    def encoder(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, str):
            return str(obj)

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

    def convert_data_to_json(self, data, json_path, cat):
        '''
        :param data: a list/array of dictionaries
        :param json_path: path of the target json_file
        :param cat: "label" of the json file
        :return: none
        '''
        for sample in data:
            for key in sample.keys():
                sample[key] = self.encoder(sample[key])
                # una volta finito quel robo avrò un dizionario pronto per essere convertito
            self.to_json(sample, json_path, cat)
        return

    def get_data_from_db(self, db_name, fields):
        df = pd.read_csv(db_name)
        columns = self.select_columns(df.columns, fields)
        new_df = pd.DataFrame([])
        for col in columns:
            samples = df[df.columns[col]]
            new_df[col] = samples

        samples = []
        for idx in range(0, len(new_df)):
            dict_out = {}
            row_values = new_df.iloc[idx]
            for val in range(0, len(row_values)):
                dict_out[fields[val]] = row_values[val]

            samples.append(dict_out)

        return samples
