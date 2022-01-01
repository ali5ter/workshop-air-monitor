
import serial
from datetime import datetime

class SDS011(object):

    def __init__(self, sample_time, samples_day, aio):

        # The path to the serial devices
        self.serial_device = '/dev/ttyUSB0'
        
        # The number of loops after which to fetch sensor data
        self.sample_time = sample_time

        # The number of loops after which to write 24h data
        self.samples_day = samples_day

        # Instance of the connection to Adafruit IO
        self.aio = aio

        # Sample counter used for rolling averages
        self.sample_count = 0

        # Total of all PM2.5 samples used for rolling averages
        self.total_pm_small = 0

        # Total of all PM10 samples used for rolling averages
        self.total_pm_large = 0

        # Connect with the SDS011 sensor
        self.sensor = serial.Serial(self.serial_device)

    def add_feeds(self):

        self.aio.feed_names = self.aio.feed_names + [
            'pm10',
            'pm10 ave',
            'pm10 24h ave',
            'pm2.5',
            'pm2.5 ave',
            'pm2.5 24h ave',
        ]

    def get_data(self, loop):

        if loop % self.sample_time == 0:

            dt = datetime.now()
            ts = dt.strftime('%x %X')
            self.sample_count += 1
            print(f"{loop}@{ts}: Fetching SDS011 sensor data")

            data = []
            for index in range(0,10):
                datum = self.sensor.read()
                data.append(datum)
            pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
            pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
            print(f"\t PM2.5 = {pm_small}  PM10 = {pm_large}")

            # Calc rolling averages for SDS011 data
            self.total_pm_small += pm_small
            self.total_pm_large += pm_large
            ave_pm_small = self.total_pm_small/self.sample_count
            ave_pm_large = self.total_pm_large/self.sample_count
            print(f"\t PM2.5 ave = {ave_pm_small}  PM10 ave = {ave_pm_large}")

            # Write SDS011 data to AIO feeds
            self.aio.send('pm2.5', pm_small)
            self.aio.send('pm10', pm_large)
            self.aio.send('pm2.5 ave', ave_pm_small)
            self.aio.send('pm10 ave', ave_pm_large)

            # Write 24h SDS011 data to AIO feeds
            if (loop-1) % self.samples_day == 0:
                self.aio.send_data('pm2.4 24h ave', ave_pm_small)
                self.aio.send_data('pm10 24h ave', ave_pm_large)
                print(f"\t PM2.5 24h ave = {ave_pm_small}  PM10 24h ave = {ave_pm_large}")