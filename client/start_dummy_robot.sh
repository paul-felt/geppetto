#!/bin/bash

# clean up anything hanging around
docker stop gp_client
docker rm gp_client

# copy the base python client into the docker image
cp geppetto_client.py docker/dummy/

# build and run
docker build docker/dummy -t gp_client
docker run --name gp_client gp_client

