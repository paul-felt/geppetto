import time
import asyncio
from asyncio import async
import sys
from brain.utils.wamp_utils import SubscriptionQueue
from brain import constants

def get_ts(signal):
    signal.get(float(constants.SIGNAL_TS),time.time())

def begins_episode(signal, episode_ts):
    # already started
    if curr_episode is not None:
        return False
    # Manual/web control signals start a new episode
    return signal.get(constants.SIGNAL_TYPE) == constants.SIGNAL_TYPE_CONTROL and \
        signal.get(constants.SIGNAL_SOURCE) == constants.SIGNAL_SOURCE_WEB

def ends_episode(signal, curr_episode, episode_timeout=constants.EPISODE_TIMEOUT):
    # can't end what hasn't started
    if curr_episode is None:
        return False
    # time out? (too long since last signal for these to be connected)
    return (get_ts(signal) - curr_episode[-1]) > episode_timeout

async def record_episodes(episode_dir, robot_name, host, wamp_port):
    qf = SubscriptionQueue(robot_name, host=host, wamp_port=wamp_port)
    qf.start()
    curr_episode = None
    while True:
        time.sleep(1) # we burned through the whole queue. Take a breath
        asyncio.sleep(1) # we burned through the whole queue. Take a breath

        for signal in qf:
            print("AAA",signal)
            sys.stdout.flush()

            # episode end
            if ends_episode(signal, curr_episode):
                # save the current episode to disk and null the curr_episode
                save_episode(curr_episode, episode_dir)
                curr_episode = None

            # episode begin
            if begins_episode(signal, curr_episode):
                curr_episode = []

            # existing episode
            if curr_episode is not None:
                curr_episode.append(signal)
