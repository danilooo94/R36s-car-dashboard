import pygame
import math
import config
from dashboard.widgets.base import Widget

_ARC_START = 225    # degrees, screen-space (east = 0, CCW positive)
_ARC_SPAN  = 270    # degrees of sweep
_STEPS     = 120    # line segments used to approximate the arc

_T_WARNING = 95
_T_DANGER  = 105


class TempGauge(Widget):
    """Semi-circular arc gauge for a single temperature sensor."""

    def __init__(self, surface, rect, label: str, key: str):
        super().__init__(surface, rect)
        self.label = label
        self.key   = key
        self.value = 0.0

        self._r  = min(rect.width // 2 - 25, (rect.height - 55) // 2)
        self._cx = rect.centerx
        self._cy = rect.y + self._r + 50

        self._font_val   = pygame.font.SysFont("monospace", 54, bold=True)
        self._font_unit  = pygame.font.SysFont("monospace", 17)
        self._font_label = pygame.font.SysFont("monospace", 14, bold=True)
        self._font_tick  = pygame.font.SysFont("monospace", 9)

    def update(self, data: dict):
        self.value = data.get(self.key, 0.0)

    def _arc_pt(self, frac: float):
        a = math.radians(_ARC_START - _ARC_SPAN * frac)
        return (self._cx + self._r * math.cos(a),
                self._cy - self._r * math.sin(a))

    def _color_for(self, t: float):
        if t >= _T_DANGER:
            return config.COLORS["danger"]
        if t >= _T_WARNING:
            return config.COLORS["warning"]
        return config.COLORS["primary"]

    def draw(self):
        pygame.draw.rect(self.surface, config.COLORS["panel"], self.rect)

        # Background arc
        bg = [self._arc_pt(i / _STEPS) for i in range(_STEPS + 1)]
        pygame.draw.lines(self.surface, config.COLORS["arc_bg"], False, bg, 7)

        # Filled arc
        if self.value > 0:
            frac = max(0.0, min(1.0,
                       (self.value - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)))
            n = max(0, int(_STEPS * frac))
            if n > 1:
                pts = [self._arc_pt(i / _STEPS) for i in range(n + 1)]
                pygame.draw.lines(self.surface, self._color_for(self.value), False, pts, 4)

        # Danger threshold marker on the arc
        df = (_T_DANGER - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)
        da = math.radians(_ARC_START - _ARC_SPAN * df)
        ca, sa = math.cos(da), math.sin(da)
        pygame.draw.line(self.surface, config.COLORS["danger"],
                         (int(self._cx + (self._r - 9) * ca), int(self._cy - (self._r - 9) * sa)),
                         (int(self._cx + (self._r + 9) * ca), int(self._cy - (self._r + 9) * sa)), 2)

        # Tick marks and scale labels
        for t in range(config.TEMP_MIN, config.TEMP_MAX + 1, 10):
            f     = (t - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)
            angle = math.radians(_ARC_START - _ARC_SPAN * f)
            ca, sa = math.cos(angle), math.sin(angle)
            major  = (t % 20 == 0)
            inner  = self._r - (9 if major else 4)
            pygame.draw.line(self.surface, config.COLORS["divider"],
                             (int(self._cx + inner * ca),       int(self._cy - inner * sa)),
                             (int(self._cx + (self._r + 3) * ca), int(self._cy - (self._r + 3) * sa)), 1)
            if major:
                lr = self._r + 14
                lbl = self._font_tick.render(str(t), True, config.COLORS["muted"])
                self.surface.blit(lbl, lbl.get_rect(
                    center=(int(self._cx + lr * ca), int(self._cy - lr * sa))))

        # Value text
        if self.value > 0:
            color   = self._color_for(self.value) if self.value >= _T_WARNING else config.COLORS["text"]
            val_str = f"{int(self.value)}"
        else:
            color   = config.COLORS["muted"]
            val_str = "--"

        val_surf  = self._font_val.render(val_str, True, color)
        unit_surf = self._font_unit.render("°C", True, config.COLORS["muted"])
        val_rect  = val_surf.get_rect(centerx=self._cx, centery=self._cy - 15)
        self.surface.blit(val_surf, val_rect)
        self.surface.blit(unit_surf, (val_rect.right + 2, val_rect.top + 6))

        # Label centered near bottom of rect
        lbl_surf = self._font_label.render(self.label, True, config.COLORS["muted"])
        self.surface.blit(lbl_surf, lbl_surf.get_rect(
            centerx=self._cx, bottom=self.rect.bottom - 28))
