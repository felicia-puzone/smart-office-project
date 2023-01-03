import random
import BuildingData as bd


class Operator:

    def __init__(self):
        print(" *** WORLD DATA OPERATOR LOADED SUCCESSFULLY *** ")

    def create_world(self, n_zones):
        zones = []
        for zone_id in range(0, n_zones):
            # ciascuna zona avrà da 3 a 10 edifici
            local_buildings = random.choice(range(3, 11))
            buildings = []
            for building_id in range(0, local_buildings):
                # ciascun palazzo avrà da 3 a 50 stanze
                local_rooms = random.choice(range(3, 50))
                building = bd.BuildingData(building_id, local_rooms)
                # quindi ora per ogni building devo creare le sessioni
                buildings.append(building)
            zones.append(buildings)
        return zones