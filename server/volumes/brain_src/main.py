import time
import logging
import sys
import time
import argparse
import asyncio
from collections import deque
from multiprocessing import Process

from autobahn.asyncio import component as ab_utils
from autobahn.wamp import types as ab_types

from brain.utils import wamp_utils
from brain.utils import episode_utils
from brain import planning

logger = logging.getLogger(__name__)


class Brain(object):
    def __init__(self, planner_name, episode_dir, session):
        self.planner_name = planner_name
        self.episode_dir = episode_dir
        self.session = session
        self.batch = deque()

    async def on_signal(self, *args, **signal):
        logger.info('INPUT INPUT INPUT')
        self.batch.appendleft(signal)

    async def main_brain_loop(self):
        '''This loop is in charge of understanding sensor input, taking actions in response 
            to the state of the world, and trying to learn from the result.'''
        logger.info('starting main brain loop')
        # initialize stats
        count, start_ts = 0, time.time()
        # choose a planner
        logger.info('using planner {}'.format(self.planner_name))
        if self.planner_name.lower() == 'noop':
            planner = planning.NoopPlanner(self.session)
        elif self.planner_name.lower() == 'twitch':
            planner = planning.TwitchPlanner(self.session)
        else:
            logger.info('unknown planner {}. Defaulting to noop'.format(self.planner_name))
            planner = planning.NoopPlanner(self.session)
        world_state, plan = planner.init()
        while True:
            logger.info('DO DO DO')
            # update world_state, plan
            world_state, plan = planner.update(world_state, plan)
            # execute plan
            planner.execute_plan(plan)
            # stats
            count += 1
            if count % 1000==0:
                logger.info('refresh rate={:.3f} per sec'.format(count/(time.time()-start_ts)))
                count, start_ts = 0, time.time()
            await asyncio.sleep(0.1) # context switch once per prediction cycle to get more 


def main_brain_process(robot_name, planner_name, episode_dir, host, wamp_port):
    logger.warn('brain process for {}'.format(robot_name))
    async def on_brain_join(session, details):
        brain = Brain(planner_name, episode_dir, session)
        logger.info('brain subscribing to {}'.format(robot_name))
        session.subscribe(brain.on_signal, 'gp.robots.{}'.format(robot_name), options=ab_types.SubscribeOptions(match='prefix')),
        asyncio.get_event_loop().create_task(brain.main_brain_loop())
        #asyncio.gather(
        #    # wamp component batches up input
        #    session.subscribe(brain.on_signal, 'gp.robots.{robot_name}'.format(robot_name), options=ab_types.SubscribeOptions(match='prefix')),
        #    # async: brain processes input and takes an action
        #    brain.main_brain_loop()
        #)

    async def on_brain_leave(session, details):
        logger.warn('brain disconnecting from {}'.format(robot_name))

    # create a component and run forever
    component = wamp_utils.get_wamp_component(host, wamp_port)
    component.on_join(on_brain_join)
    component.on_leave(on_brain_leave)
    ab_utils.run([component])

############################################################
# MAIN
############################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode-dir', default='/episodes')
    parser.add_argument('--host', default='plfelt-mbp.local')
    parser.add_argument('--wamp-port', default='5555')
    parser.add_argument('--planner', default='twitch')
    #parser.add_argument('--planner', default='noop')
    args = parser.parse_args()

    # set up logging
    logging.basicConfig(level=logging.DEBUG)

    # wait a few seconds to let the wamp server come fully up, if necessary
    time.sleep(5)

    # Fire off the episode recorder process
    #episode_process = Process(
    #                    target=episode_utils.record_episodes_run_forever, 
    #                    args=(args.episode_dir, args.host, args.wamp_port)
    #)
    #logger.info('Starting Episode Recorder Process')
    #episode_process.start()
    #logger.info('1111111111')

    # TODO: higher level process that monitors robot creation/deletion and starts/stops a process for each
    # Fire off the trainer process
    logger.info('222222222222')
    logger.info('222222222222')
    logger.info('222222222222')
    logger.info('222222222222')
    logger.info('222222222222')
    logger.info('222222222222')
    robot_process = Process(
                        target=main_brain_process,
                        args=('marion', args.planner, args.episode_dir, args.host, args.wamp_port)
    )
    logger.info('3333333333')
    logger.info('Starting main robot loop')
    robot_process.start()

    # Wait for processes to finish
    #episode_process.join()
    robot_process.join()
