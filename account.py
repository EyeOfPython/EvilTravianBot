'''
Created on 21.04.2014

@author: Tobias Ruck
'''
import requests
import db
from htmldom.htmldom import HtmlDom
import action
import quest
import re
import reader
from village import Village

class Account():
    '''
    Manages the requests for a specific account, handles locking etc.
    With this requests are issued.
    '''

    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:22.0) Gecko/20100101 Firefox/5.0",
        "Accept": "text/javascript, text/html,application/xhtml+xml,application/xml, */*;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
        "Connection": "close"
    }

    def __init__(self, server, user_name):
        assert isinstance(server, tuple) and len(server) == 2
        self.server    = server
        self.user_name = user_name
        
        self.url = "http://ts%s.travian.%s" % server
        
        self.session = requests.Session()
        
        self.villages = {}
        
    ### DB-loading ###
    
    def get_db(self):
        return db.users.find_one({'name': self.user_name, 'server':self.server})
    
        
    def init_db(self, email, password, nation, proxies):
        '''
        Sets the basic parameters for this account
        '''
        user = {'name': self.user_name, 'email': email, 'password': password, 'server': self.server, 'nation': nation, 'proxies': proxies, 'activated': False }
        
        db.users.save(user)

        
    def load_db(self):
        user = self.get_db()
        
        if not user:
            return
        
        self.proxies = user['proxies']
        self.email = user['email']
        self.password = user['password']
        self.nation = user['nation']
        self.activated = user['activated']
        
        # TODO: better proxy selection
        self.session.proxies = { "http": self.proxies[0], "https": self.proxies[0] }
        
    ### Request functions ###
    
    def request_GET(self, url, createDom=True):
        
        headers = self.default_headers
        result = self.session.get(self.url + url, headers=headers)
        if not result.text:
            raise ValueError("result.text is empty!")

        if createDom:
            return HtmlDom().createDom(result.text)
        return result
        
        
    def request_POST(self, url, params, add_headers = {}, createDom=True):

        headers = dict(self.default_headers)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        headers.update(add_headers)

        # perform login
        result = self.session.post(self.url + url, data=params, headers=headers)

        try:
            if createDom:
                return HtmlDom().createDom(result.text)
        except:
            print("failed reading page in POST " + url)
            print(result.text[:1000])
        
        return result
    
    
    reg_input_name  = re.compile(r'.*name="([^"]*)".*')
    reg_input_value = re.compile(r'.*value="([^"]*)".*')
    reg_input_type  = re.compile(r'.*type="([^"]*)".*')
    def submit_form(self, doc, form_id, form_values, form_action = None):

        if form_action is None:
            form_action = "/" + doc.find(form_id).attr("action")

        inputs = doc.find("%s input" % form_id)
        params = {}
        
        class _Dummy():
            __slots__ = ()
            def group(self, n): return ""

        for inpt in inputs:
            name = (self.reg_input_name.match(inpt.html()) or _Dummy()).group(1)
            value = (self.reg_input_value.match(inpt.html()) or _Dummy()).group(1)
            type1 = (self.reg_input_type.match(inpt.html()) or _Dummy()).group(1)

            params[name] = value

        params.update(form_values)

        return self.request_POST(form_action, params)
    
    
    def ajax_cmd(self, cmd, params):
        params["cmd"] = cmd
        params["ajaxToken"] = self.ajax_token

        headers = dict(self.default_headers)
        headers.update({"Content-Type":    "application/x-www-form-urlencoded;"})

        response = self.session.post(self.url + "/ajax.php?cmd=quest", data=params, headers=headers)
        return response
    
    
    ### Cookies ###
    
    def save_cookie(self):
        user_db = self.get_db()
        if user_db is None: raise ValueError(self.user_name)
        user_db['cookies'] = { k: self.session.cookies._find(k) for k, v in self.session.cookies.items() }
        db.users.save(user_db)
    
    def load_cookie(self):
        user_db = self.get_db()
        if 'cookies' in user_db:
            self.session.cookies.update(user_db['cookies'])
            return True
        else:
            return False
    
    def clear_cookie(self):
        self.session.cookies.clear()
    
    ### Basic actions (activation, login, ..)
        
    def perform_activation(self, sector):
        self.load_cookie()
        user_db = self.get_db()
        action.action_activate(self, self.server[0], user_db['activation_code'])

        self.login()
        self.save_cookie()

        action.action_select_spawn(self, self.nation, sector)
        
        self.loadup() # requests 1 village
        quest.skip_tutorial(self)
        action.action_tutorial(self, "next", "Tutorial_15a")
        
        user_db['activated'] = True
        db.users.save(user_db)
        
    def login(self, doc_login = None):
        print("logging in...")
        
        doc = doc_login or self.request_GET("/dorf1.php")

        # retrieve current login POST data
        params = {}
        for inpt in doc.find("form[name=login] input"):
            name = inpt.attr('name')
            value = None
            if inpt._is("[value]"):
                value = inpt.attr('value')
            params[name] = value

        # alter it
        params['name'] = self.user_name
        params['password'] = self.password
        params['lowRes'] = '1'
        params['s1'] = 'Einloggen'
        params['w'] = '1920:1080'
        
        print("POST", params)

        # perform login and return village overview        
        return self.request_POST("/dorf1.php", params)
    
    def loadup(self):
        """
        Loads cookies, Logins, 
        Loads all villages, events and the hero.
        """
        self.load_db()
        #self.load_cookie()
        
        doc_resources = self.request_GET("/dorf1.php")
        if not len(reader.read_resource_fields(doc_resources)):
            self.clear_cookie()
            doc_resources = self.login(doc_login = doc_resources)
            self.save_cookie()
            
            if not len(reader.read_resource_fields(doc_resources)):
                print("login failed!")
        
        village = self.request_village(None, doc_resources)
        
        other_villages = self.villages.keys() ^ { village.village_id } # all villages except the active
        
        self.request_villages(other_villages)
        
    def request_village(self, village_id, doc_login = None):
        '''
        If village_id is None, doc_login will be used and a list of villages will be stored.
        '''
        
        doc_resources = doc_login or self.request_GET("/dorf1.php?newdid=%d" % village_id)
            
        pages = { 'resources': doc_resources,
                  'village': self.request_GET("/dorf2.php") }
        
        active_village = reader.read_villages(doc_resources, True)[0]
        if village_id is None:
            all_villages = reader.read_villages(doc_resources)
            
            self.villages.clear()
            self.villages.update( { vill['village_id']: Village(self, **vill) for vill in all_villages } )
        
        if active_village['village_id'] not in self.villages:
            self.villages[active_village['village_id']] = Village(self, **active_village)
        
        village = self.villages[active_village['village_id']]
        if active_village['name'] != village.name:
            print("Village %s renamed to %s" % (village.name, active_village['name']))
        village.name = active_village['name']
        
        village.read_content(pages)
        village.read_events(pages)
        
        village.new_refresh_time()
        
        return village
        
    def request_villages(self, village_keys=None):
        """
        Requests all villages, or only those with the given keys.
        Writes the village data into existing village instances or creates new ones.
        """
        village_keys = village_keys if village_keys is not None else self.villages.keys()
        for village_id in village_keys:
            self.request_village(village_id)
            
    def update(self):
        for vill in self.villages.values():
            vill.update()
            
            
            