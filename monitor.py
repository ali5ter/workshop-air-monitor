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
AIO_FEED_PM_LARGE='garage-env.pm10'
AIO_FEED_PM_LARGE_ROLLING_AVE='garage-env.pm10-rolling-ave'
AIO_FEED_PM_LARGE_24H_AVE='garage-env.pm10-24h-ave'
AIO_FEED_PM_SMALL='garage-env.pm2-dot-5'
AIO_FEED_PM_SMALL_ROLLING_AVE='garage-env.pm2-dot-5-rolling-ave'
AIO_FEED_PM_SMALL_24H_AVE='garage-env.pm2-dot-5-24h-ave'
AIO_FEED_PRESSURE='garage-env.pressure'
AIO_FEED_TEMP='garage-env.temp'
aio = Client(AIO_USER, AIO_KEY)

AW_URL_BASE='http://dataservice.accuweather.com'
AW_URL_CONDITIONS=AW_URL_BASE + '/currentconditions/v1/{0}?apikey={1}&details=true'
AW_KEY_FILE=os.environ['HOME'] + '/.config/accuweather-key'
with open(AW_KEY_FILE, 'r') as file:
    AW_KEY = file.read().replace('\n', '')
# Found using /locations/v1/cities/search Accuweather API call
AW_LOCATION_KEY='329319'    # Cambridge, MA
# TODO: Fetch pressure for each read of BME680 sensor
try:
    r = requests.get(AW_URL_CONDITIONS.format(AW_LOCATION_KEY, AW_KEY))
    r.raise_for_status()
except HTTPError as http_err:
    print(f'HTTP error occurred: {http_err}')
except Exception as err:
    print(f'Other error occurred: {err}')
else:
    json_data = json.loads(r.text)
    for p in json_data:
        pressure=p["Pressure"]['Metric']['Value']

DEVICE='/dev/ttyUSB0'
ser = serial.Serial(DEVICE)

i2c = board.I2C()
bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, debug=False)
# TODO: Set pressure for each read of BME680 sensor
bme680.sea_level_pressure = pressure
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
total_pm_large = 0
ave_pm_large = 0
total_pm_small = 0
ave_pm_small =0

while True:

    data = []
    for index in range(0,10):
        datum = ser.read()
        data.append(datum)
        
    sample += 1
    ts = time.time()
    pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
    tempC = bme680.temperature + temperature_offset
    tempF = (tempC * 1.8) + 32
    gas = bme680.gas
    humidity = bme680.relative_humidity
    pressure = bme680.pressure
    altitude = bme680.altitude

    print(f"{sample}@{ts}: Current sensor outputs")
    print(f"\t PM2.5 = {pm_small}  PM10 = {pm_large}")
    print("\t Temperature: %0.1f C (%0.1f F)" % (tempC, tempF))
    print("\t Gas: %d ohm" % gas)
    print("\t Humidity: %0.1f %%" % humidity)
    print("\t Pressure: %0.3f hPa" % pressure)
    print("\t Altitude = %0.2f meters" % altitude)

    aio.send_data(f_pm_small.key, pm_small)
    aio.send_data(f_pm_large.key, pm_large)
    aio.send_data(f_temp.key, tempF)
    aio.send_data(f_gas.key, gas)
    aio.send_data(f_humidity.key, humidity)
    aio.send_data(f_pressure.key, pressure)

    total_pm_small += pm_small
    total_pm_large += pm_large
    ave_pm_small = total_pm_small/sample
    ave_pm_large = total_pm_large/sample
    print(f"\t PM2.5 ave = {ave_pm_small}  PM10 ave = {ave_pm_large}")
    aio.send_data(f_pm_small_rolling.key, ave_pm_small)
    aio.send_data(f_pm_large_rolling.key, ave_pm_large)

    if sample == (60*60*24)/SAMPLE_TIME:
        print(f"\t PM2.5 24h ave = {ave_pm_small}  PM10 24h ave = {ave_pm_large}")
        aio.send_data(f_pm_small_24h.key, ave_pm_small)
        aio.send_data(f_pm_large_24h.key, ave_pm_large)

    time.sleep(SAMPLE_TIME)
