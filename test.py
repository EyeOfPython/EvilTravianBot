#!/usr/bin/python3
from account import Account
import action
import time
import db
from sm_build import JobManager, build_roman
from datetime import datetime
from event import Event
import sys, os
import reader
from log import logger
import traceback

if len(sys.argv) == 1:
    name = "Sof4"
else:
    name = sys.argv[1]

std_out = sys.stdout
f_out = open('log/player_%s.log' % name, 'w')
class fc_out(object):
    def write(self, s):
        global std_out, f_out
        std_out.write(s)
        f_out.write(s)
        f_out.flush()
    def flush(self):
        global std_out, f_out
        std_out.flush()
        f_out.flush()

sys.stdout = fc_out()

email = name.lower() + "@ultimus.no-ip.org"
password = "pass_" + name[::-1] # reverse name
nation = "roman"

os.environ['HTTP_PROXY'] = ''

"""
http://217.76.38.69:3128
http://81.198.230.182:8080
"""

proxies = [ "http://37.239.46.18:80" ]
#proxies = [  ]

server = (3, 'de')

account = Account(server, name)

logger.log_name = name
logger.log_note("start", "Started the bot")

#db.users.remove({}) # wipe users
#db.states.remove({})

jobs_from_db = True

if account.get_db() is None or account.get_db()['activated'] == False:
    
    logger.log_info("register account", "need to register this account first: ensure the mailserver is running")
    if account.get_db() is None:
        account.init_db(email, password, nation, proxies)
        account.load_db()
        action.action_register(account)
        jobs_from_db = False
    
    logger.log_info("wait for email", "wait for activation email to receive...")
    user_db = account.get_db()
    while 'activation_code' not in user_db:
        time.sleep(1)
        user_db = account.get_db()
    
    account.perform_activation("so")
    
account.loadup()

first_village = next(iter(account.villages.values()))

running = True

doc = account.request_GET("/dorf1.php")
#movements = reader.read_troop_movement_simple(doc)
#print(movements)
#sys.exit()

jm = JobManager(first_village)
first_village.event_handlers.append(jm)
if not jobs_from_db:
    jm.init_from_def(build_roman)
    first_village.fire_event( Event(first_village, 'job_completed', datetime.now(), job=jm.root) )
else:
    jm.init_from_db()
    first_village.refresh()
    first_village.fire_event( Event(first_village, 'job_completed', datetime.now(), job=jm.root) )
    

account.logout()
first_village.refresh()
    
#first_village.fire_event( Event(first_village, 'baum', datetime.now()) )
#sys.exit()

def spawn_web_server():
    pass
    
while running:
    try:
        account.update()
    except Exception as e:
        traceback.print_exc()
        time.sleep(10)
        
    time.sleep(0.05)