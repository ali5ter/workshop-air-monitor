# @file: accuweather.py
# @brief: Accuweather API client for fetching current weather conditions
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import logging
import os
import requests
import json

from urllib.error import HTTPError

class ACW(object):

    def __init__(self, samples_day, accuweather_api_key=None, location_key=None):

        # Accuweather API base URL
        self.url_base = 'http://dataservice.accuweather.com'

        # Accuweather API method to fetch current weather conditions
        self.conditions_method = self.url_base + '/currentconditions/v1/{0}?apikey={1}&details=true'

        # File containing the Accuweather API access key
        self.key_file = accuweather_api_key
        with open(self.key_file, 'r') as file:
            self.key = file.read().replace('\n', '')

        # Accuweather location key used to fetch current conditions
        # Found using /locations/v1/cities/search Accuweather API method
        self.location_key = location_key

        # Accuweather API call limit per 24 hours
        self.call_limit = 50 # Free licence limited to 50 API calls per day

        # The number of loops after which to fetch current weather conitions
        self.sample_time = int(samples_day/self.call_limit)

        # Current metric temperature
        self.temp_metric = 0

        # Current imperial temperature
        self.temp_imperial = 0
        
        # Current relative humidity
        self.humidity = 0
        
        # Current sea level pressure
        self.pressure = 0

    def get_data(self, loop):

        if (loop-1) % self.sample_time == 0:
            try:
                logging.info('[%d] Fetching current weather conditions', loop)
                r = requests.get(self.conditions_method.format(self.location_key, self.key))
                r.raise_for_status()
            except HTTPError as http_err:
                logging.error('HTTP error: %s', http_err)
            except Exception as err:
                logging.error('Other error: %s', err)
            else:
                json_data = json.loads(r.text)
                for data in json_data:
                    self.temp_metric = data['Temperature']['Metric']['Value']
                    self.temp_imperial = data['Temperature']['Imperial']['Value']
                    self.humidity = data['RelativeHumidity']
                    self.pressure = data["Pressure"]['Metric']['Value']

            logging.info("\t Current temperature: %0.1f C (%0.1f F)" % (self.temp_metric, self.temp_imperial))
            logging.info("\t Current relative humidity: %0.1f %%" % self.humidity)
            logging.info("\t Current pressure: %0.3f hPa (mb)" % self.pressure)

            # Return Accuweather data in a format suitable for InfluxDB
            return {
                'measurement': 'weather',
                'fields': {
                    'temperature': self.temp_imperial,
                    'humidity': self.humidity,
                    'pressure': self.pressure
                },
                'tags': {
                    'source': 'accuweather',
                    'location': self.location_key
                }
            }