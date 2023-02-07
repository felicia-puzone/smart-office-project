import random
import numpy as np

from Script.DataType import SessionData as sn
from Script.Operators import TemporalDataOperator as tdo
from Script.Operators import LocationDataOperator as ldo
from Script.Operators import UserDataOperator as udo

tempdata_op = tdo.Operator()
location_op = ldo.Operator()
user_op = udo.Operator()

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

    def define_sessions(self, date, building_id, off_num, temp_values, hum_values):
        sessions = []
        for off in range(0, off_num):
            timestamps = np.array(self.create_timestamps())
            for timestamp in timestamps:
                session_id = self.create_session_id(building_id, "" + str(off))
                open_time = timestamp[0]
                close_time = timestamp[1]
                ext_temp = float(tempdata_op.select_measure_from_hour(temp_values, open_time))
                ext_hum = int(tempdata_op.select_measure_from_hour(hum_values, open_time))
                ext_light = int(location_op.get_light_from_hour(open_time))

                sessions.append(sn.SessionData(date, open_time, close_time,
                                               session_id, building_id, str(off),
                                               ext_temp, ext_hum, ext_light))
        return sessions

    def session_features_asarray(self, session_data):
        return [session_data.id, session_data.date, session_data.open_time,
                session_data.close_time, session_data.building_id, session_data.office_id,
                session_data.ext_temp, session_data.ext_humidity, session_data.ext_light]

    def create_sessions(self, month_idx, zones, zone_users, fields):

        days = tempdata_op.check_days(month_idx)
        temps_range = tempdata_op.get_temps_from_season(month_idx)
        humidity_range = tempdata_op.get_humidity_from_season(month_idx)

        train_sessions = []
        test_sessions = []

        count = 0

        for day in range(1, days + 1):
            date = tempdata_op.format_date(2023, month_idx, day)
            print(" *** date: " + str(date))

            for zone_idx in range(0, len(zones)):
                print(" *** zone: " + str(zone_idx))
                local_buildings = zones[zone_idx]  # mi dice quanti buildings ci sono in questa zona
                local_users = zone_users[zone_idx]  # mi dice quali sono gli utenti che frequentano la data zona
                ext_temp = location_op.get_temp_from_location(zone_idx, temps_range)
                ext_hum = location_op.get_hum_from_location(zone_idx, humidity_range)

                for building_idx in range(0, len(local_buildings)):
                    local_rooms = local_buildings[building_idx].rooms
                    local_sessions = self.define_sessions(date, building_idx, local_rooms, ext_temp, ext_hum)

                    for idx in range(0, min(len(local_users), len(local_sessions))):
                        curr_user = local_users[idx]
                        curr_session = local_sessions[idx]

                        user_temp = user_op.get_user_temp(curr_session.ext_temp,
                                                          curr_user["user_age"],
                                                          curr_user["user_sex"],
                                                          curr_user["user_task"])

                        user_light = user_op.get_user_intensity(curr_session.ext_light,
                                                                curr_user["user_age"],
                                                                curr_user["user_sex"],
                                                                curr_user["user_task"])

                        curr_session_data = [curr_session.id,
                                             curr_session.date,
                                             curr_session.open_time,
                                             curr_session.close_time,
                                             np.int64(zone_idx),
                                             np.int64(building_idx),
                                             curr_user["user_id"],
                                             curr_user["user_age"],
                                             curr_user["user_sex"],
                                             curr_user["user_task"],
                                             np.float64(curr_session.ext_temp),
                                             np.int64(curr_session.ext_humidity),
                                             np.int64(curr_session.ext_light),
                                             curr_user["user_color"],
                                             user_light,
                                             user_temp]

                        curr_session_dict = {}
                        for val in range(0, len(curr_session_data)):
                            curr_session_dict[fields[val]] = curr_session_data[val]

                        count += 1
                        if count == 15:
                            test_sessions.append(curr_session_dict)
                            count = 0
                        else:
                            train_sessions.append(curr_session_dict)

        return train_sessions, test_sessions
