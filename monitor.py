#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Pull data from SDS011 sensor and push it to an AdaFruit IO dashboard
# @author Alister Lewis-Bowen <alister@lewis-bowen.org>

import os, serial, time
from Adafruit_IO import Client

DEVICE='/dev/ttyUSB0'

# Adafruit-IO API:
# https://adafruit-io-python-client.readthedocs.io/en/latest/data.html 
AIO_USER='ali5ter'
AIO_KEY_FILE=os.environ['HOME'] + '/.config/adafruit-io-key'
with open(AIO_KEY_FILE, 'r') as file:
    AIO_KEY = file.read().replace('\n', '')
AIO_FEED_PM_SMALL_NAME='garage-pm-2-dot-5'
AIO_FEED_PM_LARGE_NAME='garage-pm-10'

ser = serial.Serial(DEVICE)
aio = Client(AIO_USER, AIO_KEY)

# TODO:Check feed axists
# feeds = aio.feeds()
# for f in feeds:
#     print('Feed: {0}'.format(f.name))

pm_small_feed = aio.feeds(AIO_FEED_PM_SMALL_NAME)
pm_large_feed = aio.feeds(AIO_FEED_PM_LARGE_NAME)

while True:

    data = []
    # SDS011 sesnor datasheet:
    # https://microcontrollerslab.com/wp-content/uploads/2020/12/NonA-PM-SDS011-Dust-sensor-datasheet.pdf

    for index in range(0,10):
        datum = ser.read()
        data.append(datum)

    pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10

    print(f"Data point: pm25 = {pm_small}  pm10 = {pm_large}")

    aio.send_data(pm_small_feed.key, pm_small)
    aio.send_data(pm_large_feed.key, pm_large)

    time.sleep(10)
