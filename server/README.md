Notes:

Useful dev commands:
  - `docker-compose down`: shut geppetto down
  - `docker-compose up`: start geppetto up
  - `docker-compose build`: rebuild all the parts of geppetto
  - `docker ps`: get a list of running containers
  - `docker exec -ti <container_name> /bin/bash`: get a console running in a container
  - `docker logs <container_name>`: see logs from the given container
  - `docker-compose stop brain; docker-compose up brain`: restart just the brain container
  - `docker-compose build brain`: rebuild the brain container (re-clone openai baselines)
  - `xvfb-run -s "-screen 0 1400x900x24" bash`: connect bash to a fake display to run baselines inside docker

WAMP channels
Sensor signals: gp.robots.<robot_name>.sensors.<sensor_name>
Control signal: gp.robots.<robot_name>.controls.<control_name>
