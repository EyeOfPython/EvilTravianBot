from datetime import timedelta, datetime
import reader
from resources import Resources
from event import EventSet, Event
import random
import action
import db
import traceback
from log import logger

class Village():

    '''
    Stores the state of a village. Collects events for the village and
    fires them on listeners.
    '''
    
    # maps important urls to more friendly names
    url_mapping = {
            'resources': '/dorf1.php',
            'village': '/dorf2.php'
        }
    
    event_refresh_pages = {
        'build': ('resources', 'village'),
        'quest_reward': ('resources',),
        'resources_spent': ('resources',),
    }
    
    def __init__(self, account, name, village_id, coord):
        from account import Account
        
        assert isinstance(account, Account)
        self.account = account
        self.name = name
        self.village_id = village_id
        self.coord = coord
        
        self.resources = None
        self.storage_capacity = None
        self.production = None
        self.resource_fields = None
        self.buildings = None
        self.resource_fields = None
        
        self.events = EventSet()
        self.next_refresh_time = datetime(1900,1,1)
        
        self.event_handlers = []
        self.triggers = []
        self.conditions = []
        
        self.suppress_refresh = False

    def has_enough_resources(self, resr):
        return +(self.resources - resr) == (self.resources - resr)

    def has_enough_space(self, resr):
        return +(self.resources + resr - self.storage_capacity) == Resources((0,0,0,0))

    def get_production_time(self, resr):
        needed = +(self.resources - resr) - (self.resources - resr)
        try:
            return timedelta(hours=max(needed / (self.production + Resources((0.00001,)*4))))
        except:
            logger.log_error("production calculation failed", "resr: %s \n self.resources: %s \n self.production: %s" % (resr, self.resources, self.production))
            raise
            return timedelta(minutes=1)
        
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
            if not self.resources or not self.production:
                logger.log_error("page error", [ "%s: %s" % (t, p.find("html").html().strip()) for t,p in pages.items() ], 'Could not fetch village data')
                
            try:
                self.storage_capacity = Resources(reader.read_storage_capacity(doc))
                self.name = reader.read_villages(doc, True)[0]['name']
            except Exception as e:
                traceback.print_exc()
                self.storage_capacity = []
                self.name = ""
        
        # dorf2.php
        if 'village' in pages:
            doc = pages['village']
            self.buildings = reader.read_buildings(doc)
    
    def save_status(self):
        status = db.status.find_one({'village': self.village_id}) or {}
        status['village'] = self.village_id
        status['resource_fields'] = self.resource_fields
        status['buildings'] = self.buildings
        status['resources'] = self.resources
        status['production'] = self.production
        status['storage_capacity'] = self.storage_capacity
        status['name'] = self.name
        status['build_events'] = [ dict(village=event.village.name, name=event.name, time=event.time, **event.data) for event in self.events.build ]
        db.status.save(status)
    
    def refresh(self, *page_names):
        '''
        Refreshes all pages related with this village, or only 
        with the given pages.
        '''
        if self.suppress_refresh:
            return
        logger.log_note('refresh', 'refreshing %s' % str(page_names))
        pages = {}
        page_names = page_names or self.url_mapping.keys()
        for page_name in page_names:
            doc = self.account.request_GET(self.url_mapping[page_name])
            if 'type="password"' in doc.find("html").html():
                logger.log_info("logout", "Logout detected")
                self.account.clear_cookie()
                self.account.login()
                self.account.save_cookie()
                self.next_refresh_time = datetime.now() + timedelta(seconds=30)
                
                return
                
            pages[page_name] = doc
            
        self.read_content(pages)
        self.read_events(pages)
        
        print(self.events.build)
        
        if not self.resources or not self.production or not self.storage_capacity:
            logger.log_error("page error", [ "%s: %s" % (t, p.find("html").html().strip()) for t,p in pages.items() ], 'Could not fetch village data')
            
        self.save_status()
        
        self.new_refresh_time()
        
    def new_refresh_time(self):
        self.next_refresh_time = datetime.now() + timedelta(minutes=random.random()*3+2)
            
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
            self.fire_event(next_event) # asynchronously 
            
        for trigger in self.triggers:
            trigger.update()
            
        for cond in self.conditions:
            cond.update()
            
        if self.next_refresh_time <= now:
            self.refresh()
            
    def fire_event(self, event):
        logger.log_note("event fired", "event %s got fired! %s" % (event.name, event))
        
        pages = self.event_refresh_pages.get(event.name, None)
        if pages is not None:
            try:
                self.refresh(*pages)
            except Exception as e:
                print("could not refresh due to connection issues.")
                print(traceback.format_exc())
        for event_handler in self.event_handlers:
            event_handler.__on_event__(event)
            
        for trigger in self.triggers:
            trigger.__on_event__(event)
        
        for condition in self.conditions:
            condition.__on_event__(event)
            
    def build_building(self, bld_gid, bld_lvl):
        from_lvl = bld_lvl - 1

        bld_bid = None
        bld_new = None
        for bid, gid, lvl in self.buildings + self.resource_fields:
            if gid == bld_gid and lvl == from_lvl:
                bld_bid = bid
                bld_new = False
                break

        if bld_bid is None:
            for bid, gid, lvl in self.buildings + self.resource_fields:
                if gid == 0:
                    bld_bid = bid
                    bld_new = True
                    break
                
        if bld_new is None:
            logger.log_error("build not found", "Nothing to build found! ")
            return False

        if bld_new == True:
            logger.log_info("build", "Building %s new lvl %s at %s" % (db.buildings[bld_gid]['gname'], bld_lvl, bld_bid) )
            action.action_build_new(self.account, bld_bid, bld_gid)
        else:
            logger.log_info("build", "Building %s up from lvl %s to %s at %s" % (db.buildings[bld_gid]['gname'], from_lvl, bld_lvl, bld_bid) )
            action.action_build_up(self.account, bld_bid)
            
        self.fire_event(Event(self, 'resources_spent', datetime.now()))
        
    def get_bid_by_gid(self, search_gid):
        for bid, gid, lvl in self.buildings:
            if search_gid == gid:
                return bid
        return None
        
    def get_bid_by_name(self, name):
        return self.get_bid_by_gid(db.building_names[name])
        
    def __repr__(self):
        return str(self)
            
    def __str__(self):
        return ("Village: \n" +
                "  Resources:  " + str(self.resources) + "\n" +
                "  Production: " + str(self.production) + "\n" +
                "  Buildings:  " + str(self.buildings) + "\n" +
                "  ResourceFields: " + str(self.resource_fields) + "\n" +
                "  Events:     " + str(self.events) + "\n")

