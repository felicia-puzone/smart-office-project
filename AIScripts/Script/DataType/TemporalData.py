class DayData:

    '''
        daily_temps = array of daily temperature measures (4)
        daily_humidiy = array of daily humidity measures (4)
        sessions = array of sessions (N)
    '''

    def __init__(self, daily_temps, daily_humidity):
        self.daily_temps = daily_temps
        self.daily_humidity = daily_humidity