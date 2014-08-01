'''
Created on 22.07.2014

@author: Tobias Ruck
'''
import db
from datetime import datetime
import time

class Logger():
    
    def __init__(self):
        self.table = db.log
        self.log_name = None
        
    def log(self, log_severity, log_type, message, title=None):
        assert self.log_name, "A log name must be set."
        
        if title:
            print(log_severity.upper(), log_type.title(), datetime.now(), "--", title)
            print(message)
        else:
            print(log_severity.upper(), log_type.title(), datetime.now(), "--", message)
        
        self.table.insert({ "log_name": self.log_name, "severity": log_severity, "type": log_type, "message": message, "time": datetime(*datetime.now().timetuple()[:6]), "title": title })
        
    def log_error(self, log_type, message, title=None):
        self.log("error", log_type, message, title)
        
    def log_warn(self, log_type, message, title=None):
        self.log("warn", log_type, message, title)
        
    def log_info(self, log_type, message, title=None):
        self.log("info", log_type, message, title)
        
    def log_note(self, log_type, message, title=None):
        self.log("note", log_type, message, title)
        
logger = Logger()

if __name__ == '__main__':
    pass