import math
import struct
import time
import pygame
import config

# ── Thresholds (must mirror widget color logic) ─────────────────────────────
_TEMP_WARN   = 95
_TEMP_DANGER = 105
_V_WARN_LOW  = 12.5
_V_WARN_HIGH = 14.4
_V_DANG_LOW  = 11.5
_V_DANG_HIGH = 14.8

# ── Blink rates (half-cycle in frames at config.FPS) ────────────────────────
_BLINK_WARN   = 30   # 1 Hz  (on 30f / off 30f)
_BLINK_DANGER = 15   # 2 Hz  (on 15f / off 15f)

# ── Sound cooldowns ──────────────────────────────────────────────────────────
_COOLDOWN_WARN   = 4.0   # seconds between warning beeps
_COOLDOWN_DANGER = 1.0   # seconds between danger beeps


def _make_beep(freq: int, duration_ms: int, sample_rate: int, volume: float = 0.55):
    """Generate a sine-wave beep as a pygame.mixer.Sound (no external libs)."""
    n   = int(sample_rate * duration_ms / 1000)
    buf = bytearray(n * 4)          # 2 channels × 2 bytes (int16)
    for i in range(n):
        # Fade out the last 20% to avoid clicks
        env = 1.0 - max(0.0, (i / n - 0.8) / 0.2)
        val = int(math.sin(2 * math.pi * freq * i / sample_rate) * volume * env * 32767)
        val = max(-32768, min(32767, val))
        struct.pack_into('<hh', buf, i * 4, val, val)
    return pygame.mixer.Sound(buffer=bytes(buf))


class AlarmManager:
    """
    Tracks per-sensor alarm levels, drives blink animation, and plays beeps.

    Call update(data) once per frame.  Query level(key) and blink_on to
    know what to draw.
    """

    def __init__(self):
        if not pygame.mixer.get_init():
            pygame.mixer.init(44100, -16, 2, 512)
        sample_rate = pygame.mixer.get_init()[0] or 44100

        self._sounds = {
            1: _make_beep(880, 120, sample_rate),   # warning : short high beep
            2: _make_beep(420, 300, sample_rate),   # danger  : low sustained beep
        }

        self._levels       = {}   # key → 0/1/2
        self._last_sound   = 0.0
        self._blink_tick   = 0
        self._blink_on     = False

    # ── Internal level evaluators ────────────────────────────────────────────

    @staticmethod
    def _eval_temp(v: float) -> int:
        if v >= _TEMP_DANGER: return 2
        if v >= _TEMP_WARN:   return 1
        return 0

    @staticmethod
    def _eval_voltage(v: float) -> int:
        if v <= 0:                            return 0
        if v < _V_DANG_LOW or v > _V_DANG_HIGH: return 2
        if v < _V_WARN_LOW or v > _V_WARN_HIGH: return 1
        return 0

    # ── Public API ───────────────────────────────────────────────────────────

    def update(self, data: dict):
        """Must be called once per frame with the current sensor snapshot."""
        oil   = data.get("oil_temp",   0.0)
        water = data.get("water_temp", 0.0)
        volt  = data.get("voltage",    0.0)

        self._levels = {
            "oil_temp":   self._eval_temp(oil)      if oil   > 0 else 0,
            "water_temp": self._eval_temp(water)    if water > 0 else 0,
            "voltage":    self._eval_voltage(volt),
        }

        top = self.overall()

        # ── Sound ────────────────────────────────────────────────────────────
        if top > 0 and config.ALARM_SOUND:
            cooldown = _COOLDOWN_DANGER if top == 2 else _COOLDOWN_WARN
            now = time.monotonic()
            if now - self._last_sound >= cooldown:
                self._sounds[top].play()
                self._last_sound = now

        # ── Blink ────────────────────────────────────────────────────────────
        half = _BLINK_DANGER if top == 2 else _BLINK_WARN
        self._blink_tick = (self._blink_tick + 1) % (half * 2)
        self._blink_on   = (top > 0) and (self._blink_tick < half)

    def level(self, key: str) -> int:
        """Alarm level for a specific sensor: 0 = ok, 1 = warning, 2 = danger."""
        return self._levels.get(key, 0)

    def overall(self) -> int:
        """Highest alarm level across all sensors."""
        return max(self._levels.values(), default=0)

    @property
    def blink_on(self) -> bool:
        """True during the visible phase of the blink animation."""
        return self._blink_on
