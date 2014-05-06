
import db
import action
from action import Action

from datetime import datetime, timedelta
from calendar import timegm
import travian

import time

import random
from event import Event

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
    def create(cls, job_dict, additional_conditions={}):
        return job_classes[job_dict['type']](job_dict, additional_conditions)

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

"""build_roman = ( [
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
    )"""

##### ROOT JOB #####

@job('root')
class JobRoot(Job):
    def execute(self, village):
        pass

##### BUILD JOB #####

@job('build')
class JobBuild(Job):
    
    def get_conditions(self, village):
        build_id = self.get_build_id()
        build_db = db.buildings[build_id]
        resources = build_db['levels'][self['level']-1]['r']
        
        cond = { 'resources': resources,
                 'build_slot_id': self.get_slot_id(village.account) }
        cond.update(super().get_conditions(village))
        return cond
        
    def execute(self, village):
        village.build_building(self.get_build_id(), self['level'])
        
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
            village.account.request_POST(self['url'], self['params'])
        else:
            village.account.request_GET(self['url'], False)
            
@job('rename_village')
class JobRenameVillage(Job):
    
    def execute(self, village):
        action.action_rename_village(village.account, village.village_id, self['new_name'])

@job('quest')
class JobQuest(Job):
    
    def get_conditions(self, village):
        cond = {}
        if 'space' in self:
            cond['space'] = self['space']
        cond.update(super().get_conditions(village))
        return cond
    
    def execute(self, village):
        action.action_quest(village.account, "next", self['name'])
        village.fire_event(Event(village, 'quest_reward', datetime.now()))
        
