'''
Created on 31.07.2014

@author: Tobias Ruck
'''
from collections import namedtuple

import db
from resources import Resources
from account import Account

_vs_tuple = namedtuple('VillageState', ['resources', 'production', 'storage', 'buildings', 'troops'] )
class VillageState(_vs_tuple):
    '''
    Describes the state of a village. Calculates production and storage accordingly.
    '''

    def __new__(cls, resources, buildings, troops):
        '''
        Constructor
        '''
        return _vs_tuple.__new__(cls, resources, cls.calculate_production(buildings), cls.calculate_storage(buildings), buildings, troops)
        
    @classmethod
    def calculate_production(cls, buildings):
        prod = [0,0,0,0]
        for _, gid, lvl in buildings:
            if 0 < gid <= 4: # 1-4: woodcutter, ..., cropland
                p = db.buildings[gid]['levels'][lvl-1]['zdata']
                prod[gid - 1] += p
        return Resources(prod)
    
    @classmethod
    def calculate_storage(cls, buildings):
        stor = Resources((0,0,0,0))
        print(len(stor))
        for _, gid, lvl in buildings:
            if gid:
                p = db.buildings[gid]['levels'][lvl-1]['zdata']
            if gid == db.building_names['warehouse']: # 1-4: woodcutter, ..., cropland
                stor = stor + ([p] * 3 + [0])
            if gid == db.building_names['granary']:
                stor = stor + ([0] * 3 + [p])
        return Resources(stor)
    
    
if __name__ == '__main__':
    account = Account((3, 'de'), 'Gl4ss')
    account.loadup()
    
    vill = next(iter(account.villages.values()))
    
    print(VillageState(vill.resources, vill.resource_fields+vill.buildings, None))
    print(vill.production)