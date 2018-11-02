import time

class Planner():
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

