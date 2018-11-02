import sys
import logging

from autobahn.asyncio import component as ab_utils
from autobahn.wamp import types as ab_types
from collections import deque, defaultdict
from brain import constants

logger = logging.getLogger(__name__)

def get_wamp_component(host, wamp_port):
    return ab_utils.Component(
        transports=u"ws://{host}:{port}/ws".format(host=host, port=wamp_port),
        realm=u"realm1",
    )

def subscribe_and_run_forever(host, wamp_port, callback, channel, match='prefix'):
    # create wamp component
    wamp_component = get_wamp_component(host, wamp_port)

    async def on_join(session, details):
        logger.info('wamp component: joining')
        session.subscribe(callback, channel, options=ab_types.SubscribeOptions(match='prefix'))
    
    async def on_leave(session, details):
        logger.info('wamp component: leaving')

    # subscribe an episode writer
    wamp_component.on_join(on_join)
    wamp_component.on_leave(on_leave)

    # run component
    ab_utils.run([wamp_component])

