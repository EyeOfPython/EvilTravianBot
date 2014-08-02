
import re
from datetime import datetime
from urllib.parse import urlencode

import reader

import time
from event import Event
from log import logger
import db

reg_build_link = re.compile('dorf\d\.php\?a=\d{1,3}&amp;c=\w{6}(?!&amp;b)', re.M)

vid_dict = { "roman": 1,
             "teuton": 2,
             "gaul": 3 }

class Action(dict):
    def __init__(self, account, func_action, params, after_job = False):
        self.account = account
        self.func_action = func_action
        self.params = params
        self.after_job = after_job
        self['msg'] = str(self.func_action) + " " + str(params)

    def execute(self, account = None):
        logger.log_note("execute action", "Execute: %s(%s)" % (self.func_action.__name__, self.params))
        self.func_action(account or self.account, *self.params)

def action_register(account):

    r = account.session.post("http://travian.de/ajax.php?cmd=registration",
                             {"cmd": "registration", "activeServerId":account.server[0], "playerName":account.user_name, "password":account.password,
                              "email": account.email, "preRegistrationCode":"", "generalTermsAndConditions":"1", "newsletter":"false"})

    if '"success":true' in r.text:
        return True
    else:
        logger.log_error("register failed", "Registration failed:\n %s" % r.text)
        return False

def action_activate(account, world_id, activation_code):
    r = account.session.post("http://www.travian.%s/ajax.php?cmd=activate" % account.server[1],
                             data={"cmd":"activate", "activationCode":activation_code, "worldId": world_id})

    return r

def action_select_spawn(account, vid, sector):
    """ sector: { nw, no, sw, so } """
    account.request_GET("/activate.php")
    if vid in vid_dict:
        vid = vid_dict[vid]
    account.request_POST("/activate.php?page=vid", { "vid": vid }, createDom=False )

    account.request_POST("/activate.php?page=sector", { "sector": sector }, createDom=False )

def action_quest(account, action, quest= None):
    
    params = {}
    
    if action is not None:
        params["action"] = action
    if quest is not None:
        params["questTutorialId"] = quest

    response = account.ajax_cmd("quest", params)
    if response.text == "":
        logger.log_error("ajax failed", "Ajax request failed at tutorial: action: %s, quest: %s" % (action, quest))

    logger.log_note("quest", response.text, title="Execute %s %s" % (action, quest))

def action_build_up(account, bid):
    doc = account.request_GET("/build.php?id=%d" % bid)

    contract = doc.find("div#contract div.contractLink div.button-container").html()

    try:
        link = '/' + reg_build_link.findall(contract)[0].replace('&amp;', '&')
        # TODO: log this
        
        account.request_GET(link, createDom=False)

        return True
    except:
        return False

def action_build_new(account, bid, gid):
    doc = account.request_GET("/build.php?id=%d" % bid)

    content = doc.find("div#content div#build").html()

    reg = re.compile('dorf2\.php\?a=%d&amp;id=\d{1,3}&amp;c=\w{6}' % gid, re.M)
    
    try:
        link = '/' + reg.findall(content)[0].replace('&amp;', '&')
        # TODO: log this
            
        account.request_GET(link)
        return True
    except:
        return False

def action_hero_attributes(account, resource, attack_behaviour, attributes):
    'cmd=heroSetAttributes&resource=4&attackBehaviour=hide&attributes[power]=0&attributes[offBonus]=0&attributes[defBonus]=0&attributes[productionPoints]=1&ajaxToken=7aeac2a704ae8f60fb51045428071812'
    params = { 'resource': resource, 'attackBehaviour': attack_behaviour }
    for k,v in attributes.items():
        params['attributes[' + k +']'] = v
    
    response = account.ajax_cmd("saveHeroAttributes", params)
    
    
def action_adventure(village):

    doc = village.account.request_GET("/hero_adventure.php")

    adventures = doc.find("form#adventureListForm tr")

    try:
        adventure = next(adventures)
        link = "/" + adventure.find("td.goTo a").attr("href").replace('&amp;', '&')
        timer = datetime.strptime(adventure.find("td.moveTime span").text().strip(), "%H:%M:%S") - datetime(1900, 1, 1)
    except:
        print("no adventures found")
        return
    print(datetime.today(), "start adventure")
    
    village.account.request_GET(link)
    doc2 = village.account.submit_form("form.adventureSendButton", {}, "/start_adventure.php")
    
def action_apply_item(account, item, amount):
    "cmd=heroInventory&id=353199&drid=bag&amount=1&a=98565&c=c779c8&ajaxToken=bc2a6d69c417002631d5a364b89a9132"
    account.ajax_cmd("heroInventory", { 'id': item.id, 'drid': 'bag', 'amount': amount, 'a': account.hero.item_a, 'c': account.hero.item_c })

def action_rename_village(account, village_id, new_name):
    "cmd=changeVillageName&name=Dickery%20Town&did=104258&ajaxToken=4026c27a2adf6f43ada3f9f330d0cd5e"
    account.ajax_cmd("changeVillageName", { 'name':new_name, 'did': village_id })
    
def action_rename_current_village(account, new_name):
    village_id = account.current_village.village_id
    action_rename_village(account, village_id, new_name)
    
def action_sell_resources(village, sell_res, sell_amount, buy_res, buy_amount):
    market_bid = village.get_bid_by_name('marketplace')
    doc = village.account.request_GET('/build.php?id=%d&t=2' % market_bid)
    village.account.submit_form(doc, '.sell_resources', { 'm1': sell_amount,
                                                          'm2': buy_amount,
                                                          'rid1': sell_res,
                                                          'rid2': buy_res })
    