# @file: datacache.py
# @brief: Data cache for storing sensor readings when offline
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import json
import os
from collections import deque
import logging

class DataCache:
    def __init__(self, cache_file=None, flush_limit=None):
        self.cache_file = cache_file
        self.flush_limit = flush_limit
        self.buffer = self._load_cache()
        self.unsaved_count = 0  # Track number of new unsaved entries

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

    def add(self, item):
        self.buffer.append(item)
        self.unsaved_count += 1
        if self.unsaved_count >= self.flush_limit:
            self._save_cache()

    def _save_cache(self):
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, "w") as f:
                json.dump(list(self.buffer), f)
            logging.info(f"📝 Flushed cache to disk ({len(self.buffer)} items)")
            self.unsaved_count = 0
        except Exception as e:
            logging.error(f"❌ Failed to save cache: {e}")

    def flush(self):
        """Manually force flush (e.g., at shutdown or reconnect)."""
        self._save_cache()

    def drain(self):
        """Returns a list of buffered items and clears the buffer."""
        drained = list(self.buffer)
        self.buffer.clear()
        self.unsaved_count = 0
        self._save_cache()
        return drained

    def is_empty(self):
        return not self.buffer