import csv
import random

class Operator:

    def __init__(self):
        print(" *** LOCATION DATA OPERATOR LOADED SUCCESSFULLY *** ")

    '''
    Supponiamo di avere 5 edifici
    0: Modena 
    1: Milano
    2: Torino
    3: Roma
    4: Napoli

    Facciamo il sampling delle temperature su Modena e modifichiamo gli altri accordingly
    
    mor_temp = random.choice(temps_range)
    mid_temp = mor_temp + 3
    aft_temp = mor_temp + random.choice(range(0, 3))
    eve_temp = mor_temp - 2

    mor_hum = random.choice(humidity_range)
    mid_hum = mor_hum - random.choice(range(0, 15))
    aft_hum = mid_hum - random.choice(range(-10, 10))
    eve_hum = mor_hum - random.choice(range(-15, 10))
    '''

    def forge_temp(self, temps_range):
        mor_temp = random.choice(temps_range)
        mid_temp = mor_temp + 3
        aft_temp = mor_temp + random.choice(range(0, 3))
        eve_temp = mor_temp - 2
        return [mor_temp, mid_temp, aft_temp, eve_temp]

    def forge_hum(self, hum_range):
        mor_hum = random.choice(hum_range)
        mid_hum = mor_hum - random.choice(range(0, 15))
        aft_hum = mid_hum - random.choice(range(-10, 10))
        eve_hum = mor_hum - random.choice(range(-15, 10))
        return [mor_hum, mid_hum, aft_hum, eve_hum]

    def adjust_data(self, data, threshold):
        adjusted_data = []
        for value in data:
            new_value = value - threshold
            if new_value > 100:
                new_value = 100
            adjusted_data.append(new_value)
        return adjusted_data

    def get_temp_from_location(self, build_idx, temps_range):
        # temp_data sarà un range
        temps = self.forge_temp(temps_range)
        if build_idx == 0:
            return temps
        elif build_idx == 1:
            return self.adjust_data(temps, random.choice(range(-1, 5)))
        elif build_idx == 2:
            return self.adjust_data(temps, random.choice(range(2, 5)))
        elif build_idx == 3:
            return self.adjust_data(temps, random.choice(range(0, 2)))
        else:
            return self.adjust_data(temps, random.choice(range(-1, 3)))

    def get_hum_from_location(self, build_idx, hum_range):
        # hum_data sarà un range
        hums = self.forge_temp(hum_range)
        if build_idx == 0:
            return hums
        elif build_idx == 1:
            return self.adjust_data(hums, random.choice(range(-8, 20)))
        elif build_idx == 2:
            return self.adjust_data(hums, random.choice(range(-10, 15)))
        elif build_idx == 3:
            return self.adjust_data(hums, random.choice(range(-3, 20)))
        else:
            return self.adjust_data(hums, random.choice(range(-5, 30)))