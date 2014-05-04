from datetime import timedelta, datetime
import reader
from resources import Resources
from event import EventSet, Event
import random

class Village():

    '''
    Stores the state of a village. Collects events for the village and
    fires them on listeners.
    '''
    
    # maps important urls to more friendly names
    url_mapping = {
            'resources': '/dorf1.php',
            'buildings': '/dorf2.php'
        }
    
    def __init__(self, account, name, village_id, coord):
        from account import Account
        
        assert isinstance(account, Account)
        self.account = account
        self.name = name
        self.village_id = village_id
        self.coord = coord
        
        self.resources = None
        self.production = None
        self.resource_fields = None
        self.buildings = None
        self.resource_fields = None
        
        self.events = EventSet()
        self.next_refresh_time = datetime(1900,1,1)
        
        self.event_handlers = []
        self.triggers = []

    def get_next_field(self):
        '''
        @deprecated: move this to AI
        '''
        resr_index = self.resources * self.production
        
        fewest_resource = min(range(4), key = lambda k: resr_index[k]) + 1

        return min((bld for bld in self.resource_fields if bld[1] == fewest_resource),
                   key = lambda bld: bld[2])

    def has_enough_resources(self, resr):
        return +(self.resources - resr) == (self.resources - resr)

    def get_production_time(self, resr):
        needed = +(self.resources - resr) - (self.resources - resr)
        return timedelta(hours=max(needed / self.production))
    
    def get_build_events_for_slot(self, slot_id):
        if slot_id == 0:
            return self.events.build
        
        if slot_id == 1:
            predicate = lambda event: event.building <= 4
        else:
            predicate = lambda event: event.building > 4
            
        return { event for event in self.events.build if predicate(event) }
    
    def read_events(self, pages:dict):
        '''
        Reads all available events from the given pages
        possible keys:
        - trader_movement (marketplace)
        - troop_movement (rally_place)
        - infantry (barracks)
        - cavalry (stable)
        - siege (workshop)
        - traps (trapper)
        - akademy_research (academy)
        - upgrade_research (smithy)
        '''
        if 'resources' in pages:
            doc = pages['resources']
            server_time = reader.read_server_time(doc)
            build_queue = reader.read_build_queue(doc)
            self.events.build = { Event(village = self, 
                                        name    = 'build', 
                                        time    = build_item['timer'] + server_time, 
                                        building= build_item['building'],
                                        level   = build_item['level']) for build_item in build_queue }
        self.events.update_next()
        
    def read_content(self, pages:dict):
        '''
        Reads the content of the given pages and writes them into the village.
        possible keys:
        - resources   (dorf1.php)
            resource_fields
            resources
            production
        - village (dorf2.php)
        - troops (rally_place)
        '''
        
        # dorf1.php:
        if 'resources' in pages: 
            doc = pages['resources']
            self.resource_fields = reader.read_resource_fields(doc)
            self.resources = Resources(reader.read_resources(doc))
            self.production = Resources(reader.read_production(doc))
        
        # dorf2.php
        if 'village' in pages:
            doc = pages['village']
            self.buildings = reader.read_buildings(doc)
            
    def refresh(self, *page_names):
        '''
        Refreshes all pages related with this village, or only 
        with the given pages.
        '''
        print('refreshing at', datetime.now())
        pages = {}
        page_names = page_names or self.url_mapping.keys()
        for page_name in page_names:
            doc = self.account.request_GET(self.url_mapping[page_name])
            pages[page_name] = doc
            
        self.read_content(pages)
        self.read_events(pages)
        
        print(self)
        
        self.new_refresh_time()
        
    def new_refresh_time(self):
        self.next_refresh_time = datetime.now() + timedelta(minutes=random.random()*3)
            
    def update(self):
        '''
        Updates the village by one "tick"
        Fires events and eventually refreshes the events/content
        '''
        
        now = datetime.now()
        if self.events.next and self.events.next.time <= now:
            next_event = self.events.next
            self.events.remove(next_event)
            self.events.update_next()
            self.fire_event(next) # asynchronously 
            
        for trigger in self.triggers:
            trigger.update()
            
        if self.next_refresh_time <= now:
            self.refresh()
            
    def fire_event(self, event):
        print("event %s got fired!" % event)
        
        if event.name == 'build':
            self.refresh('resources', 'village')
        
        for event_handler in self.event_handlers:
            event_handler.__on_event__(event)
            
        for trigger in self.triggers:
            trigger.__on_event__(event)
            
    def __repr__(self):
        return str(self)
            
    def __str__(self):
        return ("Village: \n" +
                "  Resources:  " + str(self.resources) + "\n" +
                "  Production: " + str(self.production) + "\n" +
                "  Buildings:  " + str(self.buildings) + "\n" +
                "  ResourceFields: " + str(self.resource_fields) + "\n" +
                "  Events:     " + str(self.events) + "\n")

