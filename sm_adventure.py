'''
Created on 23.05.2014

@author: Tobias Ruck
'''
from state import StateMachine, State

class StateMachine_Adventure(metaclass=StateMachine):
    '''
    classdocs
    '''

    class start(State):
        
        def transition(self):
            self.current_state = self.wait_for_hero
            
    class wait_for_hero(State):
        
        