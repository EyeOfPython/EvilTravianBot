'''
Created on 02.05.2014

@author: Tobias Ruck
'''
from state import State, StateMachine
from event import listen_to, Event
from trigger import trigger, TriggerEnoughResources, TriggerBuildSlotAvailable,\
    TriggerEnoughSpaceForResources
from datetime import datetime
from job import Job, JobBuild
from condition import condition_changes, ConditionEnoughResources,\
    ConditionEnoughSpaceForResources, ConditionBuildSlotAvailable,\
    ConditionQuestFulfilled
import db

build_roman = ( 
               
        # World quests       
        [ 
            { 'type': 'http',  'url': '/statistiken.php' },
            ({ 'type': 'quest', 'name': 'World_01', 'space': (90, 120, 60, 30) },),
            { 'type': 'rename_village', 'new_name': 'Bubber Duckey' },
            ({ 'type': 'quest', 'name': 'World_02' },),
        ],
               
        [
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'build', 'name': 'woodcutter', 'level': 1 }, 
            { 'type': 'build', 'name': 'iron_mine', 'level': 1 }, 
            ({ 'type': 'quest', 'name': 'Economy_01'},),
            { 'type': 'build', 'name': 'cropland', 'level': 1 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 1, 'quest_event': 'Economy_02' },
            { 'type': 'build', 'name': 'cropland', 'level': 1 }, 
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 1 }, 
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 1 },
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 1 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 1, 'quest_event': 'Economy_04' },
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 },
            { 'type': 'build', 'name': 'cropland', 'level' : 2 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level' : 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2, 'quest_event': 'Economy_05' },
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 }, 
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level': 2 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level': 2 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level' : 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2, 'quest_event': 'Economy_08' },
            { 'type': 'build', 'name': 'clay_pit', 'level': 3 },
            { 'type': 'build', 'name': 'cropland', 'level' : 3 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 3 },
            { 'type': 'build', 'name': 'cropland', 'level' : 3 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 3 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 3 }, 
            { 'type': 'build', 'name': 'cropland', 'level' : 2 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 3 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 3 },
            { 'type': 'build', 'name': 'cropland', 'level': 3 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 3 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 3 },
            { 'type': 'build', 'name': 'cropland', 'level': 3 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 3 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 3 },
            { 'type': 'build', 'name': 'cropland', 'level' : 4 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 3 },
            { 'type': 'build', 'name': 'cropland', 'level': 5 },
            { 'type': 'build', 'name': 'grain_mill', 'level': 1, 'quest_event': 'Economy_11' },
            { 'type': 'build', 'name': 'cropland', 'level': 3 },
            ## TODO: build all to 5
        ],

        [
            { 'type': 'build', 'name': 'main_building', 'level': 2 },
            { 'type': 'build', 'name': 'cranny', 'level': 1, 'quest_event': 'Battle_02' },
            { 'type': 'build', 'name': 'main_building', 'level': 3, 'quest_event': 'World_03' },
            { 'type': 'build', 'name': 'granary', 'level': 1, 'quest_event': 'Economy_03' }, 
            { 'type': 'http', 'url': '/karte.php' },
            ({ 'type': 'quest', 'name': 'World_05', 'space': (90, 160, 90, 95) },),
            { 'type': 'read_inbox' },
            ({ 'type': 'quest', 'name': 'World_06', 'space': (280, 315, 200, 145) },),
            { 'type': 'open_gold_menu' },
            { 'type': 'quest', 'name': 'World_07b' },
            { 'type': 'build', 'name': 'embassy', 'level': 1, 'quest_event': 'World_04' },
            { 'type': 'build', 'name': 'warehouse', 'level': 1 },
            { 'type': 'build', 'name': 'marketplace', 'level': 1, 'quest_event': 'Economy_06' },
            { 'type': 'build', 'name': 'warehouse', 'level': 2 },
            { 'type': 'build', 'name': 'barracks', 'level': 1, 'quest_event': 'Battle_03' },
            { 'type': 'build', 'name': 'warehouse', 'level': 3, 'quest_event': 'Economy_09' },
            { 'type': 'build', 'name': 'main_building', 'level': 4 },
            { 'type': 'build', 'name': 'main_building', 'level': 5, 'quest_event': 'World_05' },
            { 'type': 'build', 'name': 'granary', 'level': 2 },
            { 'type': 'build', 'name': 'granary', 'level': 3, 'quest_event': 'Economy_10' },
        ],
        
        [
            { 'type': 'quest', 'name': 'Economy_06', 'space': (600, 0, 0, 0), 'is_event_based': True }, # marketplace 
            { 'type': 'sell_resources', 'sell_res': 1, 'buy_res': 2, 'sell_amount': 100, 'buy_amount': 200 }, # sell 100 wood for 200 clay
            { 'type': 'quest', 'name': 'Economy_07', 'space': (100, 99, 99, 99) }
        ],
        
        { 'type': 'quest', 'name': 'Economy_02', 'space': (160, 190, 150, 70),  'is_event_based': True }, # 4 of each resource at lvl 1
        { 'type': 'quest', 'name': 'Economy_03', 'space': (250, 290, 100, 130), 'is_event_based': True }, # granary
        { 'type': 'quest', 'name': 'Economy_04', 'space': (400, 460, 330, 270), 'is_event_based': True }, # everything at lvl 1
        { 'type': 'quest', 'name': 'Economy_05', 'space': (240, 255, 190, 160), 'is_event_based': True }, # 4 of each resource at lvl 2
        { 'type': 'quest', 'name': 'Economy_08', 'space': (400, 400, 400, 200), 'is_event_based': True }, # everything at lvl 2
        { 'type': 'quest', 'name': 'Economy_09', 'space': (620, 730, 560, 230), 'is_event_based': True }, # warehouse lvl 3
        { 'type': 'quest', 'name': 'Economy_10', 'space': (880, 1020,590, 320), 'is_event_based': True }, # granary lvl 3
        { 'type': 'quest', 'name': 'Economy_11', 'is_event_based': True }, # grain mill
        
        { 'type': 'quest', 'name': 'Battle_02',  'space': (130, 150, 120, 100), 'is_event_based': True }, # cranny
        
        { 'type': 'quest', 'name': 'World_03',   'space': (170, 100, 130, 70),  'is_event_based': True }, # main building lvl 3
        { 'type': 'quest', 'name': 'World_04',   'space': (215, 145, 195, 50),  'is_event_based': True }, # embassy
        
)

class JobManager():
    
    def __init__(self, village, job_definition):
        self.village = village
        self.jobs = []
        self.state_machines = []
        self.root = Job.create({'type':'root'})
        self._recursive_add_jobs(self.root, job_definition)
        
    def _recursive_add_jobs(self, parent, job_def):
        if isinstance(job_def, tuple):
            for jd in job_def:
                self._recursive_add_jobs(parent, jd)
        
        elif isinstance(job_def, list):
            for jd in job_def:
                p = self._recursive_add_jobs(parent, jd)
                if p is not None:
                    parent = p
                    
        elif isinstance(job_def, dict):
            job = Job.create(job_def)
            self.jobs.append(job)
            
            sm = StateMachine_Job(self.village, {'start': { 'job': job } })
            sm.current_state['after_job_id'] = parent['_jid']
            self.state_machines.append(sm)
            return job
        
    def __on_event__(self, event):
        '''
        Dispatches the event to all children state machines
        '''
        for sm in self.state_machines:
            sm.__on_event__(event)

class StateMachine_Job(metaclass = StateMachine):
    
    class start(State):
        
        @listen_to('job_completed')
        def on_job_completed(self, event):
            #if self['job'].get('name', None) == 'main_building':
            #    print('* main build:', self.data, event.job)
            if event.job['_jid'] == self['after_job_id']:
                self.wait_for_conditions['job'] = self['job']
                self.current_state = self.wait_for_conditions
                
                
    class wait_for_conditions(State):
        
        def transition(self):
            '''
            Store the conditions of the job and assign the triggers
            '''
            self['conditions'] = self['job'].get_conditions(self.village)
            self.cond_instances = {}
            self.ready = False
            
            if 'resources' in self['conditions']:
                self.cond_instances['resources'] = self.cond_enough_resources().enqueue(self.village, self['conditions']['resources'])
                
            if 'space' in self['conditions']:
                self.cond_instances['space'] = self.cond_enough_space().enqueue(self.village, self['conditions']['space'])
                
            if 'build_slot_id' in self['conditions']:
                self.cond_instances['build_slot_id'] = self.cond_build_slot_available().enqueue(self.village, self['conditions']['build_slot_id'])
            
            if 'quest_event' in self['conditions']:
                self.cond_instances['quest_event'] = self.cond_quest_fulfilled().enqueue(self.village, self['conditions']['quest_event'])
            
            self.ready = True
            self.check_execution()
            
        @condition_changes(ConditionQuestFulfilled)
        def cond_quest_fulfilled(self):
            self.check_execution()
            
        @condition_changes(ConditionEnoughResources)
        def cond_enough_resources(self):
            self.check_execution()
            
        @condition_changes(ConditionEnoughSpaceForResources)
        def cond_enough_space(self):
            self.check_execution()
            
        @condition_changes(ConditionBuildSlotAvailable)
        def cond_build_slot_available(self):
            self.check_execution()
            
        def check_execution(self):
            if not self.ready:
                return
            self.ready = False
            c = True
            cn = {}
            for k, cond in self.cond_instances.items():
                c = c and cond.is_true()
                cn[k] = cond.is_true()
            print("*** check", self['job'], cn, self['conditions'], self.cond_instances)
            if c:
                print("execute job", self['job'])
                for cond in self.cond_instances.values():
                    cond.terminate()
                self['job'].execute(self.village)
                
                if 'quest_event' in self['job'] and isinstance(self['job'], JobBuild):
                    self.wait_for_build['quest_event'] = self['job']['quest_event']
                    self.wait_for_build['building'] = self['job'].get_build_id()
                    self.wait_for_build['level'] = self['job']['level']
                    self.current_state = self.wait_for_build
                else:
                    self.current_state = self.terminated
                self.village.fire_event( Event(self.village, 'job_completed', datetime.now(), job=self['job']) )
            self.ready = True
                
    class wait_for_build(State):
                
        @listen_to('build')
        def on_build(self, event):
            if event.building == self['building'] and event.level == self['level']:
                self.village.fire_event( Event(self.village, 'quest_fulfilled', datetime.now(), quest_name=self['quest_event']) )
                
                self.current_state = self.terminated
                
    class terminated(State):
        
        pass

class StateMachine_Quests(metaclass = StateMachine):
    
    class start(State):
        
        def init(self):
            if 'build_index' not in self:
                self['build_index'] = 0
        
        @listen_to('idle')
        def on_idle(self, event):
            self.current_state = self.idle
    
    class idle(State):
        
        def transition(self):
            print('start idling')

if __name__ == '__main__':
    import pprint
    from village import Village
    from account import Account
    vill = Village(Account((0,0), None), None, None, None)
    jm = JobManager(vill, build_roman)
    pprint.pprint([ sm.current_state.data for sm in jm.state_machines ])
    print("-"*10)
    #jm.__on_event__(Event(vill, 'job_completed', None, job=jm.root))