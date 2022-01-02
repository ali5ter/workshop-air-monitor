import logging
import os

from Adafruit_IO import Client, Feed, Group

class AIO(object):

    def __init__(self):

        # Adafruit IO user name
        self.user = 'ali5ter'

        # File containing the Adafruit IO API access key
        self.key_file = os.environ['HOME'] + '/.config/adafruit-io-key'
        with open(self.key_file, 'r') as file:
            self.key = file.read().replace('\n', '')

        # Adafruit IO Feed Group name
        self.group = 'garage-env'

        # Adafruit IO Feed names
        self.feed_names = []

        # Adafruit IO Feed references
        self.feeds = {}

        # Connection to AIO
        self.client = Client(self.user, self.key)

    def connect_feeds(self, init=False):

        if init:
            try:
                self.client.delete_group(self.group)
            except Exception as err:
                logging.error('AIO Client error: %s', err)
            group = Group(name=self.group)
            group = self.client.create_group(group)
            for name in self.feed_names:
                logging.error('AIO Client error: %s', err)
                print(f"Creating feed called, {name}")
                feed = Feed(name=name)
                self.feeds[name] = self.client.create_feed(feed, group_key=self.group)
        else:
            group = self.client.groups(self.group)
            for feed in group.feeds:
                logging.info('Connecting AIO Feed called, %s', feed.name)
                self.feeds[feed.name] = self.client.feeds(feed.key)

    def send(self, name, data):

        if name in self.feeds.keys():
            while True:
                try:
                    self.client.send_data(self.feeds[name].key, data)
                except Exception as err:
                    logging.warning('Unable to send data to AIO: %s', err)
                    continue
                break
        else:
            logging.error('Unable to find AIO Feed called, %s', name)