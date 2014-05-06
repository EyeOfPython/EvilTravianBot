'''
Created on 02.05.2014

@author: Tobias Ruck
'''
from state import State, StateMachine
from event import listen_to, Event
from trigger import trigger, TriggerEnoughResources, TriggerBuildSlotAvailable,\
    TriggerEnoughSpaceForResources
from datetime import datetime
from job import Job

build_roman = ( 
               
        # World quests       
        [ 
            { 'type': 'http',  'url': '/statistiken.php' },
            ({ 'type': 'quest', 'name': 'World_01', 'space': (90, 120, 60, 30) },),
            { 'type': 'rename_village', 'new_name': 'Bubber Duckery' },
            ({ 'type': 'quest', 'name': 'World_02' },),
        ],
               
        [
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'build', 'name': 'woodcutter', 'level': 1 }, 
            { 'type': 'build', 'name': 'iron_mine', 'level': 1 }, 
            ({ 'type': 'quest', 'name': 'Economy_01'},),
            { 'type': 'build', 'name': 'cropland', 'level': 1 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 1 },
            { 'type': 'build', 'name': 'cropland', 'level': 1 }, 
            ({ 'type': 'quest', 'name': 'Economy_02', 'space': (160, 190, 150, 70) },),
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 1 }, 
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 1 },
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'type': 'build', 'name': 'cropland', 'level' : 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 1 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 1 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 },
            ({ 'type': 'quest', 'name': 'Economy_04', 'space': (400, 460, 330, 270) },),
            { 'type': 'build', 'name': 'woodcutter', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level' : 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 }, 
            ({ 'type': 'quest', 'name': 'Economy_05', 'space': (240, 255, 190, 160) },),
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level': 2 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level': 2 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2 },
            { 'type': 'build', 'name': 'cropland', 'level' : 2 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 2 },
            { 'type': 'build', 'name': 'clay_pit', 'level': 3 },
            ({ 'type': 'quest', 'name': 'Economy_08'},)  
        ],

        [
            { 'type': 'build', 'name': 'main_building', 'level': 2 },
            { 'type': 'build', 'name': 'cranny', 'level': 1 },
            { 'type': 'build', 'name': 'main_building', 'level': 3 },
            ({ 'type': 'quest', 'name': 'Battle_02'},) ,
            { 'type': 'build', 'name': 'granary', 'level': 1 }, 
            ({ 'type': 'quest', 'name': 'World_03'},),
            { 'type': 'build', 'name': 'embassy', 'level': 1 },
            ({ 'type': 'quest', 'name': 'Economy_03'},),
            { 'type': 'build', 'name': 'warehouse', 'level': 1 },
            ({ 'type': 'quest', 'name': 'World_04'},),
            { 'type': 'http', 'url': '/karte.php' },
            { 'type': 'build', 'name': 'marketplace', 'level': 1 }
        ],
        
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
            if event.job['_jid'] == self['after_job_id']:
                self.wait_for_conditions['job'] = self['job']
                self.current_state = self.wait_for_conditions
                
    class wait_for_conditions(State):
        
        def transition(self):
            '''
            Store the conditions of the job and assign the triggers
            '''
            self['conditions'] = self['job'].get_conditions(self.village)
            self.check_execution()
            
            if 'resources' in self['conditions']:
                self.handle_enough_resources().enqueue(self.village, self['conditions']['resources'])
                
            if 'space' in self['conditions']:
                self.handle_enough_space().enqueue(self.village, self['conditions']['space'])
                
            if 'build_slot_id' in self['conditions']:
                self.handle_build_slot_available().enqueue(self.village, self['conditions']['build_slot_id'])
                
        @trigger(TriggerEnoughResources)
        def handle_enough_resources(self):
            self['conditions'].pop('resources')
            self.check_execution()
            
        @trigger(TriggerEnoughSpaceForResources)
        def handle_enough_space(self):
            self['conditions'].pop('space')
            self.check_execution()
            
        @trigger(TriggerBuildSlotAvailable)
        def handle_build_slot_available(self):
            self['conditions'].pop('build_slot_id')
            self.check_execution()
            
        def check_execution(self):
            if len(self['conditions']):
                print('conditions left', self['conditions'])
            if len(self['conditions']) == 0:
                print("execute job", self['job'])
                self['job'].execute(self.village)
                self.village.fire_event( Event(self.village, 'job_completed', datetime.now(), job=self['job']) )
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
    jm = JobManager(None, build_roman)
    jm.__on_event__(Event(None, 'job_completed', None, job=jm.root))