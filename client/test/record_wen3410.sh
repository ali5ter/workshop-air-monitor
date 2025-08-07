#!/usr/bin/env bash
# @file: record_wen3410.sh
# @brief: Script to record IR signals from WEN 3410 remote control.
# @ref: https://www.wenproducts.com/3-speed-remote-controlled-air-filtration-system-3410.html
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>
# @note: This script is intended for Debian-based systems (e.g., Raspberry Pi OS).

[[ -n $DEBUG ]] && set -x
set -eou pipefail

# To emulate the WEN 3410's remote control, we need to record
# the IR signals it sends. This can be done with an IR receiver
# connected to an RPi GPIO pin, and using LIRC (Linux Infrared
# Remote Control) to capture the signals. Once captured, we can
# use LIRC to send the same signals to control the air filtration
# system.

# Hardware requirements:
# - Raspberry Pi with GPIO pins
# - IR receiver module (e.g., TSOP38238)
#   - Receiver OUT pin connected to GPIO 18 (pin 12)
#   - Receiver VCC pin connected to 3.3V (pin 1)
#   - Receiver GND pin connected to GND (pin 6)

if ! command -v irrecord &> /dev/null; then
    echo "📦 LIRC (Linux Infrared Remote Control) is not installed. Installing..."
    sudo apt-get install lirc --no-install-recommends
fi

if ! grep -q "dtoverlay=gpio-ir" /boot/firmware/config.txt; then
    echo "🔧 Configuring LIRC for GPIO pin 18..."
    echo "dtoverlay=gpio-ir,gpio_pin=18" | sudo tee -a /boot/firmware/config.txt
    echo "❌ Run 'sudo reboot' to apply changes. Then come back to this script to record IR signals."
    exit 0
else
    echo "🔧 LIRC is already configured for GPIO pin 18."
fi
# echo "dtoverlay=gpio-ir-tx,gpio_pin=17" >> /boot/firmware/config.txt

echo "📦 Configuring LIRC for IR signal capture..."
sudo systemctl enable lircd
sudo systemctl start lircd

if ls /dev/lirc*; then
    echo "📦 LIRC is ready for use."
else
    echo "❌ LIRC is not ready. Please check the configuration."
    exit 1
fi

# You can manually record the IR signals using using mode2 to capture the raw
# signals like this:
# sudo systemctl stop lircd
# mode2 -d /dev/lirc0

echo "Follow the instructions to record the IR signals from the WEN 3410 remote control."
echo "- Press the buttons on the remote control when asked (multiple times)"
echo "- Name each button clearly, e.g., POWER, SPEED_LOW, SPEED_MEDIUM, TIMER_1H, etc."
echo
echo "🔴 Recording IR signals from WEN 3410 remote control..."
sudo systemctl stop lircd
irrecord -d /dev/lirc0 ~/wen3410.lircd.conf

echo "📎 Recording complete. The configuration file is saved as ~/wen3410.lircd.conf"
echo "and copied to the LIRC configuration directory at /etc/lirc/lircd.conf.d/wen3410.conf"
sudo cp ~/wen3410.lircd.conf /etc/lirc/lircd.conf.d/wen3410.conf
sudo systemctl restart lircd