#!/usr/bin/env bash
# @file: install_sensor_support.sh
# @brief: Script to install necessary libraries and configure the system for sensor support.
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>
# @note: This script is intended for Debian-based systems (e.g., Raspberry Pi OS).

set -e

echo "🔌 Step 1: Running Adafruit raspi-blinka.py to configure hardware interfaces..."

# Download and run Adafruit's official setup script
curl -fsSL https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/adafruit-pi-external/adafruit_shell.py -o adafruit_shell.py
curl -fsSL https://raw.githubusercontent.com/adafruit/Raspberry-Pi-Installer-Scripts/master/raspi-blinka.py -o raspi-blinka.py
sudo python3 raspi-blinka.py
rm -f adafruit_shell.py raspi-blinka.py

echo "📦 Step 2: Upgrading pip and installing sensor libraries..."

# Upgrade pip with system override
sudo python3 -m pip install --upgrade pip --break-system-packages

# Install CircuitPython BME680 library
sudo pip3 install adafruit-circuitpython-bme680 --break-system-packages

# Install pyserial for SDS011 sensor
sudo pip3 install pyserial --break-system-packages

# Add user to 'dialout' group for UART access
echo "🔐 Adding user '$USER' to 'dialout' group..."
sudo usermod -aG dialout "$USER"

echo "🔧 Step 3: Disabling serial console (freeing UART for SDS011)..."

# Remove serial console from /boot/cmdline.txt
sudo sed -i 's/console=serial0,[0-9]* //g' /boot/cmdline.txt

# Ensure UART is enabled in /boot/config.txt
sudo sed -i '/^#*enable_uart=/d' /boot/config.txt
echo "enable_uart=1" | sudo tee -a /boot/config.txt

# Disable serial getty service to avoid console on UART
sudo systemctl disable serial-getty@ttyAMA0.service || true
sudo systemctl disable serial-getty@serial0.service || true

echo "📎 Step 4: Attempting to load i2c and spi kernel modules..."

for module in i2c-dev spi-dev; do
    if modinfo "$module" &>/dev/null; then
        echo "Loading module: $module"
        sudo modprobe "$module"
    else
        echo "⚠️ Warning: Kernel module '$module' not found. Skipping."
    fi
done

echo ""
echo "✅ Setup complete. A reboot is required to apply changes."
echo "   - UART is enabled and serial console is disabled"
echo "   - Sensor libraries installed: BME680, pyserial (for SDS011)"
echo "   - User '$USER' added to 'dialout' group (relogin or reboot required)"

read -p "🔁 Reboot now? [y/N]: " reboot_ans
if [[ "$reboot_ans" =~ ^[Yy]$ ]]; then
    sudo reboot
else
    echo "⚠️ Don't forget to reboot manually: sudo reboot"
fi