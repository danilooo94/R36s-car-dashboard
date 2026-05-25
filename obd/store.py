import threading

class DataStore:
    _defaults = {
        "rpm":        0,
        "speed":      0,
        "oil_temp":   0,
        "water_temp": 0,
        "voltage":    0.0,
        "connected":   False,
        "esp32_port":  "",
    }

    def __init__(self):
        self._lock = threading.Lock()
        self._data = dict(self._defaults)

    def set(self, key, value):
        with self._lock:
            self._data[key] = value

    def snapshot(self):
        with self._lock:
            return dict(self._data)
