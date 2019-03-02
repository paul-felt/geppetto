#!/bin/sh
set -e # fail on error

# run tests
python3 -m unittest /code/test/*.py

