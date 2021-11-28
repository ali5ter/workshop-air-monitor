# Workshop Climate Monitor

I wanted to monitor the air quality, temperature and pressure of my garage workshop using a single board computer (SBC) like a Raspberry Pi.

As well as controlling my air filtration, sawdust collection and heating systems, I was curious to know baselines for general particulate matter, noxious gasses, pressure and humidity. I also wanted a way to trigger a camera from a motion sensor to record who was going in and out of the workshop.

Instead of creating a web server to present graphs of collected data, I chose to [push data to feeds on Adafruit IO](https://adafruit-io-python-client.readthedocs.io/en/latest/data.html) where I could play with dashboarding the feed data.

I could [trigger other services directly using IFTTT](https://platform.ifttt.com/docs/connect_api) but saw that [Adafruit IO already integrates with IFTTT](https://learn.adafruit.com/using-ifttt-with-adafruit-io).

## Particulate matter monitoring

Inspired by [this article](https://www.raspberrypi.com/news/monitor-air-quality-with-a-raspberry-pi/), I figured I could monitor the airbourne sawdust that was not being gathered by my sawdust collection system. If it got above a certain level, I figured I could triger my dust filtration unit.

Using [the SDS011 sensor](https://microcontrollerslab.com/wp-content/uploads/2020/12/NonA-PM-SDS011-Dust-sensor-datasheet.pdf) I could collect data on two standard sizes of particulate matter (PM). According to [the Air Quality Standards in my area](https://www3.epa.gov/region1/airquality/pm-aq-standards.html), the 10 micron particles (PM<sub>10</sub>) should not exceed 150 micrograms per cubic meter (μg/m3) based on a 24-hour average. Similarly, the small nasty stuff that can really hurt you, the 2.5 micron particles (PM<sub>2.5</sub>) should not exceed 35 micrograms per cubic meter (μg/m3) based on a 24-hour average.

## Temperature, humidity, pressure and gas monitoring

Adafruit sell [the amazing BME680](https://learn.adafruit.com/adafruit-bme680-humidity-temperature-barometic-pressure-voc-gas) providing the remaining environmental sensing I wanted.

I took advantage of the adafruit_blinka python library to use the CircuitPython hardware API that talks I2C and SPI protocols that sensors often use. Adafruit [explains this and how to install this lib onto your Linux SBC](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi) and I also put the associated commands into the [install.sh](install.sh) script for repeatability.


## Motion sensing

I chose to use [the Pyroelectric ("Passive") InfraRed Sensor from Adafruit](https://learn.adafruit.com/pir-passive-infrared-proximity-motion-sensor) to undersstand if someone was in the workshop. I figured that would be good to cross reference with environmental changes but also wanted a way to trigger a camera to at least understand who was in there. 

## Camera module

...


