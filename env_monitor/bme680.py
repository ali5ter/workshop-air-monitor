import logging
import board
import adafruit_bme680

class BME680(object):

    def __init__(self, sample_time, aio):

        # The temperature offset used for the BME680 sensor
        # @ref https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas/python-circuitpython
        self.bme680_temp_offset = -5

        # The current sea level pressure
        self.current_pressure = 1015

        # The number of loops after which to fetch sensor data
        self.sample_time = sample_time

        # Instance of the connection to Adafruit IO
        self.aio = aio

        # Sample counter used for rolling averages
        self.sample_count = 0

        # Total of all humidity samples used for rolling averages
        self.total_humidity = 0

        # Total of all pressure samples used for rolling averages
        self.total_pressure = 0

        # Total of all pressure samples used for rolling averages
        self.total_temperature = 0

        # Connect to the BME680 sensor
        self.sensor = adafruit_bme680.Adafruit_BME680_I2C(board.I2C(), debug=False)

    def add_feeds(self):

        self.aio.feed_names = self.aio.feed_names + [
            'temperature',
            'temperature ave',
            'pressure',
            'pressure ave',
            'humidity',
            'humidity ave',
            'gas'
        ]

    def get_data(self, loop):

        if loop % self.sample_time == 0:

            self.sample_count += 1
            logging.info('[%d] Fetching BME680 sensor data', loop)

            self.sensor.sea_level_pressure = self.current_pressure  # Calibrate BME680
            tempC = self.sensor.temperature + self.bme680_temp_offset
            tempF = (tempC * 1.8) + 32
            gas = self.sensor.gas
            humidity = self.sensor.relative_humidity
            pressure = self.sensor.pressure
            altitude = self.sensor.altitude
            logging.info("\t Temperature: %0.1f C (%0.1f F)" % (tempC, tempF))
            logging.info("\t Gas: %d ohm" % gas)
            logging.info("\t Humidity: %0.1f %%" % humidity)
            logging.info("\t Pressure: %0.3f hPa" % pressure)
            logging.info("\t Altitude = %0.2f meters" % altitude)

            # Calc rolling average for BME680 date
            self.total_humidity += humidity
            self.total_pressure += pressure
            self.total_temperature += tempF
            ave_humidity = self.total_humidity/self.sample_count
            ave_pressure = self.total_pressure/self.sample_count
            ave_temperature = self.total_temperature/self.sample_count
            logging.info(f"\t Humidity ave = {ave_humidity}  Pressure ave = {ave_pressure}  Temperature ave = {ave_temperature}")

            # Write BME680 data to AIO feeds
            self.aio.send('temperature', tempF)
            self.aio.send('temperature ave', ave_temperature)
            self.aio.send('gas', gas)
            self.aio.send('humidity', humidity)
            self.aio.send('humidity ave', ave_humidity)
            self.aio.send('pressure', pressure)
            self.aio.send('pressure ave', ave_pressure)