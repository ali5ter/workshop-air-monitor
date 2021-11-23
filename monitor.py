#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Pull data from SDS011 sensor and push it to an AdaFruit IO dashboard
# @author Alister Lewis-Bowen <alister@lewis-bowen.org>

import os
import time

import serial
from Adafruit_IO import Client

DEVICE='/dev/ttyUSB0'
SAMPLE_TIME=60
SAMPLES_DAY=(60*60*24)/SAMPLE_TIME
SAMPLES_YEAR=(60*60*24*356)/SAMPLE_TIME

AIO_USER='ali5ter'
AIO_KEY_FILE=os.environ['HOME'] + '/.config/adafruit-io-key'
with open(AIO_KEY_FILE, 'r') as file:
    AIO_KEY = file.read().replace('\n', '')

AIO_FEED_PM_SMALL_NAME='pm-2-dot-5'
AIO_FEED_PM_SMALL_ROLLING_MEAN='pm-2-dot-5-rolling-mean'
AIO_FEED_PM_SMALL_24H_MEAN='pm-2-dot-5-24h-mean'
AIO_FEED_PM_LARGE_NAME='pm-10'
AIO_FEED_PM_LARGE_ROLLING_MEAN='pm-10-rolling-mean'
AIO_FEED_PM_LARGE_24H_MEAN='pm-10-24h-mean'

ser = serial.Serial(DEVICE)
aio = Client(AIO_USER, AIO_KEY)

# TODO:Check feed axists
# feeds = aio.feeds()
# for f in feeds:
#     print('Feed: {0}'.format(f.name))

pm_small_feed = aio.feeds(AIO_FEED_PM_SMALL_NAME)
pm_small_feed_rolling = aio.feeds(AIO_FEED_PM_SMALL_ROLLING_MEAN)
pm_small_feed_24h = aio.feeds(AIO_FEED_PM_SMALL_24H_MEAN)
pm_large_feed = aio.feeds(AIO_FEED_PM_LARGE_NAME)
pm_large_feed_rolling = aio.feeds(AIO_FEED_PM_LARGE_ROLLING_MEAN)
pm_large_feed_24h = aio.feeds(AIO_FEED_PM_LARGE_24H_MEAN)

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
    pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10

    print(f"{sample}: {SAMPLE_TIME}sSample pm25 = {pm_small}  pm10 = {pm_large}")
    aio.send_data(pm_small_feed.key, pm_small)
    aio.send_data(pm_large_feed.key, pm_large)

    pm_small_total += pm_small
    pm_large_total += pm_large
    pm_small_mean = pm_small_total/sample
    pm_large_mean = pm_large_total/sample
    print(f"{sample}: RollingMean pm25 = {pm_small_mean}  pm10 = {pm_large_mean}")
    aio.send_data(pm_small_feed_rolling.key, pm_small_mean)
    aio.send_data(pm_large_feed_rolling.key, pm_large_mean)

    if sample == (60*60*24)/SAMPLE_TIME:
        print(f"{sample}: 24hMean pm25 = {pm_small_mean}  pm10 = {pm_large_mean}")
        aio.send_data(pm_small_feed_24h.key, pm_small_mean)
        aio.send_data(pm_large_feed_24h.key, pm_large_mean)
        pm_small_total = 0
        pm_large_total = 0

    time.sleep(SAMPLE_TIME)
