class Operator:

    def __init__(self):
        print(" *** SESSION DATA OPERATOR LOADED SUCCESSFULLY *** ")

    def format_date(self, year, month, day):
        if month < 10:
            month_string = "0" + str(month)
        else:
            month_string = str(month)
        if day < 10:
            day_string = "0" + str(day)
        else:
            day_string = str(day)

        return str(year) + "/" + month_string + "/" + day_string

    def check_days(self, month):
        thirty = [4, 6, 9, 11]
        if month in thirty:
            return 30
        elif month == 2:
            return 28
        else:
            return 31

    def check_season(self, month):
        # ricordiamo che la funzione range di python non include l'ultimo indice
        months_spring = range(3, 6)
        months_summer = range(6, 9)
        months_autumn = range(9, 12)

        if month in months_spring:
            return 0
        elif month in months_summer:
            return 1
        elif month in months_autumn:
            return 2
        else:
            return 3

    def get_temps_from_season(self, month):
        if self.check_season(month) == 0:
            return range(8, 19)
        if self.check_season(month) == 1:
            return range(19, 40)
        if self.check_season(month) == 2:
            return range(5, 14)
        else:
            return range(-3, 10)

    def select_measure_from_hour(self, measures, hour):
        if hour in range(8, 10):
            return measures[0]
        elif hour in range(10, 14):
            return measures[1]
        elif hour in range(14, 18):
            return measures[2]
        else:
            return measures[3]

    def get_humidity_from_season(self, month):
        if self.check_season(month) == 0:
            return range(30, 85)
        if self.check_season(month) == 1:
            return range(15, 60)
        if self.check_season(month) == 2:
            return range(40, 90)
        if self.check_season(month) == 3:
            return range(50, 95)

    def get_light_from_hour(self, hh):
        '''

        ext_light: integer in range [0, 3]
        - 0: night time (off-ish)
        - 1: low_light
        - 2: medium_light
        - 3: strong_light

        '''

        if hh in range(6, 9):
            return 1
        if hh in range(10, 16):
            return 3
        if hh in range(16, 18):
            return 2
        else:
            return 0