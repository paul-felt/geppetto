import sys
from asyncio import async
from autobahn.asyncio import component as ab_utils
from autobahn.wamp import types as ab_types
from collections import deque, defaultdict
from brain import constants

def get_wamp_component(host, wamp_port):
    return ab_utils.Component(
        transports=u"ws://{host}:{port}/ws".format(host=host, port=wamp_port),
        realm=u"realm1",
    )

#class SubscriptionQueue(object):
#    def __init__(self, robot_name, host='localhost', wamp_port=5555, maxsize=1000):
#        self.robot_name = robot_name
#        self.host = host
#        self.wamp_port = wamp_port
#        self.q = defaultdict(deque)
#        self.maxsize = maxsize
#        super().__init__()
#
#    async def handle_signal(self, *args, **kwargs):
##        print('got sensor data',len(args),kwargs.keys())
#        if kwargs is not None and constants.SIGNAL_ROBOT_NAME in kwargs:
#            signal_q = self.q[kwargs[constants.SIGNAL_ROBOT_NAME], kwargs[constants.SIGNAL_TYPE], kwargs[constants.SIGNAL_NAME]]
#            signal_q.append((args, kwargs))
#            # slide window to respect max size
#            while len(signal_q) > self.maxsize:
#                signal_q.popleft()
#
#    def get_queue(self):
#        return self.q
#
#    def __iter__(self):
#        while len(self.q) > 0:
#            yield self.q.popleft()
#
#    async def on_join(self, session, details):
#        print('subscribing to %s','gp.robots.%s'%self.robot_name)
#        sys.stdout.flush()
#        session.subscribe(self.handle_signal, 'gp.robots.%s'%self.robot_name, options=ab_types.SubscribeOptions(match='prefix'))
#
#    def start(self):
#        print('creating wamp component:',self.host, self.wamp_port)
#        self.wamp_component = self._get_wamp_component(self.host, self.wamp_port)
#        print('creating wamp component:',self.wamp_component)
#        self.wamp_component.on_join(self.on_join)
#        self.wamp_component.start()
#
#    def stop(self):
#        self.wamp_component.stop()
