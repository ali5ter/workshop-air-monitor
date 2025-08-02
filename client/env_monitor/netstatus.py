# @file: netstatus.py
# @brief: Network status checker for monitoring wifi signal strength, quality
# and connectivity.
# @author: Alister Lewis-Bowen <alister@lewis-bowen.org>

import platform
import subprocess
import re
import shutil
import os
import socket

class NetworkStatus:

    def __init__(self, interface="wlan0"):
        self.interface = interface
        self.system = platform.system()

    def get_wifi_status(self):
        if self.system == "Linux":
            return self._get_linux_status()
        elif self.system == "Darwin":
            return self._get_darwin_status()
        else:
            print(f"WiFiStatus: Unsupported system: {self.system}")
            return None, None

    def _get_linux_status(self):
        if shutil.which("iwconfig") is None:
            print("iwconfig not found. Install wireless-tools.")
            return None, None

        try:
            result = subprocess.run(["iwconfig", self.interface], capture_output=True, text=True)
            output = result.stdout

            signal_match = re.search(r"Signal level=(-?\d+) dBm", output)
            quality_match = re.search(r"Link Quality=(\d+)/(\d+)", output)

            signal = int(signal_match.group(1)) if signal_match else None

            quality = None
            if quality_match:
                q_current = int(quality_match.group(1))
                q_max = int(quality_match.group(2))
                quality = round(q_current / q_max * 100, 1)

            return signal, quality

        except Exception as e:
            print(f"[Linux] Failed to get WiFi status: {e}")
            return None, None

    def _get_darwin_status(self):
        airport_path = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport"

        if not os.path.exists(airport_path):
            print("airport utility not found on macOS")
            return None, None

        try:
            result = subprocess.run([airport_path, "-I"], capture_output=True, text=True)
            output = result.stdout

            signal_match = re.search(r"agrCtlRSSI:\s*(-?\d+)", output)
            signal = int(signal_match.group(1)) if signal_match else None

            # No clear "quality" on macOS; consider calculating signal-noise if needed
            return signal, None

        except Exception as e:
            print(f"[Darwin] Failed to get WiFi status: {e}")
            return None, None

    def is_connected(self):
        host = "8.8.8.8"
        port = 53
        timeout = 2
        try:
            socket.create_connection((host, port), timeout)
            return True
        except OSError:
            return False