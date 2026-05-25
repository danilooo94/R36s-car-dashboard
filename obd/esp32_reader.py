import glob
import sys
import threading
import json
import serial
import serial.tools.list_ports
import config
import app_log

# Maps ESP32 JSON keys → DataStore keys
_KEY_MAP = {
    "coolant_temp": "water_temp",
    "oil_temp":     "oil_temp",
    "battery_v":    "voltage",
}

# Known USB VID/PID combos used on ESP32 devkits, in priority order
_ESP32_VIDPID = [
    (0x303A, 0x1001),  # Espressif native USB (ESP32-C3 / S2 / S3)
    (0x303A, 0x0002),  # Espressif ESP32-S2
    (0x10C4, 0xEA60),  # CP2102 (Silicon Labs) — common on ESP32 devkits
    (0x1A86, 0x7523),  # CH340
    (0x1A86, 0x55D4),  # CH9102
]

def find_esp32_port():
    """Scan serial ports and return the first one that looks like an ESP32.

    Matching order:
      1. Exact VID/PID from the known list above
      2. Description contains 'CP210', 'CH340', 'CH9102', or 'ESP32'
    Returns the port name (e.g. 'COM4') or None if nothing found.
    """
    ports = list(serial.tools.list_ports.comports())

    # Pass 1 — VID/PID
    for port in ports:
        if port.vid is not None and port.pid is not None:
            if (port.vid, port.pid) in _ESP32_VIDPID:
                app_log.info(f"[ESP32] found by VID/PID: {port.device} — {port.description}")
                return port.device

    # Pass 2 — description string
    _DESC_KEYWORDS = ("CP210", "CH340", "CH9102", "ESP32", "USB Serial")
    for port in ports:
        desc = (port.description or "").upper()
        if any(kw.upper() in desc for kw in _DESC_KEYWORDS):
            app_log.info(f"[ESP32] found by description: {port.device} — {port.description}")
            return port.device

    # Pass 3 — Linux fallback: first ttyUSB* or ttyACM* device
    if sys.platform.startswith("linux"):
        candidates = sorted(glob.glob("/dev/ttyUSB*") + glob.glob("/dev/ttyACM*"))
        if candidates:
            app_log.info(f"[ESP32] found by device path: {candidates[0]}")
            return candidates[0]

    return None


class Esp32SerialReader(threading.Thread):
    def __init__(self, store):
        super().__init__(daemon=True)
        self.store = store
        self._stop = threading.Event()

    def _resolve_port(self):
        if config.ESP32_PORT != "auto":
            return config.ESP32_PORT
        port = find_esp32_port()
        if port is None:
            app_log.warning("[ESP32] no port found — retrying in 3 s")
        return port

    def run(self):
        while not self._stop.is_set():
            port = self._resolve_port()
            if port is None:
                self._stop.wait(timeout=3)
                continue
            try:
                with serial.Serial(port, config.ESP32_BAUD, timeout=2) as ser:
                    app_log.info(f"[ESP32] opened {port} at {config.ESP32_BAUD} baud")
                    self.store.set("esp32_port", port)
                    while not self._stop.is_set():
                        raw = ser.readline()
                        if not raw:
                            continue
                        try:
                            msg = json.loads(raw.decode("utf-8", errors="ignore").strip())
                        except json.JSONDecodeError as e:
                            app_log.error(f"[ESP32] JSON decode error: {e} — raw: {raw!r}")
                            continue

                        if "status" in msg:
                            self.store.set("connected", msg["status"] in ("connected", "simulating"))
                            continue

                        for esp_key, store_key in _KEY_MAP.items():
                            if esp_key in msg:
                                self.store.set(store_key, msg[esp_key])
            except serial.SerialException as e:
                if "Permission denied" in str(e) or "Errno 13" in str(e):
                    app_log.error(
                        f"[ESP32] permissão negada em {port}. "
                        f"Execute: sudo usermod -a -G dialout $USER  (depois reinicie a sessão)"
                    )
                    self._stop.wait(timeout=10)
                else:
                    app_log.error(f"[ESP32] serial error on {port}: {e}")
                    self._stop.wait(timeout=3)
                self.store.set("connected", False)
                self.store.set("esp32_port", "")

    def stop(self):
        self._stop.set()
