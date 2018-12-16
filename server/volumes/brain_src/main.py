import time
import logging
import sys
import time
import argparse
import asyncio
import requests
from multiprocessing import Process

from autobahn.asyncio import component as ab_utils
from autobahn.wamp import types as ab_types

from brain.utils import wamp_utils
from brain.utils import episode_utils
from brain import planning

logger = logging.getLogger(__name__)


class Brain(object):
    def __init__(self, robot_info, planner_name, episode_dir, session):
        self.robot_info = robot_info
        self.planner_name = planner_name
        self.episode_dir = episode_dir
        self.session = session
        self.batch = []

    async def on_signal(self, *args, **signal):
        logger.info('INPUT %s:%s', signal['source'], signal['name'])
        self.batch.append(signal)

    async def main_brain_loop(self):
        '''This loop is in charge of understanding sensor input, taking actions in response 
            to the state of the world, and trying to learn from the result.'''
        logger.info('starting main brain loop')
        # initialize stats
        count, start_ts = 0, time.time()
        # choose a planner
        logger.info('using planner {}'.format(self.planner_name))
        if self.planner_name.lower() == 'noop':
            planner = planning.NoopPlanner(self.robot_info, self.session)
        elif self.planner_name.lower() == 'print':
            planner = planning.PrintingPlanner(self.robot_info, self.session)
        elif self.planner_name.lower() == 'twitch':
            planner = planning.TwitchPlanner(self.robot_info, self.session)
        else:
            logger.info('unknown planner {}. Defaulting to noop'.format(self.planner_name))
            planner = planning.NoopPlanner(self.robot_info, self.session)
        world_state, plan = planner.init()
        while True:
            logger.info('ACTION')
            # we want to sleep here long enough to let the signal routine to batch up all incoming data
            await asyncio.sleep(0.1) # context switch once per prediction cycle to get more 
            # update world_state, plan
            world_state, plan = await planner.update(world_state, plan, self.batch)
            self.batch = []
            # stats
            count += 1
            if count % 1000==0:
                logger.info('refresh rate={:.3f} per sec'.format(count/(time.time()-start_ts)))
                count, start_ts = 0, time.time()


def main_brain_process(robot_name, planner_name, episode_dir, host, web_port, wamp_port):
    logger.warn('brain process for {}'.format(robot_name))

    while True:
        try:
            # get robot info
            robot_info = requests.get('http://{}:{}/robots/{}'.format(host, web_port, robot_name)).json()

            async def on_brain_join(session, details):
                brain = Brain(robot_info, planner_name, episode_dir, session)
                logger.info('brain subscribing to {}'.format(robot_name))
                session.subscribe(brain.on_signal, 'gp.robots.{}'.format(robot_name), options=ab_types.SubscribeOptions(match='prefix')),
                asyncio.get_event_loop().create_task(brain.main_brain_loop())

            async def on_brain_leave(session, details):
                logger.warn('brain disconnecting from {}'.format(robot_name))

            # create a wamp component and run forever
            component = wamp_utils.get_wamp_component(host, wamp_port)
            component.on_join(on_brain_join)
            component.on_leave(on_brain_leave)
            ab_utils.run([component])
        except:
            time.sleep(2)
            logger.warn('unable to get robot_info for {}. Trying again...'.format(robot_name))

############################################################
# MAIN
############################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode-dir', default='/episodes')
    parser.add_argument('--host', default='plfelt-mbp.local')
    parser.add_argument('--web-port', default='8080')
    parser.add_argument('--wamp-port', default='5555')
    #parser.add_argument('--planner', default='noop')
    parser.add_argument('--planner', default='print')
    #parser.add_argument('--planner', default='twitch')
    args = parser.parse_args()

    # set up logging
    logging.basicConfig(level=logging.DEBUG)

    # wait a few seconds to let the wamp server come fully up, if necessary
    time.sleep(3)

    # Fire off the episode recorder process
    episode_process = Process(
                        target=episode_utils.record_episodes_run_forever, 
                        args=(args.episode_dir, args.host, args.wamp_port)
    )
    logger.info('Starting Episode Recorder Process')
    episode_process.start()

    # TODO: start a higher level process that monitors robot creation/deletion and starts/stops a process for each robot
    # Fire off the brain process (just one for now)
    robot_process = Process(
                        target=main_brain_process,
                        args=('marion', args.planner, args.episode_dir, args.host, args.web_port, args.wamp_port)
    )
    logger.info('Starting Main Brain Process')
    robot_process.start()

    # Wait for processes to finish
    episode_process.join()
    robot_process.join()
