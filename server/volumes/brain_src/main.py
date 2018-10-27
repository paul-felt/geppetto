import time
import logging
import sys
import time

from brain.utils import wamp_utils
from brain.utils import episode_utils

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    time.sleep(10)
    logging.basicConfig(level=logging.DEBUG)
    logger.info('Starting brain processes')
    episode_utils.record_episodes('/episodes', host='plfelt-mbp.local', wamp_port=5555)
