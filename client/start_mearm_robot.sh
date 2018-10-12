#!/bin/bash

# Option 1: run directly
PYTHONPATH=$PYTHONPATH:. python3 docker/raspberry-pi/mearm_client.py --host=plfelt-mbp.local --web-port=8080 --wamp-port=5555


# Option 2: run in a container
#
# Note: I'm leaving this around for the future, but 
# I couldn't get the camera to work inside a container.
# I know it's possible because resin.io allows it, but 
# it wasn't worth the effort first time around.
## clean up anything hanging around
#docker stop gp_mearm
#docker rm gp_mearm
#
## copy the base python client into the docker image
#cp geppetto_client.py docker/raspberry-pi/
#
## build 
#docker build docker/raspberry-pi -t gp_mearm
#
## clean up to avoid confusion
#rm docker/raspberry-pi/geppetto_client.py 
#
## run
## Note: --privileged allows the container to access system devices (GPIO pins)
## we could do this in a more targeted way in the future (e.g., --device)
#docker run --name gp_mearm --privileged gp_mearm
