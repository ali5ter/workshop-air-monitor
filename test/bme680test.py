#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Test BME680 sensor works
# @ref https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas

import board
import adafruit_bme680

i2c = board.I2C()
sensor = adafruit_bme680.Adafruit_BME680_I2C(i2c)

# Sea Level Pressure
# @ref https://w1.weather.gov/obhistory/KBOS.html
sensor.seaLevelhPa = 1011.1

print('Temperature: {} degrees C'.format(sensor.temperature))
print('Gas: {} ohms'.format(sensor.gas))
print('Humidity: {}%'.format(sensor.humidity))
print('Pressure: {}hPa'.format(sensor.pressure))
print('Altitude: {} meters'.format(sensor.altitude))