import csv
import random
import numpy as np

import SessionData as sn
import TemporalDataOperator as tdo

tempdata_op = tdo.Operator()

last_session_val = 0


class Operator:
    '''
        session_id: unique value assigned to each session in the system
        session_open_time: hh:mm:ss
        session_close_time: hh:mm:ss

        building_id: integer in range [0, 4] as we have 5 unique buildings
        room_id: integer in range [0, x], where x is the number of rooms in a certain building
        user_id: unique value assigned to each user in the system
    '''

    def __init__(self):
        print(" *** SESSION DATA OPERATOR LOADED SUCCESSFULLY *** ")

    def check_availability(self, office_hours, av, session_start, session_end):
        for session_hour in range(session_start, session_end):
            if av[np.where(office_hours == session_hour)[0]] != 1:
                return []
            else:
                av[np.where(office_hours == session_hour)[0]] = 0
        return av

    def create_session_id(self, building_id, off_id):
        global last_session_val
        curr_session_val = last_session_val
        last_session_val = curr_session_val + random.choice(range(0, 3))
        return "" + str(building_id) + str(off_id) + str(curr_session_val)

    def create_timestamps(self):
        start_time = 8
        end_time = 20
        office_hours = np.array(range(start_time, end_time))
        av_arr = np.ones(len(office_hours))
        timestamps = []
        for index in range(0, 100):
            session_start = random.choice(range(start_time, end_time))
            session_length = random.choice(range(0, end_time - session_start))
            if session_length == 0:
                session_length = 1
            session_end = session_start + session_length
            available_hours = self.check_availability(office_hours, av_arr, session_start, session_end)
            if len(available_hours) == 0:
                continue
            else:
                timestamps.append([session_start, session_end])
                av_arr = available_hours
        timestamps.sort(key=lambda timestamps: timestamps[0])
        return timestamps

    def create_sessions(self, date, building_id, off_num, temp_values, hum_values):
        sessions = []
        for off in range(0, off_num):
            timestamps = np.array(self.create_timestamps())
            # print(" *** timestamps: " + str(timestamps.shape))
            for timestamp in timestamps:
                session_id = self.create_session_id(building_id, "" + str(off))
                # building_id come parametro
                # room_id come parametro

                open_time = timestamp[0]
                close_time = timestamp[1]

                ext_temp = float(tempdata_op.select_measure_from_hour(temp_values, open_time))
                ext_hum = int(tempdata_op.select_measure_from_hour(hum_values, open_time))
                ext_light = int(tempdata_op.get_light_from_hour(open_time))

                sessions.append(sn.SessionData(date, open_time, close_time,
                                               session_id, building_id, str(off),
                                               ext_temp, ext_hum, ext_light))
        return sessions

    def session_features_asarray(self, session_data):
        return [session_data.id, session_data.date, session_data.open_time,
                session_data.close_time, session_data.building_id, session_data.office_id,
                session_data.ext_temp, session_data.ext_humidity, session_data.ext_light]
