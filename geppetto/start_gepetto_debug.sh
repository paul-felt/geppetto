#!/bin/sh
set -e

# (Optional) REDIS Teardown 
# docker stop myredis; docker rm myredis

# REDIS Setup 
# fire up the redis docker container in the background -d (it internally exposes 6379, so no need for -p)
if ! docker ps -a | grep myredis; then
  # first time
  docker run --name myredis -d redis redis-server -p 6379:6379 -v data:/data
else
  # already exists but was down
  docker start myredis
fi

# Flask
python -i server.py
