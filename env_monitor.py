#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse

from env_monitor.monitor import Monitor

if __name__ == '__main__':

    all_args = argparse.ArgumentParser(
        description='Monitor sensors connected to RPi measuring environmental conditions'
    )
    all_args.add_argument(
        '-I', '--init',
        action="store_true", 
        default=False, 
        help='Initialize the Adafruit IO feeds'
    )
    args = vars(all_args.parse_args())

    monitor = Monitor()
    monitor.connect_feeds(args['init'])
    monitor.start()