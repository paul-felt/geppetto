#!/bin/bash
set -e

# prereqs
sudo apt-get install -y git build-essential python-dev
sudo pip install -r requirements.txt

# enable I2C
echo "We are about to configure your raspberry to allow I2C."
echo "In the next screen choose:"
echo "1. Interfacting Options"
echo "2. I2C"
echo ""
echo "press any key to proceed to configuration"
read
sudo raspi-config

echo "Finished"
