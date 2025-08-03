# @file: pir.py
# @brief: PIR sensor client for fetching motion detection data
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import logging
import board
import digitalio

class PIR(object):

    def __init__(self, sample_time, pir_sensor_gpio_pin=None):

        # THE GPIO pin to use as the PIR sensor digital input
        self.input_pin = getattr(board, pir_sensor_gpio_pin)

        # The number of loops after which to fetch sensor data
        self.sample_time = sample_time

        # Sample counter used for rolling averages
        self.sample_count = 0

        # Connect to the PIR sensor
        self.sensor = digitalio.DigitalInOut(self.input_pin)
        self.sensor.direction = digitalio.Direction.INPUT

        # Read initial data from PIR sensor
        self.current_value = self.sensor.value
        self.old_value = self.current_value

    def get_data(self, loop):

        if loop % self.sample_time == 0:

            self.sample_count += 1
            logging.info(f"[{loop}] Fetching PIR sensor data")
            motion = 0

            self.current_value = self.sensor.value
            if self.current_value:
                if not self.old_value:
                    motion = 1
                    logging.info("\t Motion detected")
            else:
                if self.old_value:
                    motion = 0
                    logging.info("\t Motion ended")
            self.old_value = self.current_value

            # Return the data in a format suitable for InfluxDB
            return {
                'measurement': 'motion',
                'fields': {
                    'motion': motion
                },
                'tags': {
                    'sensor': 'pir'
                }
            }