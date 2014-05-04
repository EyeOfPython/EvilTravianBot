
from travian import Travian
import action

import time

server = "ts5"
region = "de"
user_name = "Douche09"
password = "bag_109"

travian = Travian(server, region, user_name, password, None, "http://217.76.38.69:3128")
action.action_register(travian, 5, 'd09@ultimus.sytes.net')

time.sleep(8)
travian.save_cookie()
print(dict(travian.session.cookies))

