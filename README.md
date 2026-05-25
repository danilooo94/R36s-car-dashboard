# R36S Car Dashboard

A pygame-based OBD-II dashboard designed to run on the **R36S** handheld Linux console (640×480). Reads engine data from an ELM327 OBD adapter via an ESP32 bridge (Bluetooth LE → USB serial) and displays it in real time.

---

## Features

- Engine coolant temperature gauge
- Engine oil temperature gauge
- Battery voltage gauge with alarm
- Device (R36S console) battery indicator
- Audio alarm for high temperature / low voltage
- CSV data logging (configurable interval)
- Error logging to timestamped text file
- Simulation / mock mode for development without hardware

---

## Architecture

```
Car OBD port
    │
    ▼
ELM327 OBD adapter (Bluetooth LE)
    │
    ▼
ESP32-C3 (Esp32ELMReader firmware) ──── BLE ────► reads PIDs
    │
    ▼  USB serial (115200 baud)
R36S / PC
    │
    ▼
obd/esp32_reader.py  (background thread)
    │
    ▼
obd/store.py  (thread-safe DataStore)
    │
    ├──► dashboard/app_extras.py  (pygame render loop, 60 FPS)
    └──► obd/logger.py            (CSV logger, every 1 s)
```

---

## Project Structure

```
CarDataReader/
├── main.py                   # Original entry point (TCP OBD)
├── main_extras.py            # Entry point for ESP32 serial mode
├── config.py                 # All settings (ports, colors, flags)
├── app_log.py                # Error logger (logs/errors_*.txt)
├── run_r36s.sh               # Launch script for R36S hardware
│
├── obd/
│   ├── store.py              # Thread-safe data store
│   ├── esp32_reader.py       # Reads JSON from ESP32 over USB serial
│   ├── reader.py             # TCP OBD reader (original mode)
│   ├── mock.py               # Simulated data for PC testing
│   └── logger.py             # CSV data logger
│
└── dashboard/
    ├── app.py                # Original pygame app (TCP mode)
    ├── app_extras.py         # Pygame app for ESP32 mode
    ├── alarm.py              # Beep alarm manager
    └── widgets/
        ├── temp_gauge.py     # Temperature arc gauge
        ├── volt_gauge.py     # Battery voltage gauge
        ├── console_battery.py# R36S device battery indicator
        ├── temp_graph.py     # Temperature history graph
        ├── speed.py          # Speed arc
        ├── rpm_bar.py        # RPM bar
        └── base.py           # Base widget class
```

---

## Hardware Requirements

| Component | Details |
|-----------|---------|
| Target device | R36S handheld console (ARM Linux) |
| OBD adapter | ELM327-compatible with Bluetooth LE (e.g. OBDLink CX, OBDII dongle) |
| Bridge MCU | ESP32-C3 running [Esp32ELMReader](../Esp32ELMReader) firmware |
| Connection | ESP32 → R36S via USB cable |

---

## Software Requirements

- Python 3.9+
- pygame
- pyserial
- pyaudio *(for alarm beeps)*

Install on the R36S (or any Linux):

```bash
pip install pygame pyserial pyaudio
```

---

## Configuration

All settings live in [config.py](config.py):

| Setting | Default | Description |
|---------|---------|-------------|
| `MOCK_MODE` | `True` | `True` = simulated data, no hardware needed |
| `ESP32_PORT` | `"auto"` | Auto-detect serial port, or set e.g. `"COM3"` / `"/dev/ttyUSB0"` |
| `ESP32_BAUD` | `115200` | Serial baud rate |
| `FULLSCREEN` | `False` | `True` on R36S (set via env var in `run_r36s.sh`) |
| `FPS` | `60` | Render frame rate |
| `LOG_ENABLED` | `True` | Enable CSV data logging |
| `LOG_INTERVAL` | `1.0` | Seconds between CSV rows |
| `ALARM_SOUND` | `True` | Enable audio alarms |
| `RPM_REDLINE` | `5500` | RPM redline threshold |
| `TEMP_MAX` | `120` | Max temperature before danger color |

Environment variable overrides (used by `run_r36s.sh`):

| Variable | Effect |
|----------|--------|
| `CARDATAREADER_FULLSCREEN=1` | Forces fullscreen mode |
| `CARDATAREADER_MOCK=0` | Disables mock mode |

---

## Running

### PC — development / simulation

```bash
python main_extras.py
```

Mock mode is on by default (`MOCK_MODE = True` in `config.py`), so no hardware is needed.

### R36S — real hardware

1. Copy the project to the R36S.
2. Connect the ESP32 via USB and make sure it is paired with the OBD adapter.
3. Add your user to the `dialout` group (one-time setup):

   ```bash
   sudo usermod -a -G dialout $USER
   # log out and back in for this to take effect
   ```

4. Run:

   ```bash
   ./run_r36s.sh
   ```

   This sets `SDL_VIDEODRIVER=kmsdrm` (KMS/DRM framebuffer, no X11 required) and disables mock mode automatically.

---

## ESP32 Firmware

The companion firmware lives in `Esp32ELMReader/` (PlatformIO project for ESP32-C3). It:

- Connects to the OBD adapter over Bluetooth LE
- Queries PIDs: coolant temp, oil temp, intake temp, fuel level, battery voltage
- Sends readings as JSON lines over USB serial at 115200 baud

Example output:
```json
{"coolant_temp": 87.0, "oil_temp": 92.5, "intake_temp": 29.0, "fuel_pct": 68.0, "battery_v": 13.8}
```

To build and flash, open `Esp32ELMReader/` in VS Code with the PlatformIO extension and click **Upload**.

---

## Logs

| Path | Content |
|------|---------|
| `logs/data_YYYY-MM-DD_HH-MM-SS.csv` | Sensor readings at 1 s intervals |
| `logs/errors_YYYY-MM-DD_HH-MM-SS.txt` | Application errors and warnings |

---

## Controls

| Input | Action |
|-------|--------|
| `A` button (R36S) / `A` key (PC) | Exit the application |

---

## Dashboard Layout

```
┌─────────────────────┬─────────────────────┐
│                     │                     │
│   OIL TEMP gauge    │  COOLANT TEMP gauge │
│                     │                     │
├──────────┬──────────┴──────────┬──────────┤
│          │                     │          │
│ CAR      │      divider        │  DEVICE  │
│ BATTERY  │                     │  BATTERY │
│ (VoltGauge)                    │  (R36S)  │
└──────────┴─────────────────────┴──────────┘
                  640 × 480 px
```
