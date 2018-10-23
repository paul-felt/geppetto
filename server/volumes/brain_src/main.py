import time
from brain.utils import wamp_utils
from brain.utils import episode_utils

if __name__ == '__main__':
    episode_utils.record_episodes('/episodes', host='plfelt-mbp.local', wamp_port=5555)
