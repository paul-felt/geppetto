import time
import base64
import os
import datetime
import json
import asyncio
import sys
import logging
import random
from collections import defaultdict
from autobahn.asyncio import component as ab_utils
from autobahn.wamp import types as ab_types

from brain.utils import wamp_utils
from brain import constants

logger = logging.getLogger(__name__)

def get_ts(signal):
    return float(signal.get(constants.SIGNAL_TS,time.time()))

def begins_episode(signal, curr_episode):
    # already started
    if curr_episode is not None:
        return False
    # Manual/web control signals start a new episode
    # logger.debug(signal.get(constants.SIGNAL_TYPE), signal.get(constants.SIGNAL_VALUE))
    return signal.get(constants.SIGNAL_TYPE) == constants.SIGNAL_TYPE_EPISODE and \
        signal.get(constants.SIGNAL_VALUE) == constants.SIGNAL_EPISODE_BEGIN

def ends_episode(signal, curr_episode):
    # can't end what hasn't started
    if curr_episode is None:
        return False
    # Manual/web control signals start a new episode
    # logger.debug(signal.get(constants.SIGNAL_TYPE), signal.get(constants.SIGNAL_VALUE))
    return signal.get(constants.SIGNAL_TYPE) == constants.SIGNAL_TYPE_EPISODE and \
        signal.get(constants.SIGNAL_VALUE) == constants.SIGNAL_EPISODE_END

def save_episode(robot_name, curr_episode, episode_dir, max_duration=constants.MAX_EPISODE_DURATION):
    # ignore bogus episodes
    if curr_episode is None or len(curr_episode)<1:
        logger.info('ignoring empty episode')
    duration = get_ts(curr_episode[-1]) - get_ts(curr_episode[0])
    if duration > max_duration:
        logger.info('ignoring too-long episode (duration=%s)'%len())
    # mkdir -p /episodes/<robot_name>
    robot_dir = os.path.join(episode_dir,robot_name)
    try:
        os.makedirs(robot_dir)
    except FileExistsError:
        pass
    # save /episodes/<robot_name>/<date>
    episode_name = datetime.datetime.now().strftime('%Y-%m-%d_%H.%M.%S')
    episode_file = os.path.join(robot_dir,episode_name)
    # convert any binary values to base64 strings
    def encode_val(val):
        if isinstance(val,bytes):
            return base64.b64encode(val).decode('utf-8')
        else:
            return val
    curr_episode = [{k:encode_val(v) for k,v in sig.items()} for sig in curr_episode]
    with open(episode_file,'w') as handle:
        json.dump(curr_episode, handle)
    logger.info('Saved episode for %s to %s', robot_name, episode_file)

def load_episode(robot_name, episode):
    ' return the indicated episode '
    episode_path = os.path.join(constants.EPISODE_DIR,robot_name,episode)
    with open(episode_path) as handle:
        return json.load(handle)

def list_episodes(robot_name):
    ' get a list of all the episodes associated with <robot_name> '
    episode_dir = os.path.join(constants.EPISODE_DIR,robot_name)
    try:
        return os.listdir(episode_dir)
    except OSError:
        return []

def load_random_episode(robot_name):
    ' returns a random episode for the given robot, or None if none exists '
    episodes = list_episodes(robot_name)
    if len(episodes)==0:
        return None
    else:
        return load_episode(robot_name, random.choice(episodes))

class RobotEpisodeRecorder(object):

    def __init__(self, robot_name):
        self.robot_name = robot_name
        self.curr_episode = None

    async def on_signal(self, *args, **signal):
        # episode end
        if ends_episode(signal, self.curr_episode):
            logger.info('Ending episode for %s',self.robot_name)
            # save the current episode to disk and null the curr_episode
            save_episode(self.robot_name, self.curr_episode, constants.EPISODE_DIR)
            self.curr_episode = None

        # episode begin
        if begins_episode(signal, self.curr_episode):
            logger.info('Beginning episode for %s',self.robot_name)
            self.curr_episode = []

        # existing episode
        if self.curr_episode is not None:
            logger.debug('Existing episode for %s',self.robot_name)
            self.curr_episode.append(signal)


class EpisodeRecorder(object):
    def __init__(self):
        self.robot_to_episode = {}
    async def on_signal(self, *args, **signal):
        robot_name = signal['robot_name']
        # make sure we have a recorder for this robot
        if robot_name not in self.robot_to_episode:
            self.robot_to_episode[robot_name] = RobotEpisodeRecorder(robot_name)
        # route the signal through to the right robot recorder
        await self.robot_to_episode[robot_name].on_signal(**signal)

def record_episodes_run_forever(episode_dir, host, wamp_port):
    wamp_utils.subscribe_and_run_forever(host, wamp_port, EpisodeRecorder().on_signal, 'gp.robots')

