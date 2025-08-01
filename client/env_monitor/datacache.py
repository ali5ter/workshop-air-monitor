# @file: datacache.py
# @brief: Data cache for storing sensor readings when offline
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import json
import os
from collections import deque
import logging

class DataCache:
    def __init__(self, cache_file=None):
        self.cache_file = cache_file
        self.buffer = self._load_cache()

    def _load_cache(self):
        if not os.path.exists(self.cache_file):
            logging.info("ℹ️ Cache file not found. Starting with empty buffer.")
            return deque()
        try:
            with open(self.cache_file, "r") as f:
                return deque(json.load(f))
        except Exception as e:
            logging.warning(f"⚠️ Failed to load cache: {e}. Starting fresh.")
            return deque()

    def append(self, item):
        self.buffer.append(item)
        self._save_cache()

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(list(self.buffer), f)
        except Exception as e:
            logging.error(f"❌ Failed to save cache: {e}")

    def flush(self, flush_limit, write_func):
        if len(self.buffer) >= flush_limit:
            to_write = list(self.buffer)
            try:
                for item in to_write:
                    write_func(**item)
                self.buffer.clear()
                self._save_cache()
                logging.info(f"✅ Flushed {len(to_write)} cached items to Influx.")
            except Exception as e:
                logging.warning(f"⚠️ Flush failed: {e}. Cache retained.")