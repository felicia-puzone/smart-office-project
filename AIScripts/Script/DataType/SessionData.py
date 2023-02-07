class SessionData:
    '''
        session_id: unique value assigned to each session in the system
        session_open_time: hh:mm:ss
        session_close_time: hh:mm:ss

        building_id: integer in range [0, 4] as we have 5 unique buildings
        room_id: integer in range [0, x], where x is the number of rooms in a certain building
        user_id: unique value assigned to each user in the system
    '''

    def convert_to_time_string(self, time):
        if time <= 9:
            return "0" + str(time) + ":00:00"
        return str(time) + ":00:00"

    def __init__(self, date, open_time, close_time,
                 id, building_id, room_id,
                 ext_temp, ext_humidity, ext_light):

        # info timestamp
        self.date = date
        self.open_time = self.convert_to_time_string(open_time)
        self.close_time = self.convert_to_time_string(close_time)

        # info sessione
        self.id = id
        self.building_id = building_id
        self.room_id = room_id

        # roba dall'esterno
        self.ext_temp = ext_temp
        self.ext_humidity = ext_humidity
        self.ext_light = ext_light
        self.ext_temp = ext_temp
