#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @file: monitor.py
# @brief: Monitor environmental sensors and log data
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import argparse
import os

from dotenv import load_dotenv
from env_monitor.monitor import Monitor

if __name__ == '__main__':

    # Load environment variables from .env file in the current directory
    load_dotenv()
    
    # Set up argument parser
    all_args = argparse.ArgumentParser(
        description='Monitor sensors connected to RPi measuring environmental conditions'
    )
    all_args.add_argument(
        '--server-config',
        type=str,
        default=os.getenv('SERVER_CONFIG'),
        help='Path to the server configuration file'
    )
    all_args.add_argument(
        '--accuweather-api-key',
        type=str,
        default=os.getenv('ACCUWEATHER_API_KEY'),
        help='Path to the Accuweather API key file'
    )
    all_args.add_argument(
        '--accuweather-location-key',
        type=str,
        default=os.getenv('ACCUWEATHER_LOCATION_KEY'),
        help='Accuweather location key for fetching current conditions'
    )
    all_args.add_argument(
        '--pir-sensor-gpio-pin',
        type=int,
        default=int(os.getenv('PIR_SENSOR_GPIO_PIN')),
        help='GPIO pin number for the PIR sensor'
    )
    all_args.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level'
    )
    all_args.add_argument(
        '-d', '--duration',
        type=int,
        help='Duration in minutes to run the monitor (optional, default is to run indefinitely)',
    )
    args = vars(all_args.parse_args())

    monitor = Monitor(loglevel=args['loglevel'],
                      accuweather_api_key=args['accuweather_api_key'],
                      accuweather_location_key=args['accuweather_location_key'],
                      pir_sensor_gpio_pin=args['pir_sensor_gpio_pin'],
                      server_config=args['server_config'])
    monitor.start(duration_minutes=args['duration'])