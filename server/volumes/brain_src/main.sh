#!/bin/sh
set -e # fail on error
WEB_PORT=$1
WAMP_PORT=$2

# run tests
python3 -m unittest /code/test/*.py

# run brain
python3 /code/main.py --web-port=$WEB_PORT --wamp-port=$WAMP_PORT
