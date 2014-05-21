
from __future__ import print_function

import asyncore

import smtpd
import sys
from smtpd import SMTPServer

import re

from datetime import datetime

import time

import db

#smtpd.DEBUGSTREAM = sys.stdout

std_out = sys.stdout
f_out = open('server_email.log', 'w')
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

reg = r"(http://www\.travian\.\w{1,4}/\?worldId=\w{1,4}&id=\w*#activation)\n\n-------------------------------------------------------------------------=\n--------------------------------------------------------\n\n[^:]*:\n\n[^:]*:  ([^\n]*)\n[^:]*: .*\n[^:]*: (.*)\n[^:]*: .*\n\n[^:]*: (\w*)"
reg = reg.replace(r'\n', '\n')
r"""
[^:]*:

[^:]*:  (.*)
[^:]*: .*
[^:]*: .*
[^:]*: .*

[^:]*: (\w*)

-------------------------------------------------------------------------=
--------------------------------------------------------
"""
reg_activation = re.compile(reg, re.DOTALL)

class TravianActivatorSMTPServer(SMTPServer):

    def __init__(self):
        SMTPServer.__init__(self, ('0.0.0.0', 25), None)

    def start(self):
        print("Server started")
        asyncore.loop()

    def process_message(self, peer, mailfrom, rcpttos, message_data):

        #print(message_data)
        #print("*** Repr:")
        #print(repr(message_data))
        
        m = reg_activation.search(message_data.replace('=3D', '='))

        if m is not None:
            print("Registration found:", m.group(2), m.group(1), m.group(3))

            time.sleep(2)

            user_db = db.users.find_one({"name":m.group(2)})
            if user_db is None:
                print("player not found:", m.group(2))
            else:
                user_db['activation_link'] = m.group(1)
                user_db['activation_code'] = m.group(4)
                db.users.save(user_db)

            open("email_activation_list.txt", 'a').write("%s=%s\n" % (m.group(2), m.group(1)))
        else:
            print("received non-activation email:")
            print(message_data)
            open("mails/%s.txt" % (str(time.time())), 'w').write(message_data)

server = TravianActivatorSMTPServer()
server.start()

#m = reg_activation.search('strierung bei Travian!\n\nDu hast dich f=C3=BCr die Welt de3 in Travian registriert. Um deinen Acco=\nunt zu\naktivieren klicke bitte\nauf folgenden Link:\n\nhttp://www.travian.de/?worldId=3D3&id=3D997dd86dcd#activation\n\n-------------------------------------------------------------------------=\n--------------------------------------------------------\n\nDeine Zugangsdaten:\n\nSpielername:  Jerk11\nE-Mail-Adresse: jerksparrow11@ultimus.sytes.net\nPasswort: cock321\nSpielwelt: de3\n\nAktivierungscode: 997dd86dcd\n\n-------------------------------------------------------------------------=\n--------------------------------------------------------\n\nTipps zum Spiel:\nIn unserem Travian Answers http://t4.answers.travia'.replace('=3D', '='))
#print(m.group(0))
#print(m.group(1), m.group(2), m.group(3))
