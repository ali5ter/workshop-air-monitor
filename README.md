# Workshop Air Monitor

Inspired by [this article](https://www.raspberrypi.com/news/monitor-air-quality-with-a-raspberry-pi/), I wanted to monitor the particulate matter I was breathing in my garage workshop.

Adafruit-IO API:
https://adafruit-io-python-client.readthedocs.io/en/latest/data.html 

SDS011 sesnor datasheet:
https://microcontrollerslab.com/wp-content/uploads/2020/12/NonA-PM-SDS011-Dust-sensor-datasheet.pdf

[Acceptable levels for my area](https://www3.epa.gov/region1/airquality/pm-aq-standards.html).
For PM10: 150 microns per cubic meters based on a 24-hour average
For PM2.5: 35 microns per cubin meters based on a 24-hour average

nohup ./monitor.py &

