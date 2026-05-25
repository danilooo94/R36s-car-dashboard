import threading
import time
import config
from obdii import Connection, commands

_COMMANDS = [
    ("rpm",        commands["ENGINE_SPEED"]),
    ("speed",      commands["VEHICLE_SPEED"]),
    ("oil_temp",   commands["ENGINE_OIL_TEMP"]),
    ("water_temp", commands["ENGINE_COOLANT_TEMP_ALT"]),
    ("voltage",    commands["VEHICLE_VOLTAGE"]),
]

class OBDReader(threading.Thread):
    def __init__(self, store, host, port):
        super().__init__(daemon=True)
        self.store = store
        self.host = host
        self.port = port
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            try:
                conn = Connection((self.host, self.port), auto_connect=True, fast=True)
                self.store.set("connected", True)
                while not self._stop.is_set():
                    for key, cmd in _COMMANDS:
                        try:
                            resp = conn.query(cmd)
                            self.store.set(key, resp.value or 0)
                        except Exception:
                            pass
                    self._stop.wait(timeout=config.OBD_POLL_INTERVAL)
            except Exception:
                self.store.set("connected", False)
                self._stop.wait(timeout=2)

    def stop(self):
        self._stop.set()
