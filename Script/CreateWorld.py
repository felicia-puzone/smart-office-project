import WorldDataOperator as wdo

world_op = wdo.Operator()

'''
    Supponiamo di avere 5 zone
    0: Modena 
    1: Milano
    2: Torino
    3: Roma
    4: Napoli

    All'interno di ogni zona ci sono x palazzi, es. 10

Facciamo il sampling delle temperature su Modena e modifichiamo gli altri accordingly

'''

# script usato per creare zone con palazzi annessi
n_zones = 5

zones = world_op.create_world(n_zones)

print(" *** current_zones: " + str(len(zones)))