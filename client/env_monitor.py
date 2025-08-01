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
        help='Path to the server configuration file (optional, defined in .env file)'
    )
    all_args.add_argument(
        '--cache-file',
        type=str,
        default=os.getenv('CACHE_FILE'),
        help='Path to the cache file (optional, defined in .env file)'
    )
    all_args.add_argument(
        '--cache-flush-limit',
        type=int,
        default=int(os.getenv('CACHE_FLUSH_LIMIT', 10)),
        help='Number of items to keep in memory before flushing to disk (optional, defined in .env file, default is 10)'
    )
    all_args.add_argument(
        '--openweather-api-key',
        type=str,
        default=os.getenv('OPENWEATHER_API_KEY'),
        help='Path to the OpenWeather API key file (optional, defined in .env file)'
    )
    all_args.add_argument(
        '--openweather-location-key',
        type=str,
        default=os.getenv('OPENWEATHER_LOCATION_KEY'),
        help='OpenWeather location key for fetching current conditions (optional, defined in .env file)'
    )
    all_args.add_argument(
        '--pir-sensor-gpio-pin',
        type=str,
        default=os.getenv('PIR_SENSOR_GPIO_PIN'),
        help='GPIO pin number for the PIR sensor (optional, defined in .env file)'
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
                      openweather_api_key=args['openweather_api_key'],
                      openweather_location_key=args['openweather_location_key'],
                      pir_sensor_gpio_pin=args['pir_sensor_gpio_pin'],
                      server_config=args['server_config'],
                      cache_file=args['cache_file'],
                      cache_flush_limit=args['cache_flush_limit'])
    monitor.start(duration_minutes=args['duration'])