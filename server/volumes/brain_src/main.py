import time
import logging
import sys
import time
import argparse
from multiprocessing import Process

from brain.utils import wamp_utils
from brain.utils import episode_utils
from brain import planning

logger = logging.getLogger(__name__)


def main_robot_loop(episode_dir, host, wamp_port):
    '''This loop is in charge of understanding sensor input, taking actions in response 
        to the state of the world, and trying to learn from the result.'''
    # initialize stats
    count, start_ts = 0, time.time()
    # choose a planner
    planner = planning.NoopPlanner()
    world_state, plan = planner.init()
    while True:
        # update world_state, plan
        world_state, plan = planner.update(world_state, plan)
        # execute plan
        planner.execute_plan(plan)
        # stats
        count += 1
        if count % 1000==0:
            logger.info('refresh rate={:.3f} per sec'.format(count/(time.time()-start_ts)))
            count, start_ts = 0, time.time()


############################################################
# MAIN
############################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--episode-dir', default='/episodes')
    parser.add_argument('--host', default='plfelt-mbp.local')
    parser.add_argument('--wamp-port', default='5555')
    args = parser.parse_args()

    # set up logging
    logging.basicConfig(level=logging.DEBUG)
    
    # wait a few seconds to let the wamp server come fully up, if necessary
    time.sleep(5)

    # Fire off the episode recorder process
    episode_process = Process(
                        target=episode_utils.record_episodes, 
                        args=(args.episode_dir, args.host, args.wamp_port)
    )
    logger.info('Starting Episode Recorder Process')
    episode_process.start()

    # TODO: higher level process that monitors robot creation/deletion and starts/stops a process for each
    # Fire off the trainer process
    robot_process = Process(
                        target=main_robot_loop,
                        args=(args.episode_dir, args.host, args.wamp_port)
    )
    logger.info('Starting main robot loop')
    robot_process.start()

    # Wait for processes to finish
    episode_process.join()
    robot_process.join()
