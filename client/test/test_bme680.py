#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @file: test_bme680.py
# @brief: Test BME680 sensor works
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import time
import board
import busio
import adafruit_bme680

i2c = busio.I2C(board.SCL, board.SDA)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c)

# Set sea level pressure in hPa (adjust for your local elevation)
bme680.sea_level_pressure = 1013.25

while True:
    print(f"Temperature: {bme680.temperature:.1f} °C")
    print(f"Gas: {bme680.gas:.1f} ohm")
    print(f"Humidity: {bme680.humidity:.1f} %")
    print(f"Pressure: {bme680.pressure:.1f} hPa")
    print(f"Altitude: {bme680.altitude:.2f} m")
    print("-" * 40)
    time.sleep(2)