#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Garage workshop environment monitor
# Pulling data from localy connected sensors and updating Adafruit IO feeds
# @author Alister Lewis-Bowen <alister@lewis-bowen.org>

import os
import time
import serial
import board
import adafruit_bme680
from Adafruit_IO import Client

SAMPLE_TIME=60
SAMPLES_DAY=(60*60*24)/SAMPLE_TIME
SAMPLES_YEAR=(60*60*24*356)/SAMPLE_TIME

AIO_USER='ali5ter'
AIO_KEY_FILE=os.environ['HOME'] + '/.config/adafruit-io-key'
with open(AIO_KEY_FILE, 'r') as file:
    AIO_KEY = file.read().replace('\n', '')
AIO_FEED_GAS='garage-env.gas'
AIO_FEED_HUMIDITY='garage-env.humidity'
AIO_FEED_PM_LARGE='garage-env.pm-10'
AIO_FEED_PM_LARGE_ROLLING_AVE='garage-env.pm-10-rolling-ave'
AIO_FEED_PM_LARGE_24H_AVE='garage-env.pm-10-24h-ave'
AIO_FEED_PM_SMALL='garage-env.pm-2-dot-5'
AIO_FEED_PM_SMALL_ROLLING_AVE='garage-env.pm-2-dot-5-rolling-ave'
AIO_FEED_PM_SMALL_24H_AVE='garage-env.pm-2-dot-5-24h-ave'
AIO_FEED_PRESSURE='garage-env.pressure'
AIO_FEED_TEMP='garage-env.temp'
aio = Client(AIO_USER, AIO_KEY)

DEVICE='/dev/ttyUSB0'
ser = serial.Serial(DEVICE)

i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
bme680.sea_level_pressure = 1011.1
temperature_offset = -5

# TODO:Check feed axists
# feeds = aio.feeds()
# for f in feeds:
#     print('Feed: {0}'.format(f.name))
f_gas = aio.feeds(AIO_FEED_GAS)
f_humidity = aio.feeds(AIO_FEED_HUMIDITY)
f_pm_large = aio.feeds(AIO_FEED_PM_LARGE)
f_pm_large_rolling = aio.feeds(AIO_FEED_PM_LARGE_ROLLING_AVE)
f_pm_large_24h = aio.feeds(AIO_FEED_PM_LARGE_24H_AVE)
f_pm_small = aio.feeds(AIO_FEED_PM_SMALL)
f_pm_small_rolling = aio.feeds(AIO_FEED_PM_SMALL_ROLLING_AVE)
f_pm_small_24h = aio.feeds(AIO_FEED_PM_SMALL_24H_AVE)
f_pressure = aio.feeds(AIO_FEED_PRESSURE)
f_temp = aio.feeds(AIO_FEED_TEMP)


# TODO: Fetch any stored averages
sample=0
pm_small_total=0
pm_large_total=0
pm_small_mean=0
pm_large_mean=0

while True:

    data = []
    for index in range(0,10):
        datum = ser.read()
        data.append(datum)
        
    sample += 1
    ts = time.time()
    pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
    temp = bme680.temperature + temperature_offset
    gas = bme680.gas
    humidity = bme680.relative_humidity
    pressure = bme680.pressure
    altitude = bme680.altitude

    print(f"{sample}@{ts}: Current sensor outputs")
    print(f"\t PM2.5 = {pm_small}  PM10 = {pm_large}")
    print("\t Temperature: %0.1f C" % temp)
    print("\t Gas: %d ohm" % gas)
    print("\t Humidity: %0.1f %%" % humidity)
    print("\t Pressure: %0.3f hPa" % pressure)
    print("\t Altitude = %0.2f meters" % altitude)

    aio.send_data(pm_small_feed.key, pm_small)
    aio.send_data(pm_large_feed.key, pm_large)

    pm_small_total += pm_small
    pm_large_total += pm_large
    pm_small_mean = pm_small_total/sample
    pm_large_mean = pm_large_total/sample
    print(f"\tRollingMean pm25 = {pm_small_mean}  pm10 = {pm_large_mean}")
    aio.send_data(pm_small_feed_rolling.key, pm_small_mean)
    aio.send_data(pm_large_feed_rolling.key, pm_large_mean)

    if sample == (60*60*24)/SAMPLE_TIME:
        print(f"\t24hMean pm25 = {pm_small_mean}  pm10 = {pm_large_mean}")
        aio.send_data(pm_small_feed_24h.key, pm_small_mean)
        aio.send_data(pm_large_feed_24h.key, pm_large_mean)

    time.sleep(SAMPLE_TIME)
