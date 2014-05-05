
import db
import action
from action import Action

from datetime import datetime, timedelta
from calendar import timegm
import travian

import time

import random

job_classes = {}

def job(job_type):
    def _add_class(cls):
        cls.__job_type__ = job_type
        job_classes[job_type] = cls
        return cls

    return _add_class

class Job(dict):
    
    accumulator = 1000

    def __init__(self, job_dict, additional_conditions={}):
        job_dict.setdefault('type', self.__job_type__)
        if '_jid' not in job_dict:
            job_dict['_jid'] = Job.accumulator
            Job.accumulator += 1
        dict.__init__(self, job_dict)
        self.additional_conditions = additional_conditions

    @classmethod
    def create(cls, job_dict):
        return job_classes[job_dict['type']](job_dict)

    def get_conditions(self, village):
        return self.additional_conditions
    
    def execute(self, village): raise NotImplemented()

    def __repr__(self):
        return type(self).__name__ + "(" + str(dict(self)) + ")"

    
def quest(quest_name, after_job = False):
    return Action(None, action.action_quest, ["next", quest_name], after_job = after_job)

def get(url):
    return Action(None, travian.Travian.request_GET, [ url, False ])

def rename_village(new_name):
    return Action(None, action.action_rename_current_village, [ new_name ])

build_roman = ( [
            { "name": "clay_pit", "level": 1, "actions": [ get("/statistiken.php") ] },
            { "name": "clay_pit", "level": 1, "actions": [ rename_village("Bubber Duckery") ] },
            { "name": "woodcutter", "level": 1, "actions": [ quest("World_02") ]},
            { "name": "iron_mine", "level": 1, "actions": [ quest("Economy_01", after_job = True) ] },
            { "name": "cropland", "level": 1 },
            { "name": "iron_mine", "level" : 1 },
            { "name": "cropland", "level": 1, "actions": [ quest("Economy_02") ] },
            { "name": "clay_pit", "level": 1 },
            { "name": "cropland", "level" : 1 },
            { "name": "woodcutter", "level" : 1, "actions": [ quest("World_01") ] },
            { "name": "cropland", "level" : 1 },
            { "name": "woodcutter", "level" : 1, "delay": timedelta(seconds=30) },
            { "name": "cropland", "level" : 1 },
            { "name": "cropland", "level" : 2 },
            { "name": "iron_mine", "level" : 1 },
            { "name": "iron_mine", "level" : 1 },
            { "name": "clay_pit", "level": 2, "actions": [ quest("Economy_04") ] },
            { "name": "woodcutter", "level" : 2 },
            { "name": "cropland", "level" : 2 },
            { "name": "iron_mine", "level" : 2 },
            { "name": "clay_pit", "level": 2, "actions": [ quest("Economy_05") ] },
            { "name": "clay_pit", "level": 2 },
            { "name": "woodcutter", "level" : 2 },
            { "name": "cropland", "level": 2 },
            { "name": "woodcutter", "level" : 2 },
            { "name": "iron_mine", "level" : 2 },
            { "name": "cropland", "level": 2 },
            { "name": "clay_pit", "level": 2 },
            { "name": "iron_mine", "level" : 2 },
            { "name": "cropland", "level" : 2 },
            { "name": "iron_mine", "level" : 2 },
            { "name": "clay_pit", "level": 3, "actions": [ quest("Economy_08") ] }
        ],

        [
            { "name": "main_building", "level": 2 },
            { "name": "cranny", "level": 1 },
            { "name": "main_building", "level": 3, "actions": [ quest("Battle_02") ] },
            { "name": "granary", "level": 1, "actions": [ quest("World_03") ] },
            { "name": "embassy", "level": 1, "actions": [ quest("Economy_03") ] },
            { "name": "warehouse", "level": 1, "actions": [ quest("World_04"), get("/karte.php") ] },
            { "name": "marketplace", "level": 1 }
        ]
    )
##### BUILD JOB #####

@job('build')
class JobBuild(Job):
    
    def get_conditions(self, village):
        build_id = self.get_build_id()
        build_db = db.buildings[build_id]
        resources = build_db['levels'][self['level']-1]
        
        cond = { 'resources': resources,
                 'build_slot_id': self.get_slot_id(village.account) }
        cond.update(super().get_conditions(village))
        return cond
        
    def execute(self, village):
        self.build_building(self.get_build_id(), self['level'])
    
    def build_building(self, village, bld_gid, bld_lvl):
        from_lvl = bld_lvl - 1

        bld_bid = None
        bld_new = None
        for bid, gid, lvl in village.buildings:
            if gid == bld_gid and lvl == from_lvl:
                bld_bid = bid
                bld_new = False
                break

        if bld_bid is None:
            for bid, gid, lvl in village.buildings:
                if gid == 0:
                    bld_bid = bid
                    bld_new = True
                    print("building gid %d lvl %d new on %d" % (bld_gid, bld_lvl, bld_bid))
                    break
                
        if bld_new is None:
            return False

        if bld_new == True:
            action.action_build_new(village.account, bld_bid, bld_gid)
        else:
            action.action_build_up(village.account, bld_bid)
        
    def get_build_id(self):
        return db.building_names[self['name']]
        
    def get_slot_id(self, account):
        if account.nation != 'roman':
            return 0
        
        return 1 if self.get_build_id() <= 4 else 2
        
@job('http')
class JobHttp(Job):
    
    def execute(self, village):
        if self.get('method', None) == 'post':
            self.village.account.request_POST(self['url'], self['params'])
        else:
            self.village.account.request_GET(self['url'], False)
            
@job('rename_village')
class JobRenameVillage(Job):
    
    def execute(self, village):
        action.action_rename_current_village(village.account, self['new_name'])

@job('quest')
class JobQuest(Job):
    
    '''def get_conditions(self, village):
        cond = { 'quest': self['name'] }
        cond.update(super().get_conditions(village))
        return cond'''
    
    def execute(self, village):
        action.action_quest(village.account, "next", self['name'])
        
