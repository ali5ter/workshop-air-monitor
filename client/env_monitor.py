#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @file: monitor.py
# @brief: Monitor environmental sensors and log data
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

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
        help='Initialize any feeds before starting the monitor'
    )
    all_args.add_argument(
        '--loglevel',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level'
    )
    args = vars(all_args.parse_args())

    monitor = Monitor()
    monitor.setup_logging(args['loglevel'])
    # monitor.connect_feeds(args['init'])
    monitor.start()