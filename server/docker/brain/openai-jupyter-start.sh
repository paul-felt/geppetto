#!/bin/bash
/usr/bin/xvfb-run -s "-screen 0 1280x720x24" /usr/local/bin/jupyter-notebook --no-browser --ip=0.0.0.0 --notebook-dir=/notebooks
# this script is meant to be the command for a docker-compose jupyter notebook server capable of rendering openai gym environments.
# Openai gym render() needs an X11 environment to work in--xvfb gives it a virtual in-memory x environment.
# --no-browser says don't pop open a browser when you start this
# ip, port, and notebook dir are set via docker-compose directives
xvfb-run -s '-screen 0 1400x900x24' jupyter-notebook -y --allow-root --no-browser
