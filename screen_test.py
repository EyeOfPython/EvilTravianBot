'''
Created on 12.05.2014

@author: ruckt
'''

import npyscreen as ns
import sys

class CmdApp(ns.NPSAppManaged):
    
    def onStart(self):
        self.addForm('MAIN', CmdScreen, name="Evil Travian Bot")

class CmdScreen(ns.Form):
    
    def create(self):
        self.name = self.add(ns.TitleText, name = "Name")
        self.date = self.add(ns.TitleText, name = "Date")
        
    def afterEditing(self):
        self.parentApp.setNextForm(None)

CmdApp().run()