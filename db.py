import pickle

def read_csv():
    import csv
    

    reader = csv.reader(open("data/builds.csv", "r"), delimiter=',')

    buildings = { }

    next(reader)

    for gid, gname, lvl, r1, r2, r3, r4, r5, time, kp, zdata, zdatainfo in reader:
        gid = int(gid)

        if gid not in buildings:
            buildings[gid] = {
                    'gid':      gid,
                    'gname':    gname,
                    'zdatainfo':zdatainfo,
                    'levels':   []
                }

        zdata = zdata.strip().replace(',', '.')
        
        buildings[gid]['levels'].append({
                    'r':  [ int(r1), int(r2), int(r3), int(r4) ], 
                    'r5':   int(r5),
                    'time': int(time),
                    'kp':   int(kp),
                    'zdata':float(zdata if zdata else 0)
                })

    pickle.dump(buildings, open('data/builds.pickle', 'wb'))

#read_csv()
try:
    buildings = pickle.load(open('data/builds.pickle', 'rb'))
except:
    buildings = {}

building_names = {
        'woodcutter':   1,
        'clay_pit':     2,
        'iron_mine':    3,
        'cropland':     4,
        'sawmill':      5,
        'brickyard':    6,
        'iron_foundry': 7,
        'grain_mill':   8,
        'bakery':       9,
        'warehouse':    10,
        'granary':      11,
        'smithy':       13,
        'tournament square': 14,
        'main_building': 15,
        'rally_point':  16,
        'marketplace':  17,
        'embassy':      18,
        'barracks':     19,
        'stable':       20,
        'workshop':     21,
        'academy':      22,
        'cranny':       23,
        'town_hall':    24,
        'residence':    25,
        'palace':       26,
        'treasury':     27,
        'trade_office': 28,
        'great_barracks': 29,
        'great_stable': 30,
        'city_wall':    31,
        'earth_wall':   32,
        'palisade':     33,
        'stonemasons_lodge': 34,
        'brewery':      35,
        'trapper':      36,
        'heros_mansion': 37,
        'great_warehouse': 38,
        'great_granary': 39,
        'wonder_of_the_world': 40,
        'horse_drinking_trough': 41
    }
    
"""change_map = { 1: 18, 2: 35, 3: 39,  4: 38, 5: 28, 6: 15, 7: 11,
               8: 17, 9: 26, 10: 41, 11: 24, 12: 25, 13: 10, 14: 27,
               15: 34, 16: 23, 17: 40, 18: 22, 19: 32, 20: 36, 21: 29, 22: 30,
               23: 37, 24: 19, 25: 33, 26: 13, 27: 32, 28: 20, 29: 14, 30: 16,
               32: 21, 33: 1, 34: 2, 35: 3, 36: 4, 37: 8, 38: 7, 39: 5,
               40: 6, 41: 7 }

new_buildings = {}

for f, t in change_map.items():
    b = buildings[f]
    b['gid'] = t
    new_buildings[t] = b

pickle.dump(new_buildings, open('data/builds.pickle', 'wb'))"""

import pymongo

class DBTable():
    def find(self): pass
    def find_one(self): pass
    def insert(self): pass
    def save(self): pass
    def remove(self): pass

users = DBTable()
jobs = DBTable()
states = DBTable()

try:
    mongo_server = pymongo.MongoClient('localhost', 27017)
except:
    mongo_server = pymongo.MongoClient('ultimus.sytes.net', 27017)
database = mongo_server.eviltravian
users = database.users
jobs = database.jobs
states = database.states

def get_gid_by_name(gname):
    try:
        return next(bld['gid'] for bld in buildings.values() if bld['gname'] == gname)
    except:
        print(gname)
    
