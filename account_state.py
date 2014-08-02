'''
Created on 02.08.2014

@author: ruckt
'''
from collections import namedtuple
from resources import Resources

import inspect

class state_tuple():
    def new_with(self, **kwargs):
        params = inspect.signature(type(self).__new__).parameters
        d = self._asdict()
        return type(self)(**{ k: kwargs.get(k, d[k]) for k in params.keys() & d.keys() })

_hs_tuple = namedtuple('HeroState', ['status', 'health', 'exp', 'skill_points', 'production_slot', 
                                     'production_bonus'])
class HeroState(_hs_tuple, state_tuple):
    '''
    '''
    
    all_production_per_level = 6
    single_production_per_level = 20
    base_grain_production = 6
    
    def __new__(cls, status, health, exp, skill_points, production_slot):
        assert 'production' in skill_points
        return _hs_tuple.__new__(cls, status, health, exp, skill_points, production_slot, cls.calculate_production_bonus(skill_points['production'], production_slot))
    
    @classmethod
    def calculate_production_bonus(cls, production_points, production_slot):
        if production_slot == 0:
            bonus = [production_points * cls.all_production_per_level] * 4
        else:
            bonus = [0,0,0,0]
            bonus[production_slot-1] = production_points * cls.single_production_per_level
        #bonus[3] += cls.base_grain_production
        
        return Resources(bonus)

_as_tuple = namedtuple('AccountState', ['production_boost', 'hero_state'])
class AccountState(_as_tuple, state_tuple):
    '''
    classdocs
    '''

    def __new__(cls, production_boost, hero_state):
        assert isinstance(hero_state, HeroState)
        return _as_tuple.__new__(cls, production_boost, hero_state)
    
if __name__ == '__main__':
    _t = namedtuple('T', ['x','y','z'])
    class T(_t, state_tuple):
        def __new__(cls, x,y):
            return _t.__new__(cls, x,y,x+y)
    
    a = T(1,2)
    print(a)
    print(a.new_with(x=3))