class UserData:


    def __init__(self, id, age, sex,
                 task, color=0, intensity=0, temp=0):
        self.id = id
        self.age = age
        self.sex = sex
        self.task = task
        self.color = color
        self.intensity = intensity
        self.temp = temp

    def from_json_key(self, key):
        if key == 'user_id':
            return self.id
        if key == 'user_age':
            return self.age
        if key == 'user_sex':
            return self.sex
        if key == 'user_task':
            return self.task
        if key == 'user_color':
            return self.color