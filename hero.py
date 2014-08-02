'''
Created on 21.04.2014

@author: Tobias Ruck
'''

class ItemInventory():

    def __init__(self, matchObj):
        self.id = int(matchObj.group('id'))
        self.typeId = int(matchObj.group('typeId'))
        self.name = matchObj.group('name')
        self.placeId = int(matchObj.group('placeId'))
        self.place = matchObj.group('place')
        self.slot = matchObj.group('slot')
        self.amount = int(matchObj.group('amount'))
        
    def __str__(self):
        return type(self).__name__ + "(" + str(self.__dict__) + ")"

    def __repr__(self):
        return str(self)

class Hero():
    all_production_per_level = 6
    single_production_per_level = 20
    base_grain_production = 6
    
    def __init__(self):
        self.status = None
        self.health = None
        self.exp = None
        self.culture_points = None
        self.inventory = []

        self.item_a = None
        self.item_c = None
        
        self.skill_points = {}
        self.production_slot = None

    def get_production_bonus(self):
        assert 'production' in self.skill_points
        if self.production_slot == 0:
            bonus = [self.skill_points['production'] * self.all_production_per_level] * 4
        else:
            bonus = [0,0,0,0]
            bonus[self.production_slot-1] = self.skill_points['production'] * self.single_production_per_level
        bonus[3] += self.base_grain_production
        
        return bonus
        
    def __str__(self):
        return type(self).__name__ + "(" + str(self.__dict__) + ")"
