from event import handler_class, listen_to, Event
import db

class State():
    def __init__(self, state_machine, data):
        assert isinstance(state_machine, _StateMachineBase)
        self.state_machine = state_machine
        self.data = data
        self.init()
        
    def __getattr__(self, name):
        return self.state_machine.states[name]
    
    def __getitem__(self, name):
        return self.data[name]
    
    def __setitem__(self, name, value):
        self.data[name] = value
        
    def __contains__(self, name):
        return name in self.data
        
    @property
    def current_state(self):
        return self.state_machine.current_state
    
    @current_state.setter
    def current_state(self, new_state):
        self.state_machine.transition_into(new_state)
        
    @property
    def village(self):
        return self.state_machine.village
        
    def init(self):
        pass
    
    def transition(self):
        'Override this to execute code when the current state is changed to this state.'
    
    def data_updated(self):
        'Override this to execute code when the data for this state has been updated (e.g. through the database)'
    
    def save_data(self):
        'Save the data of this state to the database.'
        dbdict = self.data.copy()
        dbdict['_village'] = self.village.village_id
        dbdict['_state_machine'] = self.__state_machine_name__
        dbdict['_state'] = type(self).__name__
        db.states.save(self.data)
        
    '''def load_data(self, data):
        data.pop('_state_machine', None)
        data.pop('_state', None)
        self.data = data
        self.data_updated()'''

class _StateMachineBase():
    
    def __init__(self, village, data, start_state_name=None):
        self.village = village
        self.current_state = None
        self.states = {}
        
        for state_name, state_class in self.__state_classes__.items():
            self.states[state_name] = state_class(self, data.get(state_name, {}))
            
            if (start_state_name is not None and state_name == start_state_name) or state_class == self.__start_state__:
                self.current_state = self.states[state_name]
                
        
    def transition_into(self, new_state):
        assert isinstance(new_state, State)
        if '_id' in self.current_state:
            db.states.remove({'_id': self.current_state['_id']})
        self.current_state = new_state
        self.current_state.transition()
        
    def __on_event__(self, event):
        self.current_state.__on_event__(event)

class StateMachine(type):
    '''
    A metaclass for creating a connected system of states
    '''
    
    state_machines = {}
    
    def __new__(cls, name, bases, attrs):
        if not name.startswith("StateMachine_"):
            raise ValueError("State machine classes must have the prefix 'StateMachine_'")
        bases += (_StateMachineBase,)
        new_cls = super().__new__(cls, name, bases, attrs)
        new_cls.__state_classes__ = {}
        new_cls.__start_state__ = None
        
        for k, v in attrs.items():
            if isinstance(v, type) and issubclass(v, State):
                handler_class(v)
                v.__state_machine_name__ = name
                new_cls.__state_classes__[k] = v
                if k == 'start':
                    new_cls.__start_state__ = v
        
        cls.state_machines[name] = new_cls
        if new_cls.__start_state__ is None:
            raise ValueError("A state machine needs a start state called start")
        
        return new_cls
    
    @classmethod
    def create_from_db(cls, village, data):
        d = data.copy()
        d.pop('_state_machine')
        d.pop('_state')
        sm = cls.state_machines[data['_state_machine']](village, { data['_state']: d }, data['_state'])
        sm.current_state.data_updated()
        return sm
    