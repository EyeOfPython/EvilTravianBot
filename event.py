
class EventSet():
    
    def __init__(self):
        
        self.build  = set()
        self.troops = set()
        self.train  = set()
        self.adventure_return = set()
        
        self.next = None
        
    def __repr__(self):
        return "EventSet(%s)" % self.__dict__
    
    def _sets(self):
        return [ self.build, self.troops, self.train, self.adventure_return ]
    
    def update_next(self):
        self.next = None
        
        for event_set in self._sets():
            for event in event_set:
                if self.next is None or self.next.time > event.time:
                    self.next = event
                    
    def remove(self, event):
        for event_set in self._sets():
            event_set.difference_update({event})
            

class Event():
    
    def __init__(self, village, name, time, **data):
        self.village = village
        self.name = name
        self.time = time
        for k,v in data.items():
            self.__setattr__(k,v)
        self.data = data
        
    def __str__(self):
        return repr(self)

    def __repr__(self):
        return "Event(Village(" + repr(self.village.name) + ", ...), " + repr(self.name) + ", " + repr(self.time) + ", **" + str(self.data) + ")"
    
    def __hash__(self):
        return id(self)

def listen_to(*event_names):
    '''
    Marks a method as a listener to events
    '''
    def inner(fn):
        fn.__listened_events__ = set(event_names)
        return fn
        
    return inner

def handler_class(cls):
    '''
    Marks a class as that is contains event listeners
    '''
    assert isinstance(cls, type), "cls must be a type"
    cls.__event_listeners__ = {}
    
    for v in cls.__dict__.values():
        if hasattr(v, "__listened_events__"):
            for event_name in v.__listened_events__:
                cls.__event_listeners__.setdefault(event_name, []).append(v)
    
    def on_event(self, event):
        if event.name in self.__event_listeners__:
            for listener in self.__event_listeners__[event.name]:
                listener(self, event)
    
    cls.__on_event__ = on_event
    
    return cls
    
if __name__ == "__main__":
    
    @handler_class
    class HandlerTest():
        
        @listen_to("build")
        def listener_test(self, event):
            self.test = "test"
    
    assert HandlerTest.listener_test in HandlerTest.__event_listeners__['build']
    h = HandlerTest()
    h.__on_event__(Event(None, "build", None))
    assert h.test == "test"
    