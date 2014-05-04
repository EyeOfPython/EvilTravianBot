
from travian import Travian

import reader
import action
from resources import Resources

import quest

import time
import random
from datetime import datetime, timedelta

import db
import event

from job import Job

server = "ts5"
worldId = 5
region = "de"


user_name = "Douche09"
password = "bag_109"

nation = "roman"

class EvilTravian():

    def __init__(self, user_name, password, nation, proxy):
        self.travian = Travian(server, region, user_name, password, nation, proxy)

        self.jobs = [ Job.create(job_dict) for job_dict in db.jobs.find({"user_name": user_name}, sort=[("time", 1)]) ]

        user_db = self.get_user_db()
 
        if 'build_idx' in user_db:
            self.build_idx = user_db['build_idx']
        else:
            user_db['build_idx'] = [0, 0]
            self.build_idx = [0, 0]

        db.users.save(user_db)

    def activate(self, sector):
        self.travian.load_cookie()
        user_db = db.users.find_one({"name": self.travian.user_name})
        action.action_activate(self, worldId, user_db['activation_code'])

        self.travian.login()
        self.travian.save_cookie()

        action.action_select_spawn(self.travian, self.travian.nation, sector)
        
        self.travian.request_village()
        quest.skip_tutorial(self)
        action.action_tutorial(self, "next", "Tutorial_15a")

    def load(self):
        self.travian.load_cookie()

        self.travian.request_village()

        self.travian.save_cookie()

    def add_job(self, new_job):
        for i, job in enumerate(self.jobs):
            if new_job['time'] < job['time']:
                self.jobs.insert(i, new_job)
                break
        else:
            self.jobs.append(new_job)

        db.jobs.insert(new_job)

    def execute_job(self, job):
        result = job.check_execution(self)
        
        if 'remove' in result:
            self.jobs.remove(job)
            db.jobs.remove({'_id':job['_id']})
 
        if 'delay' in result:
            if not isinstance(job, JobAdventure):
                print("delay job ", job, "\n by", result['delay'])
            job['time'] += result['delay']

        if 'execute' in result:
            print(datetime.today(), "Executing", job)
            job.execute(self)

    def get_user_db(self):
        return db.users.find_one({'name':self.travian.user_name})

    def start(self):

        while True:

            if self.jobs and self.jobs[0]['time'] - timedelta(seconds=5) <= datetime.today():
                job = self.jobs[0]

                if job['time'] - datetime.today() >= timedelta(seconds=1):
                    
                    time.sleep(5)#(job['time'] - datetime.today()).seconds)

                self.execute_job(job)

                self.jobs.sort(key=hash)

            time.sleep(5)

evil = EvilTravian(user_name, password, nation, "http://217.76.38.69:3128")
    
if __name__ == "__main__":
    from job import JobBuild, JobAdventure
    evil.travian.load_cookie()
    evil.activate("no")
    evil.load()
    #evil.build_idx[1] -= 1
    
    evil.add_job(JobBuild.create_next(JobBuild.build_roman[0][evil.build_idx[0]], datetime.today()))
    evil.add_job(JobBuild.create_next(JobBuild.build_roman[1][evil.build_idx[1]], datetime.today()))
    evil.add_job(JobAdventure({ 'time' : datetime.today() }))
    print("starting bot...")
    
    time.sleep(3)
    
    evil.start()

#action.action_tutorial(evil.travian, "next", "Economy_01")

"""while True:

    break
    
    if len(travian.village.building_queue):

        if nation == "roman":
            may_build = any(bldq["building"][0] <= 4 for bldq in travian.village.building_queue)
        else:
            may_build=False

        if may_build:
            new_time = travian.village.building_queue[0]["time"]

            if nextTime != new_time:
                print("build queue until:", new_time)
                print(travian.village.building_queue[0])
            nextTime = new_time
            
    if nextTime <= datetime.today():
        travian.village = travian.request_village()
        time.sleep(1 + random.random())
        
        if "buildup" in job:
            bid, lvl = job["buildup"]
            bldLvl = travian.village.buildings[bid - 1][2]

            if bldLvl < lvl:
                print(str(datetime.today ()), ':', "build up:", bid, "to:", bldLvl + 1)
                action.action_build_up(travian, bid)
                time.sleep(1 + random.random())
                travian.request_village()

        elif "build_resources" in job:

            #print(travian.village.resource_fields)
            
            next_field = travian.village.get_next_field()

            bld_db = db.buildings[next_field[1]]
            needed_resr = Resources(bld_db['levels'][next_field[2]]['r'])

            print(str(datetime.today()), ':', "build up:", next_field)
            print("resource cost:", needed_resr)
            
            if +(travian.village.resources - needed_resr) != travian.village.resources - needed_resr:
                missing_resr = +(travian.village.resources - needed_resr) - (travian.village.resources - needed_resr) 
                waiting_time = timedelta(hours = max(missing_resr / travian.village.production))

                print("Missing:", missing_resr, "Wait:", waiting_time)

                nextTime = datetime.today() + waiting_time

            #print(next_field)

            

            action.action_build_up(travian, next_field[0])
            time.sleep(1 + random.random())
            travian.request_village()

    
    if travian.hero.status == 'home' and travian.hero.health > 35:
        action.action_adventure(travian)
        time.sleep(1 + random.random())
        travian.request_hero()
    
    time.sleep(25)

    waiting += timedelta(seconds=25)

    if waiting > timedelta(minutes=15):
        print("reloading your mams ass")
        travian.request_village()
        travian.request_hero()
        print(travian.hero)
        waiting = timedelta(seconds=1)"""
        
