# appunti

'''
    date: yyyy/mm/dd
    
    session_id: unique value assigned to each session in the system
    session_open_time: hh:mm:ss
    session_close_time: hh:mm:ss
    
    building_id: integer in range [0, 4] as we have 5 unique buildings
    room_id: integer in range [0, x], where x is the number of rooms in a certain building
    user_id: unique value assigned to each user in the system
    
    user_age: user age in a certain class age
        - 0: 18, 24 y/o 
        - 1: 25, 30 y/o 
        - 2: 31, 35 y/o 
        - 3: 36, 40 y/o 
            ...
            
    user_sex: integer in range [0, 2]
    
    user_task: integer in range [0, 5]
        - 0: entertainment
        - 1: study-related tasks
        - 2: office work
        - 3: manual work
        - 4: human resources
        - 5: public services
        
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

field_names = ['date', 'session_id', 'session_open_time', 'session_close_time',
               'building_id', 'room_id', 'user_id',
               'user_age', 'user_sex', 'user_task',
               'ext_temp', 'ext_humidity', 'ext_light',
               'user_temp', 'user_light', 'user_color']
