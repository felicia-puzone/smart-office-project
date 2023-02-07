import random
import numpy as np

from Script.DataType.UserData import UserData


class Operator:

    def __init__(self):
        print(" *** USER DATA OPERATOR LOADED SUCCESSFULLY *** ")

    '''
        - 0: intrattendimento
        - 1: studio
        - 2: lavoro d'ufficio
        - 3: lavoro manuale
        - 4: risorse umane
        - 5: servizi pubblici
        
        ext_temp: integer in range [-10, + 40]
        ext_humidity: integer in range [0, 100]
        ext_light: integer in range [0, 3]
            - 0: night time (off-ish)
            - 1: low_light
            - 2: medium_light
            - 3: strong_light
        
        user_temp: integer in range [18, 30]
        user_light: intger in range [0, 3]
            - 0: off (off-ish)
            - 1: low_light
            - 2: medium_light
            - 3: strong_light
    
        user_color: integer in range [0, 9]
            - 0: no color (used when the room is empty)
            - 1: red
            - 2: orange
            - 3: yellow
            - 4: green
            - 5: aqua
            - 6: blue
            - 7: purple
            - 8: fuchsia
            - 9: rgb       
    '''

    def generate_users(self, amount):
        users = []

        user_ages = []
        user_sexes = []
        user_tasks = []

        for value in range(0, amount):
            uid = "UID" + str(value)
            age = self.check_user_age(random.randint(18, 99))
            sex = random.randint(0, 2)

            if age in range(0, 7):
                # allora può sia lavorare che studiare
                task = random.randint(0, 5)
            else:
                task = random.randint(0, 2)

            users.append(UserData(uid, age, sex, task))

            user_ages.append(age)
            user_sexes.append(sex)
            user_tasks.append(task)

        unique_ages = len(list(set(user_ages)))
        unique_sexes = len(list(set(user_sexes)))
        unique_tasks = len(list(set(user_tasks)))

        print(" *** unique_ages: " + str(set(user_ages)) + " - amount: " + str(unique_ages))
        print(" *** unique_sexes: " + str(set(user_sexes)) + " - amount: " + str(unique_sexes))
        print(" *** unique_tasks: " + str(set(user_tasks)) + " - amount: " + str(unique_tasks))

        return users, unique_ages, unique_sexes, unique_tasks

    def filter_users(self, users, value, idx):
        sel_users = []
        for el in users:
            if idx == 1:
                if el.age == value:
                    sel_users.append(el)
            elif idx == 2:
                if el.sex == value:
                    sel_users.append(el)
            elif idx == 3:
                if el.task == value:
                    sel_users.append(el)
        return sel_users

    def assign_colors(self, users, age_values, task_values, color_values):
        # effettuo lo shuffle degli age_values per evitare bias
        np.random.shuffle(age_values)

        ages = [age_values[0:5], age_values[5:10]]
        output_users = []

        for age_set in ages:
            for value in age_set:
                curr_users = self.filter_users(users, value, 1)
                for task in task_values:
                    curr_colors = color_values[1:]
                    np.random.shuffle(curr_colors)
                    task_users = self.filter_users(curr_users, task, 3)
                    for user in task_users:
                        user.color = curr_colors[user.sex]
                        output_users.append(self.user_features_asarray(user))
        return users

    def adjust_temp_from_task(self, feature, user_task):
        if user_task == 0 or user_task == 1 or user_task == 2:
            threshold = 2
        elif user_task == 3:
            threshold = 3
        elif user_task == 4:
            threshold = 4
        else:
            threshold = 3
        return feature + threshold

    def get_user_temp(self, ext_temp, user_age, user_sex, user_task):
        if ext_temp < 20:
            if user_age in range(0, 2):
                return self.adjust_temp_from_task(20 + user_sex, user_task)
            elif user_age in range(2, 4):
                return self.adjust_temp_from_task(22 + user_sex, user_task)
            elif user_age in range(4, 6):
                return self.adjust_temp_from_task(24 + user_sex, user_task)
            elif user_age in range(6, 8):
                return self.adjust_temp_from_task(21 + user_sex, user_task)
            else:
                return self.adjust_temp_from_task(23 + user_sex, user_task)
        else:
            return ext_temp

    def adjust_intensity_from_task(self, feature, user_sex, user_task):
        if feature == 0:
            if user_task in range(0, 3):
                return 3 - user_sex
            elif user_task == 3:
                return 3 - user_sex
            elif user_task == 4:
                return abs(1 - user_sex)
            else:
                return 2 - user_sex

        elif feature == 1:
            # caso low_light esterno
            if user_task in range(0, 3):
                return 3 - user_sex
            elif user_task == 3:
                return 2 - user_sex
            elif user_task == 4:
                return 2 - user_sex
            else:
                return 2 - user_sex

        elif feature == 2:
            # caso medium_light esterno
            if user_task in range(0, 3):
                return 2 - user_sex
            elif user_task == 3:
                return 3 - user_sex
            elif user_task == 4:
                return 1 - user_sex
            else:
                return 2 - user_sex

        elif feature == 3:
            # caso strong_light esterno
            if user_task in range(0, 3):
                return 3 - user_sex
            elif user_task == 3:
                return 3 - user_sex
            elif user_task == 4:
                return 2 - user_sex
            else:
                return 2 - user_sex

    def get_user_intensity(self, ext_light, user_age, user_sex, user_task):
        if user_age in range(0, 2):
            return self.adjust_intensity_from_task(ext_light, user_sex, user_task)
        elif user_age in range(2, 4):
            return self.adjust_intensity_from_task(ext_light, user_sex, user_task)
        elif user_age in range(4, 6):
            return self.adjust_intensity_from_task(ext_light, user_sex, user_task)
        elif user_age in range(6, 8):
            return self.adjust_intensity_from_task(ext_light, user_sex, user_task)
        else:
            return self.adjust_intensity_from_task(ext_light, user_sex, user_task)

    def check_user_age(self, age):
        if age in range(18, 25):
            return 0
        if age in range(25, 30):
            return 1
        if age in range(30, 35):
            return 2
        if age in range(35, 40):
            return 3
        if age in range(40, 50):
            return 4
        if age in range(50, 60):
            return 5
        if age in range(60, 70):
            return 6
        if age in range(70, 80):
            return 7
        else:
            return 9

    def user_features_asarray(self, user_data):
        return [user_data.id, user_data.age, user_data.sex, user_data.task, user_data.color]

    def select_users_for_zone(self, users, zones):
        step = int(len(users) / zones)
        users_for_zone = []
        for i in range(0, len(users), step):
            start_idx = i
            end_idx = i + step
            local_users = users[start_idx:end_idx]
            users_for_zone.append(local_users)
            i += end_idx

        return users_for_zone

    def get_user_dicts(self, users, user_fields):
        dicts = []
        for user in users:
            curr_user_dict = {}
            for val in range(0, len(user_fields)):
                curr_user_dict[user_fields[val]] = user.from_json_key(user_fields[val])
            dicts.append(curr_user_dict)
        return dicts
