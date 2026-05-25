import threading
import time
import math
import random

class MockReader(threading.Thread):
    def __init__(self, store):
        super().__init__(daemon=True)
        self.store = store
        self._stop = threading.Event()

    def run(self):
        self.store.set("connected", True)
        t = 0.0
        while not self._stop.is_set():
            rpm   = 800 + abs(math.sin(t * 0.3)) * 5200 + random.uniform(-80, 80)
            speed = max(0.0, rpm / 40 + random.uniform(-3, 3))
            oil   = 90 + math.sin(t * 0.05) * 12 + random.uniform(-1, 1)
            water = 87 + math.sin(t * 0.04) * 5  + random.uniform(-0.5, 0.5)
            volt  = 13.8 + math.sin(t * 0.1) * 0.6 + random.uniform(-0.1, 0.1)

            self.store.set("rpm",        rpm)
            self.store.set("speed",      speed)
            self.store.set("oil_temp",   oil)
            self.store.set("water_temp", water)
            self.store.set("voltage",    volt)

            t += 0.1
            self._stop.wait(timeout=0.1)

    def stop(self):
        self._stop.set()
