#FROM crossbario/autobahn-python
#FROM crossbario/autobahn-python-armhf
FROM resin/rpi-raspbian:stretch
MAINTAINER Paul Felt (paul.lewis.felt@gmail.com)

# apt-get
RUN apt-get update && apt-get install \
	python3 \
	python3-pip \
	python3-picamera \
	raspi-config \
	python-smbus \
	i2c-tools 

# configure systems
RUN raspi-config nonint do_camera 1

# pip 
COPY ./requirements.txt /
RUN pip3 install -r /requirements.txt

ADD . /code
WORKDIR /code
COPY ./geppetto_client.py /code/

# TODO: discover the geppetto server
#CMD python3 mearm_client.py --host 192.168.86.22 --web-port=80 --wamp-port=8080
CMD sleep 999999
