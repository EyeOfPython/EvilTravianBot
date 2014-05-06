from account import Account
import action
import time
import db
from sm_build import JobManager, build_roman
from datetime import datetime
from event import Event

name = "Peter_10"
email = name.lower() + "@ultimus.no-ip.org"
password = "pass_" + name[::-1] # reverse name
nation = "roman"

"""
http://217.76.38.69:3128
http://81.198.230.182:8080
"""

proxies = [ "http://217.76.38.69:3128" ]

server = (5, 'de')

account = Account(server, name)

#db.users.remove({'name':'Peter_08'}) # wipe users

if account.get_db() is None:
    account.init_db(email, password, nation, proxies)
    account.load_db()
    
    print("need to register this account first:")
    print("ensure the mailserver is running")
    action.action_register(account)
    
    print("wait for activation email to receive...")
    user_db = account.get_db()
    while 'activation_code' not in user_db:
        time.sleep(1)
        user_db = account.get_db()
    
    account.perform_activation("so")
    
account.loadup()

running = True

first_village = next(iter(account.villages.values()))
jm = JobManager(first_village, build_roman)
first_village.event_handlers.append(jm)

first_village.fire_event( Event(first_village, 'job_completed', datetime.now(), job=jm.root) )

while running:
    account.update()
    
    time.sleep(0.05)