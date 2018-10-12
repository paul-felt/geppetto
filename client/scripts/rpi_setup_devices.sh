#!/bin/bash
set -e

# install prereqs
echo "installing apt-get dependencies"
sudo apt-get update && sudo apt-get install \
	python3 \
	python3-pip \
	python3-picamera \
	raspi-config \
	python-smbus \
	i2c-tools 

# pip (look for the docker folder either in . or ..)
echo "installing pip dependencies"
if [ -e ./docker ]; then
	sudo pip3 install -r ./docker/raspberry-pi/requirements.txt
else
	sudo pip3 install -r ../docker/raspberry-pi/requirements.txt
fi

# Option 1: interactive mode
# have to do interactive for now. Tried doing 
# the following non-interactive, and it never seemed 
# to take
echo "To finish, enable i2c and your camera:"
echo "1) open up your start menu -> 'Preferences' -> 'Raspberri Pi Configuration'"
echo "2) open the 'Interfaces' tab and enable 'I2C' and 'Camera'"
## Option 2: noninteractive mode
## use raspi-config in non-interactive mode
#echo "enabling i2c"
#sudo raspi-config nonint do_i2c 1
#echo "enabling camera"
#sudo raspi-config nonint do_camera 1


echo "Finished"
