'''
Created on 02.05.2014

@author: Tobias Ruck
'''
from state import State, StateMachine
from event import listen_to, Event
from trigger import trigger, TriggerEnoughResources

build_roman = ( [
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'http',  'url': '/statistiken.php' },
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'rename_village', 'new_name': 'Bubber Duckery' },
            { 'type': 'quest', 'name': 'World_02' },
            { 'type': 'build', 'name': 'woodcutter', 'level': 1 }, 
            { 'type': 'build', 'name': 'iron_mine', 'level': 1 }, 
            { 'type': 'quest', 'name': 'Economy_01' },
            { 'type': 'build', 'name': 'cropland', 'level': 1 },
            { 'type': 'build', 'name': 'iron_mine', 'level' : 1 },
            { 'type': 'build', 'name': 'cropland', 'level': 1 }, 
            { 'type': 'quest', 'name': 'Economy_02' },
            { 'type': 'build', 'name': 'clay_pit', 'level': 1 },
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'type': 'build', 'name': 'woodcutter', 'level' : 1 }, 
            { 'type': 'build', 'name': 'cropland', 'level' : 1 },
            { 'name': 'woodcutter', 'level' : 1 },
            { 'name': 'cropland', 'level' : 1 },
            { 'name': 'cropland', 'level' : 2 },
            { 'name': 'iron_mine', 'level' : 1 },
            { 'name': 'iron_mine', 'level' : 1 },
            { 'name': 'clay_pit', 'level': 2, 'actions': [ quest('Economy_04') ] },
            { 'name': 'woodcutter', 'level' : 2 },
            { 'name': 'cropland', 'level' : 2 },
            { 'name': 'iron_mine', 'level' : 2 },
            { 'name': 'clay_pit', 'level': 2, 'actions': [ quest('Economy_05') ] },
            { 'name': 'clay_pit', 'level': 2 },
            { 'name': 'woodcutter', 'level' : 2 },
            { 'name': 'cropland', 'level': 2 },
            { 'name': 'woodcutter', 'level' : 2 },
            { 'name': 'iron_mine', 'level' : 2 },
            { 'name': 'cropland', 'level': 2 },
            { 'name': 'clay_pit', 'level': 2 },
            { 'name': 'iron_mine', 'level' : 2 },
            { 'name': 'cropland', 'level' : 2 },
            { 'name': 'iron_mine', 'level' : 2 },
            { 'name': 'clay_pit', 'level': 3, 'actions': [ quest('Economy_08') ] }
        ],

        [
            
            { 'name': 'main_building', 'level': 2 },
            { 'name': 'cranny', 'level': 1 },
            { 'name': 'main_building', 'level': 3, 'actions': [ quest('Battle_02') ] },
            { 'name': 'granary', 'level': 1, 'actions': [ quest('World_03') ] },
            { 'name': 'embassy', 'level': 1, 'actions': [ quest('Economy_03') ] },
            { 'name': 'warehouse', 'level': 1, 'actions': [ quest('World_04'), get('/karte.php') ] },
            { 'name': 'marketplace', 'level': 1 }
        ]
)

class StateMachine_Job(metaclass = StateMachine):
    
    class start(State):
        
        @listen_to('job_completed')
        def on_job_completed(self, event):
            if event.job['_id'] == self['after_job_id']:
                self.current_state = self.wait_for_conditions
                self.wait_for_conditions['job'] = self['job']
                
    class wait_for_conditions(State):
        
        def transition(self):
            'store the conditions of the job'
            self['conditions'] = self['job'].get_conditions(self.village)
            self.check_completion()
            
            if 'resources' in self['conditions']:
                self.handle_en
                
        @trigger(TriggerEnoughResources)
        def handle_enough_resources(self):
            pass
            
        def check_completion(self):
            if len(self['conditions']) == 0:
                self['job'].execute()
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
    sm = StateMachine_RomanBuild({})
    sm.__on_event__(Event(None, 'idle', None))