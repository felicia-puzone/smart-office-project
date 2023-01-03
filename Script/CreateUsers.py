import os
import random

import numpy as np

import UserData as user

import UserDataOperator as udo
import GlobalDataOperator as gdo

user_op = udo.Operator()
global_op = gdo.Operator()

users_path = '../Data/users.csv'
json_path = '../Data/users.json'

''' 
    user_age: user age in a certain class age [0, 9]
        - 0: 18, 24 y/o 
        - 1: 25, 30 y/o 
        - 2: 31, 35 y/o 
        - 3: 36, 40 y/o 
            ...
            
    user_sex: integer in range [0, 2]
        - 0: fluid
        - 1: male
        - 2: female
    
    user_task: integer in range [0, 5]
        - 0: intrattendimento
        - 1: studio
        - 2: lavoro d'ufficio
        - 3: lavoro manuale
        - 4: risorse umane
        - 5: servizi pubblici
'''

field_names = ['user_id', 'user_age', 'user_sex', 'user_task', 'user_color']

global_users = []

# script che mi crea 1000 utenti random
for value in range(0, 10000):
    id = "UID" + str(value)
    age = user_op.check_user_age(random.randint(18, 99))
    sex = random.randint(0, 2)
    if age in range(0, 7):
        # allora può sia lavorare che studiare
        task = random.randint(0, 5)
    else:
        task = random.randint(0, 2)

    global_users.append(user.UserData(id, age, sex, task))


def filter_users(global_users, value, idx):
    filtered_users = []
    for el in global_users:
        if idx == 1:
            if el.age == value:
                filtered_users.append(el)
        elif idx == 2:
            if el.sex == value:
                filtered_users.append(el)
        elif idx == 3:
            if el.task == value:
                filtered_users.append(el)
    return filtered_users


# script che mi crea le categorie di colore in base agli utenti
age_arr = np.array(range(0, 10))
color_arr = np.array(range(0, 10))
sex_arr = range(0, 3)
task_arr = np.array(range(0, 6))

# faccio lo shuffle dei dati bcus reasons
np.random.shuffle(age_arr)

# dividiamo l'age arr in due gruppi
user_ages = [age_arr[0:5], age_arr[5:10]]

color_users = []

# age_set è una ipercategoria
for age_set in user_ages:
    # print(" *** age_category: " + str(age_set))
    for age in age_set:

        filt_users = filter_users(global_users, age, 1)
        # print(" *** users for age class: " + str(age) + " - " + str(len(filt_users)))

        for task in task_arr:
            curr_colors = color_arr[1:]
            np.random.shuffle(curr_colors)
            task_users = filter_users(filt_users, task, 3)
            # print(" *** users for task: " + str(task) + " - " + str(len(task_users)))

            for user in task_users:
                # user[3] corrisponde al sesso
                user.color = curr_colors[user.sex]
                color_users.append(user_op.user_features_asarray(user))


global_op.write_data_to_db(color_users, field_names, users_path)
print(" *** users.csv created *** ")

users = global_op.get_data_from_db(users_path, field_names)

global_op.convert_data_to_json(users, json_path, "users")
print(" *** users.csv converted to .json")

