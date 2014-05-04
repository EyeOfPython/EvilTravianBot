from account import Account
import action
import time
import db

name = "Carl_02"
email = name.lower() + "@ultimus.sytes.net"
password = "pass_" + name[::-1] # reverse name
nation = "roman"

proxies = [ "http://217.76.38.69:3128" ]

server = (5, 'de')

account = Account(server, name)

#db.users.remove({}) # wipe users

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

while running:
    account.update()
    
    time.sleep(0.05)