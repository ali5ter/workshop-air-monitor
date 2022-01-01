
import board
import digitalio
from datetime import datetime

class PIR(object):

    def __init__(self, sample_time, aio):

        # THE GPIO pin to use as the PIR sensor digital input
        self.input_pin = board.D4

        # The number of loops after which to fetch sensor data
        self.sample_time = sample_time

        # Sample counter used for rolling averages
        self.sample_count = 0

        # Instance of the connection to Adafruit IO
        self.aio = aio

        # Connect to the PIR sensor
        self.sensor = digitalio.DigitalInOut(self.input_pin)
        self.sensor.direction = digitalio.Direction.INPUT

        # Read initial data from PIR sensor
        self.current_value = self.sensor.value
        self.old_value = self.current_value


    def add_feeds(self):

        self.aio.feed_names = self.aio.feed_names + [
            'motion'
        ]

    def get_data(self, loop):

        if loop % self.sample_time == 0:

            dt = datetime.now()
            ts = dt.strftime('%x %X')
            self.sample_count += 1
            print(f"{loop}@{ts}: Fetching PIR sensor data")

            self.current_value = self.sensor.value
            if self.current_value:
                if not self.old_value:
                    motion = 1
                    print("\t Motion detected")
                self.aio.send('motion', 1)
            else:
                if self.old_value:
                    motion = 0
                    print("\t Motion ended")
                self.aio.send('motion', 0)
            self.old_value = self.current_value