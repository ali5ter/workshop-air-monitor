#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @file: test_sds011.py
# @brief: Test SDS011 sensor works
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import serial
import struct
import time

ser = serial.Serial("/dev/serial0", baudrate=9600, timeout=2)

def read_sds011():
    while True:
        byte = ser.read(1)
        if byte == b"\xaa":
            data = ser.read(9)
            if data[0] == 0xC0 and data[8] == 0xAB:
                pm25 = (data[2] + data[3]*256) / 10.0
                pm10 = (data[4] + data[5]*256) / 10.0
                return pm25, pm10

while True:
    try:
        pm25, pm10 = read_sds011()
        print(f"PM2.5: {pm25:.1f} µg/m³  |  PM10: {pm10:.1f} µg/m³")
        time.sleep(5)
    except Exception as e:
        print(f"Error: {e}")