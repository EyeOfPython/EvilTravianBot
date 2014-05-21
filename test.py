from account import Account
import action
import time
import db
from sm_build import JobManager, build_roman
from datetime import datetime
from event import Event
import sys, os
from job import JobReadInbox, JobOpenGoldMenu, JobSellResources

if len(sys.argv) == 1:
    name = "Hans_26"
else:
    name = sys.argv[1]

std_out = sys.stdout
f_out = open('log/player_%s.log' % name, 'w')
class fc_out(object):
    def write(self, s):
        global std_out, f_out
        std_out.write(s)
        f_out.write(s)
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

proxies = [ "http://217.76.38.69:3128" ]
#proxies = [  ]

server = (6, 'de')

account = Account(server, name)

#db.users.remove({}) # wipe users

if account.get_db() is None or account.get_db()['activated'] == False:
    
    print("need to register this account first:")
    print("ensure the mailserver is running")
    if account.get_db() is None:
        account.init_db(email, password, nation, proxies)
        account.load_db()
        action.action_register(account)
    
    print("wait for activation email to receive...")
    user_db = account.get_db()
    while 'activation_code' not in user_db:
        time.sleep(1)
        user_db = account.get_db()
    
    account.perform_activation("so")
    
account.loadup()

first_village = next(iter(account.villages.values()))

running = True

jm = JobManager(first_village, build_roman)
first_village.event_handlers.append(jm)

first_village.fire_event( Event(first_village, 'job_completed', datetime.now(), job=jm.root) )

while running:
    account.update()
    
    time.sleep(0.05)