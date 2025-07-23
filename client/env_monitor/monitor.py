# @file: monitor.py
# @brief: Monitor environmental sensors and log data
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import time
import sys
import logging
import signal

from .accuweather import ACW
from .influx import INFLUX
from .bme680 import BME680
from .pir import PIR
from .sds011 import SDS011
from .influx import INFLUX
from memory_profiler import memory_usage

class Monitor(object):

    def __init__(self, loglevel='INFO'):

        self.setup_logging(loglevel=loglevel)

        # The number of seconds to delay at the end of each sample loop
        self.loop_delay = 5

        # The number of loops after which to ask sensors for data
        self.sample_time = int(60/self.loop_delay)

        # The number of loops after which to store 24 hours worth of data
        self.samples_day = int((60*60*24)/self.loop_delay)

        # Default to running state
        self.running = True

        # Set up connection to InfluxDB
        self.influx = INFLUX()
        
        # Set up connection to Accuweather
        self.acw = ACW(self.samples_day, self.aio)

        # Set up connection to the SDS011 sensor
        self.sds011 = SDS011(self.sample_time, self.samples_day, self.aio)

        # Set up the connection to the BME860 sensor
        self.bme680 = BME680(self.sample_time, self.aio)

        # Set up the connection to the PIR sensor
        self.pir = PIR(1, self.aio)

        # Register signal handlers
        signal.signal(signal.SIGINT, self.handle_exit)
        signal.signal(signal.SIGTERM, self.handle_exit)

    def setup_logging(self, loglevel='INFO'):
        numeric_level = getattr(logging, loglevel.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {loglevel}")
        
        logging.basicConfig(
            filename='env_monitor.log',
            encoding='utf-8',
            format='%(asctime)s::%(levelname)s::%(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
            level=numeric_level
        )
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
        logging.info(f"Logging initialized at level: {loglevel}")

    def handle_exit(self, signum, frame):
        logging.info(f"Signal {signum} received. Exiting gracefully.")
        self.running = False

    def cleanup(self):
        logging.info('Cleaning up resources...')
        if hasattr(self.sds011, 'close'):
            self.sds011.close()
        if hasattr(self.bme680, 'close'):
            self.bme680.close()
        if hasattr(self.pir, 'close'):
            self.pir.close()
        if hasattr(self.influx, 'close'):
            self.influx.close()
        logging.info('Cleanup complete.')

    def run_loop(self, loop):
        self.influx.write(self.acw.read(loop))
        self.bme680.current_pressure = self.acw.pressure
        self.influx.write(self.bme680.read(loop))
        self.influx.write(self.sds011.read(loop))
        self.influx.write(self.pir.get_data(loop))

    def start(self, duration_minutes=None):
        logging.info('Started monitor loop')
        loop = 0
        start_time = time.time()
        max_duration = duration_minutes * 60 if duration_minutes else None

        try:
            while self.running:
                if max_duration and (time.time() - start_time) >= max_duration:
                    logging.info("Reached maximum run duration. Exiting.")
                    break

                loop += 1

                mem_before = memory_usage()[0]
                self.run_loop(loop)
                mem_after = memory_usage()[0]
                logging.debug(f"Memory used: {mem_after - mem_before:.2f} MiB")

                time.sleep(self.loop_delay)
        
        finally:
            self.cleanup()
            logging.info('Monitor loop ended')