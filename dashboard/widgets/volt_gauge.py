import pygame
import config
from dashboard.widgets.base import Widget

_V_MIN    = 10.0
_V_MAX    = 16.0
_V_LOW    = 11.5   # below: dead / very low
_V_CHARGE = 12.5   # below: engine off, running on battery
_V_HIGH   = 14.8   # above: overcharging

_ZONES = [
    (_V_MIN,    _V_LOW,    "danger"),
    (_V_LOW,    _V_CHARGE, "warning"),
    (_V_CHARGE, _V_HIGH,   "primary"),
    (_V_HIGH,   _V_MAX,    "warning"),
]


def _status(v: float):
    if v < _V_LOW:
        return "BATERIA CRITICA", "danger"
    if v < _V_CHARGE:
        return "MOTOR DESLIGADO", "warning"
    if v > _V_HIGH:
        return "SOBRECARGA", "danger"
    return "NORMAL", "primary"


class VoltGauge(Widget):
    """Horizontal bar gauge for battery voltage."""

    def __init__(self, surface, rect):
        super().__init__(surface, rect)
        self.voltage = 0.0
        self._font_val    = pygame.font.SysFont("monospace", 52, bold=True)
        self._font_unit   = pygame.font.SysFont("monospace", 20)
        self._font_status = pygame.font.SysFont("monospace", 13, bold=True)
        self._font_tick   = pygame.font.SysFont("monospace", 10)
        self._font_label  = pygame.font.SysFont("monospace", 12)

    def update(self, data: dict):
        self.voltage = data.get("voltage", 0.0)

    def _color_for(self, v: float):
        if v < _V_LOW or v > _V_HIGH:
            return config.COLORS["danger"]
        if v < _V_CHARGE:
            return config.COLORS["warning"]
        return config.COLORS["primary"]

    def draw(self):
        pygame.draw.rect(self.surface, config.COLORS["panel"], self.rect)

        cx = self.rect.centerx
        bar_margin = 70
        bar_x = self.rect.x + bar_margin
        bar_w = self.rect.width - bar_margin * 2
        bar_h = 16

        # Section label
        hdr = self._font_label.render("BATERIA", True, config.COLORS["muted"])
        self.surface.blit(hdr, hdr.get_rect(centerx=cx, top=self.rect.y + 8))

        # Voltage value
        val_str   = f"{self.voltage:.1f}" if self.voltage > 0 else "--.-"
        text_col  = config.COLORS["text"] if self.voltage > 0 else config.COLORS["muted"]
        val_surf  = self._font_val.render(val_str, True, text_col)
        unit_surf = self._font_unit.render("V", True, config.COLORS["muted"])

        vy = self.rect.y + 26
        vx = cx - (val_surf.get_width() + unit_surf.get_width() + 4) // 2
        self.surface.blit(val_surf, (vx, vy))
        self.surface.blit(unit_surf, (vx + val_surf.get_width() + 4,
                                      vy + val_surf.get_height() - unit_surf.get_height() - 2))

        # Horizontal bar
        bar_y = vy + val_surf.get_height() + 10

        pygame.draw.rect(self.surface, config.COLORS["arc_bg"],
                         pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=3)

        # Zone tints
        for z0, z1, ck in _ZONES:
            zx = bar_x + int((z0 - _V_MIN) / (_V_MAX - _V_MIN) * bar_w)
            zw = int((z1 - z0)            / (_V_MAX - _V_MIN) * bar_w)
            tint = tuple(max(0, c // 5) for c in config.COLORS[ck])
            pygame.draw.rect(self.surface, tint, pygame.Rect(zx, bar_y, zw, bar_h))

        # Fill
        if self.voltage > 0:
            frac   = max(0.0, min(1.0, (self.voltage - _V_MIN) / (_V_MAX - _V_MIN)))
            fill_w = int(frac * bar_w)
            if fill_w > 0:
                pygame.draw.rect(self.surface, self._color_for(self.voltage),
                                 pygame.Rect(bar_x, bar_y, fill_w, bar_h), border_radius=3)

        pygame.draw.rect(self.surface, config.COLORS["divider"],
                         pygame.Rect(bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

        # Zone boundary lines
        for v_thresh in (_V_LOW, _V_CHARGE, _V_HIGH):
            tx = bar_x + int((v_thresh - _V_MIN) / (_V_MAX - _V_MIN) * bar_w)
            pygame.draw.line(self.surface, config.COLORS["divider"],
                             (tx, bar_y), (tx, bar_y + bar_h), 1)

        # Scale ticks and labels
        for v_tick in range(int(_V_MIN), int(_V_MAX) + 1):
            tx  = bar_x + int((v_tick - _V_MIN) / (_V_MAX - _V_MIN) * bar_w)
            pygame.draw.line(self.surface, config.COLORS["divider"],
                             (tx, bar_y + bar_h - 4), (tx, bar_y + bar_h), 1)
            lbl = self._font_tick.render(str(v_tick), True, config.COLORS["muted"])
            self.surface.blit(lbl, lbl.get_rect(centerx=tx, top=bar_y + bar_h + 3))

        # Status text
        if self.voltage > 0:
            st_str, st_ck = _status(self.voltage)
            st_surf = self._font_status.render(st_str, True, config.COLORS[st_ck])
            self.surface.blit(st_surf, st_surf.get_rect(
                centerx=cx, top=bar_y + bar_h + 22))
