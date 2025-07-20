#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @file: test_sds011.py
# @brief: Test SDS011 sensor works
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import serial
import time

ser = serial.Serial("/dev/ttyUSB0")

while True:
    data = []
    for index in range(0,10):
        datum = ser.read()
        data.append(datum)
    pm_small = int.from_bytes(b''.join(data[2:4]), byteorder='little') / 10
    pm_large = int.from_bytes(b''.join(data[4:6]), byteorder='little') / 10
    print(f"PM2.5: {pm_small} µg/m³  |  PM10: {pm_large} µg/m³")
    time.sleep(10)