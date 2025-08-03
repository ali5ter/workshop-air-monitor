# @file: datacache.py
# @brief: Data cache for storing sensor readings when offline
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import json
import os
from collections import deque
import logging
import tempfile

class DataCache:
    def __init__(self, cache_file=None):
        self.cache_file = cache_file
        self.buffer = self._load_cache()
        logging.debug(f"Cache initialized with {len(self.buffer)} items.")
        logging.debug(f"Cache content: {list(self.buffer)}")

    def _load_cache(self):
        if not os.path.exists(self.cache_file):
            logging.info("Cache file not found. Starting with empty buffer.")
            return deque()
        try:
            logging.debug(f"Loading cache from {self.cache_file}")
            with open(self.cache_file, "r") as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("Cache file is empty")
                data = json.loads(content)
                logging.debug(f"Cache content: {data}")
                return deque(data)
        except Exception as e:
            logging.warning(f"Failed to load cache: {e}. Starting fresh.")
            return deque()

    def append(self, item):
        self.buffer.append(item)
        self._save_cache()

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            dirpath = os.path.dirname(self.cache_file)
            with tempfile.NamedTemporaryFile("w", delete=False, dir=dirpath) as tf:
                json.dump(list(self.buffer), tf)
                tempname = tf.name
            os.replace(tempname, self.cache_file)
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")

    def flush(self, flush_limit, write_func):
        if len(self.buffer) >= flush_limit:
            to_write = list(self.buffer)
            logging.debug(f"Writing {len(to_write)} items to InfluxDB")
            try:
                for item in to_write:
                    logging.debug(f"Writing item: {item}")
                    write_func(**item)
                self.buffer.clear()
                self._save_cache()
                logging.info(f"Flushed {len(to_write)} cached items to Influx.")
            except Exception as e:
                logging.warning(f"Flush failed: {e}. Cache retained.")
        else:
            logging.debug(f"Cache size {len(self.buffer)} is below flush limit {flush_limit}. No action taken.")