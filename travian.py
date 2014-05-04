#from http.client import HTTPConnection

import requests
from htmldom.htmldom import HtmlDom

import re
import reader
import db

from village import Village
from resources import Resources

import time

import pickle

reg_input_name  = re.compile(r'.*name="([^"]*)".*')
reg_input_value = re.compile(r'.*value="([^"]*)".*')
reg_input_type  = re.compile(r'.*type="([^"]*)".*')

class Travian:
    
    """Unused"""

    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:22.0) Gecko/20100101 Firefox/5.0",
        "Accept": "text/javascript, text/html,application/xhtml+xml,application/xml, */*;q=0.9,*/*;q=0.8",
        "Accept-Language": "de-de,de;q=0.8,en-us;q=0.5,en;q=0.3",
        "Connection": "close"
    }

    def __init__(self, server, user_name, password, nation, proxy_url):
        self.server = server
        self.user_name = user_name
        self.password = password
        self.nation = nation

        self.url = "http://%s.travian.%s" % server

        self.session = requests.Session()

        self.session.headers.update(self.default_headers)
        self.session.proxies = { "http": proxy_url, "https": proxy_url }

        user_db = db.users.find_one({'name':user_name})
        if user_db is None:
            db.users.save({'name':user_name, 'password':password})
            user_db = db.users.find_one({'name':user_name})
            print("created user:", user_db)

        self._id = user_db['_id']

        self.villages = []
        self.village = None

    def request_GET(self, url, createDom=True):
        headers = self.default_headers
        result = self.session.get(self.url + url, headers=headers)
        if not result.text:
            raise ValueError("result.text is empty!")

        if createDom:
            self.current_page = HtmlDom().createDom(result.text)
        return result
        
    def request_POST(self, url, params, add_headers = {}, createDom=True):

        headers = dict(self.default_headers)
        headers['Content-Type'] = 'application/x-www-form-urlencoded'

        headers.update(add_headers)

        #headers['Content-Length'] = len(params)

        print(params)
        # perform login
        result = self.session.post(self.url + url, data=params, headers=headers)#, cookies=self.cookies)

        try:
            if createDom:
                self.current_page = HtmlDom().createDom(result.text)
        except:
            print("failed reading page in POST " + url)
            print(result.text[:1000])
        
        return result

    def ajax_cmd(self, cmd, params):
        params["cmd"] = cmd
        params["ajaxToken"] = self.ajax_token

        headers = dict(self.default_headers)
        headers.update({"Content-Type":	"application/x-www-form-urlencoded;"})

        response = self.session.post(self.url + "/ajax.php?cmd=quest", data=params, headers=headers)
        #response = self.request_POST("/ajax.php?cmd=quest", params)
        return response

    def login(self):
        print("logging in...")
        response = self.request_GET("/dorf1.php")
        
        doc = self.current_page

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

        # perform login
        response = self.request_POST("/dorf1.php", params, createDom = False)
        
        return True

    def request_village(self, dorf2 = True, failure=False):
        self.request_GET("/dorf1.php?"+str(time.time()))
        vill = Village()
        vill.buildings   = reader.read_resource_fields(self.current_page)
        if not vill.buildings:
            if failure:
                print("Login failed!")
                return None
            self.clear_cookie()
            self.login()
            self.save_cookie()
            return self.request_village(failure = True)
        vill.resource_fields = list(vill.buildings)
        vill.resources   = Resources(reader.read_resources(self.current_page))
        vill.production  = Resources(reader.read_production(self.current_page))

        self.adventure_number = reader.read_adventure_number(self.current_page)
        
        server_time = reader.read_server_time(self.current_page)
        vill.building_queue = reader.read_build_queue(self.current_page, server_time)

        self.ajax_token = reader.read_ajax_token(self.current_page)

        if dorf2:
            self.request_GET("/dorf2.php")
            vill.buildings += reader.read_buildings(self.current_page)
        self.village = vill
        return vill

    def request_hero(self):
        self.request_GET("/hero_inventory.php")
        
        reader.read_hero(self.current_page, self.hero)
        return self.hero

    def submit_form(self, form_id, form_values, form_action = None):
        doc = self.current_page

        if form_action is None:
            form_action = "/" + doc.find(form_id).attr("action")

        inputs = doc.find("%s input" % form_id)
        params = {}

        for inpt in inputs:
            name = (reg_input_name.match(inpt.html()) or _Dummy.inst).group(1)
            value = (reg_input_value.match(inpt.html()) or _Dummy.inst).group(1)
            type1 = (reg_input_type.match(inpt.html()) or _Dummy.inst).group(1)

            #params.append((name, value, type1))
            params[name] = value

        params.update(form_values)

        return self.request_POST(form_action, params)
            
    def save_cookie(self):
        user_db = db.users.find_one({'_id':self._id})
        if user_db is None: raise ValueError(self._id)
        user_db['cookies'] = { k: self.session.cookies._find(k) for k, v in self.session.cookies.items() }
        db.users.save(user_db)

    def load_cookie(self):
        user_db = db.users.find_one({'_id':self._id})
        if user_db is None: return False
        if 'cookies' in user_db:
            self.session.cookies.update(user_db['cookies'])
            return True
        else:
            return False

    def clear_cookie(self):
        self.session = requests.Session()

        self.session.headers.update(self.default_headers)
        
class _Dummy:
    inst = None
    def group(self, n):
        return ""

_Dummy.inst = _Dummy()
