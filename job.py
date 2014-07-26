
import db
import action
from action import Action

from datetime import datetime, timedelta
from calendar import timegm
import travian

import time

import random
from event import Event
import reader
from log import logger

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
        pages = village.refresh('resources')
        if not any( event.building == self.get_build_id() and event.level == self['level'] for event in village.events.build ):
            logger.log_error('build failed', pages['resources'], title='Could not build %s level %s.' % (self['name'], self['level']))
        
    def get_build_id(self):
        return db.building_names[self['name']]
        
    def get_slot_id(self, account):
        if account.nation != 'roman':
            return 0
        
        return 1 if self.get_build_id() <= 4 else 2
        
@job('build_fields')
class JobBuildFields(Job):
    
    def __init__(self, job_dict, additional_conditions={}):
        job_dict['repeat'] = True
        super().__init__(job_dict, additional_conditions)
        
    @classmethod
    def get_next_field(cls, village):
        '''
        Calculates, which field to build next.
        '''
        resr_index = village.resources * village.production
        
        fewest_resource = min(range(4), key = lambda k: resr_index[k]) + 1

        return min((bld for bld in village.resource_fields if bld[1] == fewest_resource),
                   key = lambda bld: bld[2])
        
    def next_field(self, village):
        self['next_field'] = self.get_next_field(village)
        
    def get_conditions(self, village):
        if 'next_field' not in self:
            self.next_field(village)
            
        build_db = db.buildings[self['next_field'][1]]
            
        cond = { 'resources': build_db['levels'][self['next_field'][2]-1]['r'],
                 'build_slot_id': self.get_slot_id(village.account) }
        cond.update(super().get_conditions(village))
        return cond
        
    def get_slot_id(self, account):
        if account.nation != 'roman':
            return 0
        
        return 1
        
    def execute(self, village):
        village.build_building(self['next_field'][1], self['next_field'][2]+1)
        self.next_field(village)
        pages = village.refresh('resources')
        if not any( event.building == self['next_field'][1] and event.level == self['next_field'][2]+1 for event in village.events.build ):
            logger.log_error('build failed', pages['resources'], title='Could not build %s level %s.' % (db.buildings[self['next_field']]['gname'], self['level']))
        
        
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
        if self.get('is_event_based', False):
            cond['quest_event'] = self['name']
        cond.update(super().get_conditions(village))
        return cond
    
    def execute(self, village):
        action.action_quest(village.account, "next", self['name'])
        village.fire_event(Event(village, 'quest_reward', datetime.now()))
        
@job('read_inbox')
class JobReadInbox(Job):
    # Reads the most recent message
    def execute(self, village):
        doc = village.account.request_GET('/nachrichten.php')
        inbox = reader.read_inbox(doc)
        if len(inbox) == 0:
            raise ValueError("No message in inbox found!")
        for mail in inbox:
            village.account.request_GET(mail['href'])
        
@job('open_gold_menu')
class JobOpenGoldMenu(Job):
    
    def execute(self, village):
        
        response = village.account.ajax_cmd('paymentWizard', 
                                                  { 'goldProductId': '',
                                                    'goldProductLocation': '',
                                                    'location': '',
                                                    'activeTab': 'pros' }, get_cmd = 'paymentWizard' )

@job('sell_resources')
class JobSellResources(Job):
    
    def execute(self, village):
        
        action.action_sell_resources(village, self['sell_res'], self['sell_amount'], self['buy_res'], self['buy_amount'])
        
        