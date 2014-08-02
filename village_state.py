'''
Created on 31.07.2014

@author: Tobias Ruck
'''
from collections import namedtuple

import db
from resources import Resources
from account_state import state_tuple

_vs_tuple = namedtuple('VillageState', ['account_state', 'resources', 'buildings', 'troops',
                                        'production', 'storage'] )
class VillageState(_vs_tuple, state_tuple):
    '''
    Describes the state of a village. Calculates production and storage accordingly.
    '''

    def __new__(cls, account_state, resources, buildings, troops):
        '''
        Constructor
        '''
        return _vs_tuple.__new__(cls, account_state, resources, buildings, troops, 
                                 cls.calculate_production(account_state, buildings), cls.calculate_storage(buildings))
        
    @classmethod
    def calculate_production(cls, account_state, buildings):
        prod = [0,0,0,0]
        bonus = [1,1,1,1]
        building_consumption = 0
        for _, gid, lvl in buildings:
            if gid:
                data = db.buildings[gid]['levels'][lvl-1]
                building_consumption += sum(db.buildings[gid]['levels'][l]['r5'] for l in range(0,lvl))
            if 0 < gid <= 4: # 1-4: woodcutter, ..., cropland
                p = data['zdata']
                prod[gid - 1] += p
            if db.building_names['sawmill'] <= gid <= db.building_names['grain_mill']:
                bonus[gid-db.building_names['sawmill']] += data['zdata']
            if gid == db.building_names['bakery']:
                bonus[3] += data['zdata']
        prod = Resources(prod)
        prod *= bonus
        prod += account_state.hero_state.production_bonus
        prod *= account_state.production_boost
        print(building_consumption)
        prod -= [0,0,0,building_consumption]
        return prod
    
    @classmethod
    def calculate_storage(cls, buildings):
        stor = Resources((0,0,0,0))
        for _, gid, lvl in buildings:
            if gid:
                p = db.buildings[gid]['levels'][lvl-1]['zdata']
            if gid == db.building_names['warehouse']: # 1-4: woodcutter, ..., cropland
                stor = stor + ([p] * 3 + [0])
            if gid == db.building_names['granary']:
                stor = stor + ([0] * 3 + [p])
        return Resources(stor)
    
if __name__ == '__main__':
    from account import Account
    import log
    account = Account((3, 'de'), 'Gl4ss')
    log.logger.log_name = 'Gl4ss'
    account.loadup()
    
    vill = next(iter(account.villages.values()))
    s = vill.get_state()
    
    print(account.get_state())
    print(s)
    print(vill.production)