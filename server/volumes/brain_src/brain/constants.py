# signal fields
SIGNAL_TS = 'ts'
SIGNAL_TYPE = 'type'
SIGNAL_TYPE_SENSOR = 'sensor'
SIGNAL_TYPE_CONTROL = 'control'
SIGNAL_TYPE_EPISODE = 'episode'
SIGNAL_MEDIATYPE = 'mediatype'
SIGNAL_NAME = 'name'
SIGNAL_ROBOT_NAME = 'robot_name'
SIGNAL_VALUE = 'value'
SIGNAL_SOURCE = 'source'
SIGNAL_SOURCE_WEB = 'web'
SIGNAL_EPISODE_BEGIN = 'begin'
SIGNAL_EPISODE_END = 'end'
# Enforce a sanity test in episode length. Longer than this and there's been a mistake.
MAX_EPISODE_DURATION = 1000 * 60 * 30 # 30 mins
# where should episodes be saved
EPISODE_DIR = '/episodes'
