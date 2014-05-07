'''
Created on 27.04.2014

@author: Tobias Ruck
'''
from datetime import datetime
from event import handler_class, listen_to

class _ConditionFunc():
    
    def __init__(self, cls, callback):
        self.cls = cls
        self.callback = callback
        
    def enqueue(self, village, *params):
        self.cls(village, self.callback, *params)

def condition_changes(cond_cls):
    def inner(fn):
        return lambda self=None: _ConditionFunc(cond_cls, lambda: fn(self))
    return inner
    
@handler_class
class Condition():
    '''
    Determines, whether certain conditions are met, and accepts a handler that gets fired upon change
    '''

    def __init__(self, village, callback=None):
        '''
        Constructor
        '''
        
        self.village = village
        self.callback = callback
        self.state = False
        self.prev_state = False
        
        self.village.conditions.append(self)
        
    def update(self):
        pass
    
    def is_true(self):
        '''
        Returns whether this condition holds/is fulfilled.
        '''
        return self.state
    
    def check_change(self):
        state = self.is_true()
        if state != self.prev_state:
            if self.callback is not None:
                self.callback()
            self.prev_state = state
    
    def terminate(self):
        self.village.conditions.remove(self)

@handler_class    
class ConditionEnoughResources(Condition):
    '''
    Is true when a certain amount of resources are available in a village.
    '''
    
    def __init__(self, village, callback, resources):
        super().__init__(village, callback)
        self.resources = resources
        self.recalc_time()
    
    def recalc_time(self):
        self.time = datetime.now() + self.village.get_production_time(self.resources)
    
    def update(self):
        if self.state == False and self.time <= datetime.now():
            self.state = self.village.has_enough_resources(self.resources)
            self.check_change()
            self.recalc_time()
    
    @listen_to('build', 'quest_reward')
    def on_build(self, event):
        self.recalc_time()
        
    @listen_to('resources_spent')
    def on_resources_spent(self, event):
        self.state = self.village.has_enough_resources(self.resources)
        self.recalc_time()
    
@handler_class
class ConditionEnoughSpaceForResources(Condition):
    '''
    Fires when a village can accept a certain amount of resources without overflow in the storages.
    Only used for accepting quest reward.
    '''
    
    def __init__(self, village, callback, resources):
        super().__init__(village, callback)
        self.resources = resources
        
        self.on_spend_resources(None)
    
    def update(self):
        pass
    
    @listen_to('resources_spent')
    def on_spend_resources(self, event):
        if self.village.has_enough_space(self.resources):
            self.terminate()
            self.callback()
    
@handler_class
class TriggerBuildSlotAvailable(Trigger):
    '''
    Fires when a building has finished building, and the according slot is free
    '''
    
    def __init__(self, village, callback, slot_id):
        super().__init__(village, callback)
        self.slot_id = slot_id
        
        self.on_build(None)
        
    def update(self):
        pass
    
    @listen_to('build')
    def on_build(self, event):
        if len(self.village.get_build_events_for_slot(self.slot_id)) == 0:
            self.terminate()
            self.callback()
        
if __name__ == '__main__':
    from village import Village
    from account import Account
    from resources import Resources
    from event import Event
    
    class K():
        @trigger(TriggerEnoughSpaceForResources)
        def handler_enought_space(self):
            print("enough!")
        
    vill = Village(Account((0,0), None), None, None, None)
    vill.resources = Resources((90,0,0,0))
    vill.storage_capacity = Resources((100,0,0,0))
    vill.next_refresh_time = datetime(2220, 1, 1)
    
    inst = K()
    inst.handler_enought_space().enqueue(vill, Resources((20,0,0,0)))
    print("first check")
    vill.fire_event(Event(vill, 'spend_resources', datetime.now()))
    print("second check")
    vill.resources = Resources((0,0,0,0))
    vill.fire_event(Event(vill, 'spend_resources', datetime.now()))
    print(vill.triggers)
    