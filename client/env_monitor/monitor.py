# @file: monitor.py
# @brief: Monitor environmental sensors and log data
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import time
import sys
import logging
import signal

from .openweather import OpenWeather
from .influx import InfluxDB
from .netstatus import NetworkStatus
from .datacache import DataCache
from .sensors.bme680 import BME680
from .sensors.pir import PIR
from .sensors.sds011 import SDS011
from memory_profiler import memory_usage

class Monitor(object):

    def __init__(self, loglevel='INFO', openweather_api_key=None, openweather_location_key=None,
                 pir_sensor_gpio_pin=None, server_config=None, cache_file=None, cache_flush_limit=None):

        # The log level for the monitor
        self.setup_logging(loglevel=loglevel)

        # The API key for OpenWeather
        self.openweather_api_key = openweather_api_key
        logging.debug(f"OpenWeather API key set: {self.openweather_api_key}")

        # The OpenWeather location key for fetching current conditions
        self.openweather_location_key = openweather_location_key
        logging.debug(f"OpenWeather location key set: {self.openweather_location_key}")

        # The GPIO pin number for the PIR sensor
        self.pir_sensor_gpio_pin = pir_sensor_gpio_pin
        logging.debug(f"PIR sensor GPIO pin set: {pir_sensor_gpio_pin}")

        # The server configuration file path
        self.server_config = server_config
        logging.debug(f"Server configuration file set: {server_config}")

        # The cache file path for storing monitor data when offline
        self.cache_file = cache_file
        logging.debug(f"Cache file set: {cache_file}")

        # The number of items to keep in memory before flushing to disk
        self.cache_flush_limit = cache_flush_limit
        logging.debug(f"Cache flush limit set: {self.cache_flush_limit}")

        # The number of seconds to delay at the end of each sample loop
        self.loop_delay = 5

        # The number of loops after which to ask sensors for data
        self.sample_time = int(60/self.loop_delay)

        # The number of loops after which to store 24 hours worth of data
        self.samples_day = int((60*60*24)/self.loop_delay)

        # Default to running state
        self.running = True

        # Set up connection to InfluxDB
        self.influx = InfluxDB(self.server_config)

        # Network status checker
        self.network = NetworkStatus()
        # Hardcoded thresholds for signal strength and quality
        # because these are common values for WiFi networks
        self.signal_warn_threshold = -75  # dBm
        self.quality_warn_threshold = 40  # percentage

        # Set up data cache for offline storage
        self.data_cache = DataCache(self.cache_file)
        self.flush_limit = self.cache_flush_limit 

        # Set up connection to OpenWeather
        self.openweather = OpenWeather(self.sample_time, self.openweather_api_key, self.openweather_location_key)

        # Set up connection to the SDS011 sensor
        self.sds011 = SDS011(self.sample_time, self.samples_day)

        # Set up the connection to the BME680 sensor
        self.bme680 = BME680(self.sample_time)

        # Set up the connection to the PIR sensor
        self.pir = PIR(1, self.pir_sensor_gpio_pin)

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
        # If using network, check signal strength and quality
        signal, quality = self.network.get_wifi_status()
        if signal is not None and signal < self.signal_warn_threshold:
            logging.warning(f"⚠️ Weak WiFi Signal: {signal} dBm")
        if quality is not None and quality < self.quality_warn_threshold:
            logging.warning(f"⚠️ Poor WiFi Link Quality: {quality}%")

        # Fetch data from sensors and write to InfluxDB or cache
        for sensor in [self.openweather, self.bme680, self.sds011, self.pir]:
            logging.debug(f"Fetching data from {sensor.__class__.__name__} at loop {loop}")
            data = sensor.get_data(loop)
            if sensor == self.openweather:
                self.bme680.callibrate(self.openweather.pressure)
            if self.network.is_connected():
                try:
                    self.data_cache.flush(self.flush_limit, self.influx.write)
                    # self.influx.write(**data)
                except Exception as e:
                    # logging.warning("⚠️ Influx write failed, caching: %s", e)
                    self.data_cache.append(data)
            else:
                logging.warning("❌ Offline: data cached.")
                # self.data_cache.append(data)

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