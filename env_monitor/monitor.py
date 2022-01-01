import time

from .accuweather import ACW
from .aio import AIO
from .bme680 import BME680
from .pir import PIR
from .sds011 import SDS011

class Monitor(object):

    def __init__(self):
        
        # The number of seconds to delay at the end of each sample loop
        self.loop_delay = 5

        # The number of loops after which to ask sensors for data
        self.sample_time = int(60/self.loop_delay)

        # The number of loops after which to store 24 hours worth of data
        self.samples_day = int((60*60*24)/self.loop_delay)

        # Set upi connection to Adafruit IO
        self.aio = AIO()
        
        # Set up connection to Accuweather
        self.acw = ACW(self.samples_day, self.aio)

        # Set up connection to the SDS011 sensor
        self.sds011 = SDS011(self.sample_time, self.samples_day, self.aio)

        # Set up the connection to the BME860 sensor
        self.bme680 = BME680(self.sample_time, self.aio)

        # Set up the connection to the PIR sensor
        self.pir = PIR(1, self.aio)
        

    def connect_feeds(self, initialize_feeds=False):

        self.acw.add_feeds()
        self.sds011.add_feeds()
        self.bme680.add_feeds()
        self.pir.add_feeds()

        self.aio.connect_feeds(init=initialize_feeds)

    def start(self):  

        loop = 0      

        while True:

            loop += 1

            self.acw.get_data(loop)
            self.bme680.current_pressure = self.acw.pressure

            self.sds011.get_data(loop)
            self.bme680.get_data(loop)
            self.pir.get_data(loop)

            time.sleep(self.loop_delay)