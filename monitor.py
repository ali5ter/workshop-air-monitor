#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Garage workshop environment monitor
# Pulling data from localy connected sensors and updating Adafruit IO feeds
# @author Alister Lewis-Bowen <alister@lewis-bowen.org>

import os
import time
import argparse
import requests
import json
import serial
import board
import digitalio
import adafruit_bme680
from urllib.error import HTTPError
from Adafruit_IO import Client, Feed, Group

# Set up input args
all_args = argparse.ArgumentParser(
    description='Monitor sensors connected to RPi measuring environmental conditions'
)
all_args.add_argument('-I', '--init', action="store_true", default=False, help='Initialize the Adafruit IO feeds')
args = vars(all_args.parse_args())

# Monitor configuration
LOOP_DELAY = 5
SAMPLE_TIME = 60/LOOP_DELAY
SAMPLES_DAY = ((60*60*24)/SAMPLE_TIME)/LOOP_DELAY
SERIAL_DEVICE = '/dev/ttyUSB0'
BME680_TEMP_OFFSET = -5
PIR_PIN = board.D4

# Accuweather configuration
AW_URL_BASE = 'http://dataservice.accuweather.com'
AW_URL_CONDITIONS = AW_URL_BASE + '/currentconditions/v1/{0}?apikey={1}&details=true'
AW_KEY_FILE = os.environ['HOME'] + '/.config/accuweather-key'
with open(AW_KEY_FILE, 'r') as file:
    AW_KEY = file.read().replace('\n', '')
# Found using /locations/v1/cities/search Accuweather API call
AW_LOCATION_KEY = '329319'    # Cambridge, MA
AW_CALL_LIMIT = 50 # Free licence limited to 50 API calls per day
AW_SAMPLE_TIME = ((60*60*24)/AW_CALL_LIMIT)/LOOP_DELAY

# Adafruit configuration
AIO_USER = 'ali5ter'
AIO_KEY_FILE = os.environ['HOME'] + '/.config/adafruit-io-key'
with open(AIO_KEY_FILE, 'r') as file:
    AIO_KEY = file.read().replace('\n', '')
AIO_RECREATE_FEEDS = args['init']
AIO_GROUP = 'garage-env'
AIO_FEED_NAMES = [
    'pm10',
    'pm10 ave',
    'pm10 24h ave',
    'pm2.5',
    'pm2.5 ave',
    'pm2.5 24h ave',
    'temperature',
    'temperature ave',
    'temperature local',
    'pressure',
    'pressure ave',
    'pressure local',
    'humidity',
    'humidity ave',
    'humidity local',
    'gas',
    'motion'
]
AIO_FEEDS={}

# TODO: Fetch any stored averages
loop = 0
sample_sds011 = 0
sample_bme860 = 0
c_tempC = 0
c_tempF = 0
c_humidity = 0
c_pressure = 1019
total_humidity = 0
ave_humidity = 0
total_pm_large = 0
ave_pm_large = 0
total_pm_small = 0
ave_pm_small = 0
total_pressure = 0
ave_pressure = 0
total_temp = 0
ave_temp = 0

# Access sensors
ser = serial.Serial(SERIAL_DEVICE)
bme680 = adafruit_bme680.Adafruit_BME680_I2C(board.I2C(), debug=False)
pir = digitalio.DigitalInOut(PIR_PIN)
pir.direction = digitalio.Direction.INPUT
pir_current_value = pir.value
pir_old_value = pir_current_value

# Connection to AIO
aio = Client(AIO_USER, AIO_KEY)

# Connect AIO Feeds
if AIO_RECREATE_FEEDS:
    try:
        aio.delete_group(AIO_GROUP)
    except Exception as err:
        print(f'AIO error: {err}')
    group = Group(name=AIO_GROUP)
    group = aio.create_group(group)
    for name in AIO_FEED_NAMES:
        print(f"Creating feed for {name}")
        feed = Feed(name=name)
        AIO_FEEDS[name] = aio.create_feed(feed, group_key=AIO_GROUP)
    
else:
    group = aio.groups(AIO_GROUP)
    for feed in group.feeds:
        print(f"Connecting feed for {feed.name}")
        AIO_FEEDS[feed.name] = aio.feeds(feed.key)

while True:

    loop += 1
    ts = time.time()

    # Fetch current weather conditions ---------------------------------------

    if (loop-1) % AW_SAMPLE_TIME == 0:
        try:
            print(f"{loop}@{ts}: Fetching current weather conditions")
            r = requests.get(AW_URL_CONDITIONS.format(AW_LOCATION_KEY, AW_KEY))
            r.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error: {http_err}')
        except Exception as err:
            print(f'Other error: {err}')
        else:
            json_data = json.loads(r.text)
            for data in json_data:
                c_tempC = data['Temperature']['Metric']['Value']
                c_tempF = data['Temperature']['Imperial']['Value']
                c_humidity = data['RelativeHumidity']
                c_pressure = data["Pressure"]['Metric']['Value']

        print("\t Current temperature: %0.1f C (%0.1f F)" % (c_tempC, c_tempF))
        print("\t Current relative humidity: %0.1f %%" % c_humidity)
        print("\t Current pressure: %0.3f hPa (mb)" % c_pressure)

        # Write current weather data to AIO feeds
        aio.send_data(AIO_FEEDS['humidity local'].key, c_humidity)
        aio.send_data(AIO_FEEDS['pressure local'].key, c_pressure)
        aio.send_data(AIO_FEEDS['temperature local'].key, c_tempF)

    # Fetch SDS011 data ------------------------------------------------------

    if loop % SAMPLE_TIME == 0:
        sample_sds011 += 1
        print(f"{loop}@{ts}: Fetching SDS011 sensor data")

        data = []
        for index in range(0,10):
            datum = ser.read()
            data.append(datum)
        pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
        pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
        print(f"\t PM2.5 = {pm_small}  PM10 = {pm_large}")

        # Calc rolling averages for SDS011 data
        total_pm_small += pm_small
        total_pm_large += pm_large
        ave_pm_small = total_pm_small/sample_sds011
        ave_pm_large = total_pm_large/sample_sds011
        print(f"\t PM2.5 ave = {ave_pm_small}  PM10 ave = {ave_pm_large}")

        # Write SDS011 data to AIO feeds
        aio.send_data(AIO_FEEDS['pm2.5'].key, pm_small)
        aio.send_data(AIO_FEEDS['pm10'].key, pm_large)
        aio.send_data(AIO_FEEDS['pm2.5 ave'].key, ave_pm_small)
        aio.send_data(AIO_FEEDS['pm10 ave'].key, ave_pm_large)

        # Write 24h SDS011 data to AIO feeds
        if (loop-1) % SAMPLES_DAY == 0:
            aio.send_data(AIO_FEEDS['pm2.4 24h ave'].key, ave_pm_small)
            aio.send_data(AIO_FEEDS['pm10 24h ave'].key, ave_pm_large)
            print(f"\t PM2.5 24h ave = {ave_pm_small}  PM10 24h ave = {ave_pm_large}")

    # Fetch BME680 data ------------------------------------------------------

    if loop % SAMPLE_TIME == 0:
        sample_bme860 += 1
        print(f"{loop}@{ts}: Fetching BME680 sensor data")

        bme680.sea_level_pressure = c_pressure    # Calibrate BME680
        tempC = bme680.temperature + BME680_TEMP_OFFSET
        tempF = (tempC * 1.8) + 32
        gas = bme680.gas
        humidity = bme680.relative_humidity
        pressure = bme680.pressure
        altitude = bme680.altitude
        print("\t Temperature: %0.1f C (%0.1f F)" % (tempC, tempF))
        print("\t Gas: %d ohm" % gas)
        print("\t Humidity: %0.1f %%" % humidity)
        print("\t Pressure: %0.3f hPa" % pressure)
        print("\t Altitude = %0.2f meters" % altitude)

        # Calc rolling average for BME680 date
        total_humidity += humidity
        total_pressure += pressure
        total_temp += tempF
        ave_humidity = total_humidity/sample_bme860
        ave_pressure = total_pressure/sample_bme860
        ave_temp = total_temp/sample_bme860
        print(f"\t Humidity ave = {ave_humidity}  Pressure ave = {ave_pressure}  Temperature ave = {ave_temp}")

        # Write BME680 data to AIO feeds
        aio.send_data(AIO_FEEDS['temperature'].key, tempF)
        aio.send_data(AIO_FEEDS['temperature ave'].key, ave_temp)
        aio.send_data(AIO_FEEDS['gas'].key, gas)
        aio.send_data(AIO_FEEDS['humidity'].key, humidity)
        aio.send_data(AIO_FEEDS['humidity ave'].key, ave_humidity)
        aio.send_data(AIO_FEEDS['pressure'].key, pressure)
        aio.send_data(AIO_FEEDS['pressure ave'].key, ave_pressure)

    # Fetch PIR data ---------------------------------------------------------

    print(f"{loop}@{ts}: Fetching PIR sensor data")

    pir_current_value = pir.value
    if pir_current_value:
        if not pir_old_value:
            motion = 1
            print("\t Motion detected")
        aio.send_data(AIO_FEEDS['motion'].key, 1)
    else:
        if pir_old_value:
            motion = 0
            print("\t Motion ended")
        aio.send_data(AIO_FEEDS['motion'].key, 0)
    pir_old_value = pir_current_value


    time.sleep(LOOP_DELAY)