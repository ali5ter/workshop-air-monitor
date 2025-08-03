# @file: openweather.py
# @brief: OpenWeather API client for fetching current weather conditions
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import logging
import os
import requests
import json

from urllib.error import HTTPError

class OpenWeather(object):

    def __init__(self, sample_time, openweather_api_key=None, location=None):

        # OpenWeather API base URL
        self.url_base = 'http://api.openweathermap.org/data/2.5/weather'

        # File containing the OpenWeather API access key
        self.key_file = openweather_api_key
        with open(self.key_file, 'r') as file:
            self.key = file.read().replace('\n', '')

        # OpenWeather location used to fetch current conditions (city name or lat/lon tuple)
        if isinstance(location, tuple):
            lat, lon = location
            query = (f"?lat={lat}&lon={lon}&appid={self.key}&units=metric")
        else:
            query = (f"?q={location}&appid={self.key}&units=metric")

        # OpenWeather API method to fetch current weather conditions
        self.conditions_method = self.url_base + query

        # The number of loops after which to fetch sensor data
        self.sample_time = sample_time

        # Current metric temperature
        self.temp_metric = 0

        # Current imperial temperature
        self.temp_imperial = 0
        
        # Current relative humidity
        self.humidity = 0
        
        # Current sea level pressure
        self.pressure = 0

        # Location description
        self.location = ""

        # Conditions description
        self.description = ""

    def get_data(self, loop):

        if (loop-1) % self.sample_time == 0:
            try:
                logging.info(f"[{loop}] Fetching current weather conditions")
                r = requests.get(self.conditions_method, timeout=10)
                r.raise_for_status()
            except HTTPError as http_err:
                logging.error('HTTP error: %s', http_err)
            except Exception as err:
                logging.error('Other error: %s', err)
            else:
                data = r.json()
                # Description of json data: https://openweathermap.org/current
                logging.debug("OpenWeather data: %s", json.dumps(data, indent=4))
                self.temp_metric = data['main']['temp']
                self.temp_imperial = (self.temp_metric * 9/5) + 32
                self.humidity = data['main']['humidity']
                self.pressure = data['main']['pressure']
                self.location = data['name']

            logging.info("\t Current temperature: %0.1f C (%0.1f F)" % (self.temp_metric, self.temp_imperial))
            logging.info("\t Current relative humidity: %0.1f %%" % self.humidity)
            logging.info("\t Current pressure: %0.3f hPa (mb)" % self.pressure)
            logging.info("\t Location: %s" % self.location)

            # Return OpenWeather data in a format suitable for InfluxDB
            return {
                'measurement': 'weather',
                'fields': {
                    'temperature': float(self.temp_imperial),
                    'humidity': float(self.humidity),
                    'pressure': float(self.pressure)
                },
                'tags': {
                    'source': 'openweather',
                    'location': str(self.location)
                }
            }