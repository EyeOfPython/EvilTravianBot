'''
Created on 21.04.2014

@author: Tobias Ruck
'''
from account_state import HeroState

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
        
    def get_state(self):
        return HeroState(self.status, self.health, self.exp, self.skill_points, self.production_slot)
        
    def __str__(self):
        return type(self).__name__ + "(" + str(self.__dict__) + ")"
