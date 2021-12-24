#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Garage workshop environment monitor
# Pulling data from localy connected sensors and updating Adafruit IO feeds
# @author Alister Lewis-Bowen <alister@lewis-bowen.org>

import os
import time
import requests
import json
import serial
import board
import digitalio
import adafruit_bme680
from urllib.error import HTTPError
from Adafruit_IO import Client

# Monitor configuration
LOOP_DELAY = 5
SAMPLE_TIME = 60/LOOP_DELAY
SAMPLES_DAY = ((60*60*24)/SAMPLE_TIME)/LOOP_DELAY
SERIAL_DEVICE = '/dev/ttyUSB0'
BME680_TEMP_OFFSET = -5
PIR_PIN = board.D4
AW_CALL_LIMIT = 50 # Free licence limited to 50 API calls per day
AW_SAMPLE_TIME = ((60*60*24)/AW_CALL_LIMIT)/LOOP_DELAY

# Accuweather configuration
AW_URL_BASE = 'http://dataservice.accuweather.com'
AW_URL_CONDITIONS = AW_URL_BASE + '/currentconditions/v1/{0}?apikey={1}&details=true'
AW_KEY_FILE = os.environ['HOME'] + '/.config/accuweather-key'
with open(AW_KEY_FILE, 'r') as file:
    AW_KEY = file.read().replace('\n', '')
# Found using /locations/v1/cities/search Accuweather API call
AW_LOCATION_KEY = '329319'    # Cambridge, MA

# Adafruit configuration
AIO_USER = 'ali5ter'
AIO_KEY_FILE = os.environ['HOME'] + '/.config/adafruit-io-key'
with open(AIO_KEY_FILE, 'r') as file:
    AIO_KEY = file.read().replace('\n', '')
AIO_GROUP = 'garage-env'
AIO_FEED_GAS = AIO_GROUP+'.gas'
AIO_FEED_HUMIDITY = AIO_GROUP+'.humidity'
AIO_FEED_HUMIDITY_ROLLING_AVE = AIO_GROUP+'.humidity-rolling-ave'
AIO_FEED_HUMIDITY_LOCAL = AIO_GROUP+'.local-humidity'
AIO_FEED_PM_LARGE = AIO_GROUP+'.pm10'
AIO_FEED_PM_LARGE_ROLLING_AVE = AIO_GROUP+'.pm10-rolling-ave'
AIO_FEED_PM_LARGE_24H_AVE = AIO_GROUP+'.pm10-24h-ave'
AIO_FEED_PM_SMALL = AIO_GROUP+'.pm2-dot-5'
AIO_FEED_PM_SMALL_ROLLING_AVE = AIO_GROUP+'.pm2-dot-5-rolling-ave'
AIO_FEED_PM_SMALL_24H_AVE = AIO_GROUP+'.pm2-dot-5-24h-ave'
AIO_FEED_PRESSURE = AIO_GROUP+'.pressure'
AIO_FEED_PRESSURE_ROLLING_AVE = AIO_GROUP+'.pressure-rolling-ave'
AIO_FEED_PRESSURE_LOCAL = AIO_GROUP+'.local-pressure'
AIO_FEED_TEMP = AIO_GROUP+'.temp'
AIO_FEED_TEMP_ROLLING_AVE = AIO_GROUP+'.temp-rolling-ave'
AIO_FEED_TEMP_LOCAL = AIO_GROUP+'.local-temperature'
AIO_FEED_MOTION = AIO_GROUP+'.motion'

# TODO: Fetch any stored averages
sample = 0
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

# Access AIO feeds
f_gas = aio.feeds(AIO_FEED_GAS)
f_humidity = aio.feeds(AIO_FEED_HUMIDITY)
f_humidity_rolling = aio.feeds(AIO_FEED_HUMIDITY_ROLLING_AVE)
f_humidity_local = aio.feeds(AIO_FEED_HUMIDITY_LOCAL)
f_pm_large = aio.feeds(AIO_FEED_PM_LARGE)
f_pm_large_rolling = aio.feeds(AIO_FEED_PM_LARGE_ROLLING_AVE)
f_pm_large_24h = aio.feeds(AIO_FEED_PM_LARGE_24H_AVE)
f_pm_small = aio.feeds(AIO_FEED_PM_SMALL)
f_pm_small_rolling = aio.feeds(AIO_FEED_PM_SMALL_ROLLING_AVE)
f_pm_small_24h = aio.feeds(AIO_FEED_PM_SMALL_24H_AVE)
f_pressure = aio.feeds(AIO_FEED_PRESSURE)
f_pressure_rolling = aio.feeds(AIO_FEED_PRESSURE_ROLLING_AVE)
f_pressure_local = aio.feeds(AIO_FEED_PRESSURE_LOCAL)
f_temp = aio.feeds(AIO_FEED_TEMP)
f_temp_rolling = aio.feeds(AIO_FEED_TEMP_ROLLING_AVE)
f_temp_local = aio.feeds(AIO_FEED_TEMP_LOCAL)
f_motion = aio.feeds(AIO_FEED_MOTION)

while True:

    sample += 1
    ts = time.time()

    # Fetch current weather conditions ---------------------------------------

    if (sample-1) % AW_SAMPLE_TIME == 0:
        try:
            print(f"{sample}@{ts}: Fetching current weather conditions")
            r = requests.get(AW_URL_CONDITIONS.format(AW_LOCATION_KEY, AW_KEY))
            r.raise_for_status()
        except HTTPError as http_err:
            print(f'HTTP error occurred: {http_err}')
        except Exception as err:
            print(f'Other error occurred: {err}')
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
        aio.send_data(f_humidity_local.key, c_humidity)
        aio.send_data(f_pressure_local.key, c_pressure)
        aio.send_data(f_temp_local.key, c_tempF)

    # Fetch SDS011 data ------------------------------------------------------

    if sample % SAMPLE_TIME == 0:
        print(f"{sample}@{ts}: Fetching SDS011 sensor data")

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
        ave_pm_small = total_pm_small/sample
        ave_pm_large = total_pm_large/sample
        print(f"\t PM2.5 ave = {ave_pm_small}  PM10 ave = {ave_pm_large}")

        # Write SDS011 data to AIO feeds
        aio.send_data(f_pm_small.key, pm_small)
        aio.send_data(f_pm_large.key, pm_large)
        aio.send_data(f_pm_small_rolling.key, ave_pm_small)
        aio.send_data(f_pm_large_rolling.key, ave_pm_large)

        # Write 24h SDS011 data to AIO feeds
        if (sample-1) % SAMPLES_DAY == 0:
            aio.send_data(f_pm_small_24h.key, ave_pm_small)
            aio.send_data(f_pm_large_24h.key, ave_pm_large)
            print(f"\t PM2.5 24h ave = {ave_pm_small}  PM10 24h ave = {ave_pm_large}")

    # Fetch BME680 data ------------------------------------------------------

    if sample % SAMPLE_TIME == 0:
        print(f"{sample}@{ts}: Fetching BME680 sensor data")

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
        ave_humidity = total_humidity/sample
        ave_pressure = total_pressure/sample
        ave_temp = total_temp/sample
        print(f"\t Humidity ave = {ave_humidity}  Pressure ave = {ave_pressure}  Temperature ave = {ave_temp}")

        # Write BME680 data to AIO feeds
        aio.send_data(f_temp.key, tempF)
        aio.send_data(f_gas.key, gas)
        aio.send_data(f_humidity.key, humidity)
        aio.send_data(f_pressure.key, pressure)
        aio.send_data(f_humidity_rolling.key, ave_humidity)
        aio.send_data(f_pressure_rolling.key, ave_pressure)
        aio.send(f_temp_rolling.key, ave_temp)

    # Fetch PIR data ---------------------------------------------------------

    print(f"{sample}@{ts}: Fetching PIR sensor data")

    pir_current_value = pir.value
    if pir_current_value:
        if not pir_old_value:
            motion = 1
            print("\t Motion detected")
        aio.send_data(f_motion.key, 1)
    else:
        if pir_old_value:
            motion = 0
            print("\t Motion ended")
        aio.send_data(f_motion.key, 0)
    pir_old_value = pir_current_value


    # Reset sample counter after 24h 
    if sample % SAMPLES_DAY == 0:
        sample = 0

    time.sleep(LOOP_DELAY)