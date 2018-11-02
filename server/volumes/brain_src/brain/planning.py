import time
import random
import logging

logger = logging.getLogger(__name__)

class Planner(object):
    def __init__(self, session):
        pass
    def init(self):
        raise NotImplementedError()
    def update(self, world_state, plan):
        raise NotImplementedError()
    def execute_plan(self, plan):
        raise NotImplementedError()
        

class NoopPlanner(Planner):
    def init(self):
        return None, None
    def update(self, world_state, plan):
        time.sleep(0.01)
        return None, None
    def execute_plan(self, plan):
        time.sleep(0.01)
        pass

class TwitchPlanner(Planner):
    def __init__(self, session):
        self.session = session
        self.ts = time.time()
    def init(self):
        return None, None
    def update(self, world_state, plan):
        # every 1 second twitch 
        #elapsed = time.time() - self.ts
        #if elapsed > 1:
        # emit twitch
        msg = {
            'value' : random.random()*200 + 150,
            'robot_name': 'marion',
            'name': 'claw',
            'type': 'control',
            'source': 'brain',
            'ts': time.time()*1000,
        }
        logger.info('PUBLISH CLAW')
        self.session.publish('gp.robots.marion.controls.claw', **msg)
        self.ts = time.time()

        time.sleep(1) # keep it from burning all the cpu
        return None, None
    def execute_plan(self, plan):
        time.sleep(0.01)
        pass

