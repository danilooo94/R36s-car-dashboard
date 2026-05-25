import csv
import os
import threading
from datetime import datetime

import config

_FIELDS = ["timestamp", "rpm", "speed_kmh", "oil_temp_c", "water_temp_c", "voltage_v"]

_STORE_KEYS = {
    "rpm":        "rpm",
    "speed_kmh":  "speed",
    "oil_temp_c": "oil_temp",
    "water_temp_c": "water_temp",
    "voltage_v":  "voltage",
}


class DataLogger(threading.Thread):
    def __init__(self, store):
        super().__init__(daemon=True)
        self.store = store
        self._stop = threading.Event()
        self._path = self._make_path()

    def _make_path(self):
        os.makedirs(config.LOG_DIR, exist_ok=True)
        filename = datetime.now().strftime("session_%Y-%m-%d_%H-%M-%S.csv")
        return os.path.join(config.LOG_DIR, filename)

    def run(self):
        with open(self._path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=_FIELDS)
            writer.writeheader()
            while not self._stop.is_set():
                self._stop.wait(timeout=config.LOG_INTERVAL)
                if self._stop.is_set():
                    break
                data = self.store.snapshot()
                row = {"timestamp": datetime.now().isoformat(timespec="seconds")}
                for col, key in _STORE_KEYS.items():
                    val = data.get(key, 0)
                    row[col] = round(val, 2) if isinstance(val, float) else val
                writer.writerow(row)
                f.flush()

    def stop(self):
        self._stop.set()

    @property
    def path(self):
        return self._path
