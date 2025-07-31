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
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return deque(json.load(f))
            except Exception:
                logging.warning("Cache file corrupted or unreadable. Starting fresh.")
        return deque()

    def append(self, data):
        self.buffer.append(data)

    def pop(self):
        return self.buffer.popleft()

    def __len__(self):
        return len(self.buffer)

    def flush(self, max_items, write_func):
        flushed = 0
        while self.buffer and flushed < max_items:
            data = self.pop()
            try:
                write_func(data)
                flushed += 1
            except Exception as e:
                logging.error("Failed to flush data to Influx: %s", e)
                self.buffer.appendleft(data)
                break
        self._save_cache()

    def _save_cache(self):
        try:
            with open(self.cache_file, "w") as f:
                json.dump(list(self.buffer), f)
        except Exception as e:
            logging.error("Failed to save cache: %s", e)