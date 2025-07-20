#!/usr/bin/env bash
# @file: install_circuitpython.sh
# @brief: Script to install necessary libraries and configure the system for sensor support.
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>
# @note: This script is intended for Debian-based systems (e.g., Raspberry Pi OS).

set -e

echo "🔧 Updating system packages..."
sudo apt update && sudo apt upgrade -y

echo "🐍 Installing Python 3 and required dev tools..."
sudo apt install -y python3 python3-pip python3-dev python3-setuptools python3-smbus i2c-tools git

echo "📦 Upgrading pip..."
sudo python3 -m pip install --upgrade pip --break-system-packages

echo "🌈 Installing Adafruit Blinka (CircuitPython compatibility layer)..."
sudo pip3 install --upgrade adafruit-blinka --break-system-packages

echo "🌡️ Installing Adafruit CircuitPython library for BME680 sensor..."
sudo pip3 install adafruit-circuitpython-bme680 --break-system-packages

echo "🌫️ Installing pyserial for SDS011 (UART-based sensor)..."
sudo pip3 install --upgrade pyserial --break-system-packages

echo "🔐 Adding user '$USER' to 'dialout' group for serial port access..."
sudo usermod -aG dialout "$USER"

echo "✅ Libraries installed. Now enabling I2C, SPI, and Serial..."

# Enable I2C
if ! grep -q '^dtparam=i2c_arm=on' /boot/config.txt; then
    echo "Enabling I2C..."
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
fi

# Enable SPI
if ! grep -q '^dtparam=spi=on' /boot/config.txt; then
    echo "Enabling SPI..."
    echo "dtparam=spi=on" | sudo tee -a /boot/config.txt
fi

# Enable Serial (UART)
if ! grep -q '^enable_uart=1' /boot/config.txt; then
    echo "Enabling UART (Serial)..."
    echo "enable_uart=1" | sudo tee -a /boot/config.txt
fi

# Disable serial console on UART to free the port for sensors
sudo raspi-config nonint do_serial 1 0

# Add kernel modules if not already in /etc/modules
for module in i2c-dev spi-dev; do
    if ! grep -q "$module" /etc/modules; then
        echo "Adding $module to /etc/modules..."
        echo "$module" | sudo tee -a /etc/modules
    fi
done

echo "📎 Loading i2c, spi, and serial modules..."
sudo modprobe i2c-dev
sudo modprobe spi-dev

echo "♻️ Setup complete. A reboot is recommended to apply changes."
read -r -p "Reboot now? [y/N]: " should_reboot
if [[ "$should_reboot" =~ ^[Yy]$ ]]; then
    sudo reboot
else
    echo "You can reboot later by running: sudo reboot"
fi