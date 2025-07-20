#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @file: test_pir.py
# @brief: Test PIR sensor works
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import RPi.GPIO as GPIO
import time

PIR_PIN = 17  # BCM numbering

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)

print("⏳ Waiting for PIR to settle...")
time.sleep(2)
print("✅ Ready. Watching for motion...")

try:
    while True:
        if GPIO.input(PIR_PIN):
            print("🚶 Motion detected!")
        else:
            print("… No motion")
        time.sleep(1)

except KeyboardInterrupt:
    print("👋 Exiting...")
    GPIO.cleanup()