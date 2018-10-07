#!/bin/bash
set -e

docker build docker/dummy -t gp_client
docker run --name gp_client_1 gp_client

