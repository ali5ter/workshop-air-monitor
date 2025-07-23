# @file: sds011.py
# @brief: SDS011 sensor client for fetching air quality data
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import logging
import serial

class SDS011(object):

    def __init__(self, sample_time, samples_day):

        # The path to the serial devices
        self.serial_device = '/dev/ttyUSB0'
        
        # The number of loops after which to fetch sensor data
        self.sample_time = sample_time

        # The number of loops after which to write 24h data
        self.samples_day = samples_day

        # Sample counter used for rolling averages
        self.sample_count = 0

        # Total of all PM2.5 samples used for rolling averages
        self.total_pm_small = 0

        # Total of all PM10 samples used for rolling averages
        self.total_pm_large = 0

        # Connect with the SDS011 sensor
        self.sensor = serial.Serial(self.serial_device)

    def get_data(self, loop):

        if loop % self.sample_time == 0:

            self.sample_count += 1
            logging.info('[%d] Fetching SDS011 sensor data', loop)

            data = []
            for index in range(0,10):
                datum = self.sensor.read()
                data.append(datum)
            pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
            pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
            logging.info(f"\t PM2.5 = {pm_small}  PM10 = {pm_large}")

            # Calc rolling averages for SDS011 data
            self.total_pm_small += pm_small
            self.total_pm_large += pm_large
            ave_pm_small = self.total_pm_small/self.sample_count
            ave_pm_large = self.total_pm_large/self.sample_count
            logging.info(f"\t PM2.5 ave = {ave_pm_small}  PM10 ave = {ave_pm_large}")

            # Return SDS011 data in a format suitable for InfluxDB
            return {
                'measurement': 'particulate_matter',
                'fields': {
                    'pm2.5': pm_small,
                    'pm10': pm_large,
                    'pm2.5_ave': ave_pm_small,
                    'pm10_ave': ave_pm_large
                },
                'tags': {
                    'sensor': 'sds011'
                }
            }