#!/usr/bin/env bash

USER="${1:-$(whoami)}"

# General OS housekeeping ----------------------------------------------------

sudo apt upgrade && sudo apt upgrade
if ! type python3 >/dev/null 2>/dev/null; then
    sudo apt install python3-pip
    pip3 install --upgrade setuptools
fi

# Install Adafruit IO API ----------------------------------------------------

pip3 install --upgrade adafruit-io
echo
echo "✅ adafruit-io python lib installed."
echo

# Fix Debian 11 (bullseye) issue with RPi.GPIO -------------------------------
# @ref: https://dietpi.com/phpbb/viewtopic.php?p=38481
grep -q bullseye /etc/os-release || pip3 install RPi.GPIO==0.7.1a4

# Install Adafruit Blinka lib to talk to CircuitPython API -------------------

sudo pip3 install --upgrade adafruit-python-shell

echo
echo "👋 If you're aleady run this install script before, you probably don't need to reboot when asked."
echo
wget https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py
sudo python3 raspi-blinka.py
rm raspi-blinka.py*

pip3 install --upgrade adafruit_blinka

sudo usermod -aG i2c "$USER"
sudo usermod -aG spi "$USER"
sudo usermod -aG gpio "$USER"

echo
echo "✅ adafruit_blinka python lib installed."
echo
echo "👋 I will listing I2C and SPI devices to check if successful."
echo "   If this fails, you may need to log out and back in as '$USER' to get the new permissions."
ls /dev/i2c* /dev/spi* || exit 1
echo
echo "👋 I will run blinkatest.py to check that digital i/o, I2C anf SPI work."
python3 test/blinkatest.py
echo

# Dependencies for the PM sensor ---------------------------------------------

pip3 install --upgrade pyserial 
sudo usermod -aG dialout "$USER"
echo
echo "✅ pyserial python lib installed."
echo

# Dependencies for the Environmental sensor ----------------------------------

pip3 install adafruit-circuitpython-bme680
echo
echo "✅ adafruit BME680 library python lib installed."
echo

# sudo reboot