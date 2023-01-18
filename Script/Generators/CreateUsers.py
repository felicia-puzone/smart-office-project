import numpy as np

from Script.Operators import GlobalDataOperator as gdo, \
    UserDataOperator as udo

user_op = udo.Operator()
global_op = gdo.Operator()

users_path = '../Data/users_part1.json'

''' 
    user_age: user age in a certain class age [0, 9]
        - 0: 18, 24 y/o 
        - 1: 25, 30 y/o 
        - 2: 31, 35 y/o 
        - 3: 36, 40 y/o 
            ...
            
    user_sex: integer in range [0, 2]
        - 0: non-specified
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

user_fields = ['user_id', 'user_age', 'user_sex', 'user_task', 'user_color']

# function user_op.generate_users(n) "creates" n users
users, unique_ages, unique_sexes, unique_tasks = user_op.generate_users(1000)

age_values = np.array(range(0, unique_ages))
sex_values = range(0, unique_ages)
task_values = np.array(range(0, unique_tasks))

# color_arr è un array di 10 elementi perchè ci sono 10 colori atm
color_values = np.array(range(0, 10))

final_users = user_op.assign_colors(users, age_values, task_values, color_values)
print(" *** users: " + str(len(final_users)))

user_dicts = user_op.get_user_dicts(final_users, user_fields)
print(" *** users_dict: " + str(len(user_dicts)))

print(" *** converting data to json... ")
global_op.data_to_json(user_dicts, users_path, "users")

print(" *** conversion completed. ")

