'''
Created on 27.04.2014

@author: Tobias Ruck
'''
from datetime import datetime
from event import handler_class, listen_to

@handler_class
class Trigger():
    '''
    Fires upon certain conditions, e.g. enough resources or grain production
    '''

    def __init__(self, village, callback):
        '''
        Constructor
        '''
        
        self.time = datetime(1900, 1, 1)
        self.village = village
        self.callback = callback
        
        self.village.triggers.append(self)
        
    def update(self):
        now = datetime.now()
        if self.time <= now:
            self.terminate()
            self.callback()
            
    def terminate(self):
        self.village.triggers.remove(self)

@handler_class    
class TriggerEnoughResources(Trigger):
    '''
    Fires when a certain amount of resources are available in a village.
    '''
    
    def __init__(self, village, callback, resources):
        super().__init__(village, callback)
        self.resources = resources
        self.recalc_time()
    
    def recalc_time(self):
        self.time = datetime.now() + self.village.get_production_time(self.resources)
    
    @listen_to('build')
    def on_build(self, event):
        self.recalc_time()
    
@handler_class
class TriggerBuildSlotAvailable(Trigger):
    '''
    Fires when a building has finished building, and the according slot is free
    '''
    
    def __init__(self, village, callback, slot_id):
        super().__init__(village, callback)
        self.slot_id = slot_id
        
    def update(self):
        pass
    
    @listen_to('build')
    def on_build(self, event):
        if len(self.village.get_build_events_for_slot(self.slot_id)) == 0:
            self.terminate()
            self.callback()
        
        