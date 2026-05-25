import pygame
import config
from dashboard.widgets.base import Widget

_CAP_PATH    = "/sys/class/power_supply/battery/capacity"
_STATUS_PATH = "/sys/class/power_supply/battery/status"


def _read_battery():
    """Return (percent, plugged) or (None, None) if unavailable."""
    try:
        with open(_CAP_PATH) as f:
            pct = int(f.read().strip())
        try:
            with open(_STATUS_PATH) as f:
                status = f.read().strip()
            plugged = status in ("Charging", "Full")
        except OSError:
            plugged = None
        return pct, plugged
    except OSError:
        return None, None


class ConsoleBatteryWidget(Widget):
    """Shows the R36S / host device battery level."""

    def __init__(self, surface, rect):
        super().__init__(surface, rect)
        self._pct    = None
        self._plugged = None
        self._font_val    = pygame.font.SysFont("monospace", 52, bold=True)
        self._font_unit   = pygame.font.SysFont("monospace", 20)
        self._font_label  = pygame.font.SysFont("monospace", 12)
        self._font_status = pygame.font.SysFont("monospace", 13, bold=True)
        self._font_tick   = pygame.font.SysFont("monospace", 10)

    def update(self, data: dict):
        self._pct, self._plugged = _read_battery()

    def _color(self):
        if self._pct is None:
            return config.COLORS["muted"]
        if self._pct < 15:
            return config.COLORS["danger"]
        if self._pct < 30:
            return config.COLORS["warning"]
        return config.COLORS["primary"]

    def draw(self):
        pygame.draw.rect(self.surface, config.COLORS["panel"], self.rect)

        cx        = self.rect.centerx
        bar_margin = 70
        bar_x     = self.rect.x + bar_margin
        bar_w     = self.rect.width - bar_margin * 2
        bar_h     = 16
        color     = self._color()

        # Section label
        hdr = self._font_label.render("CONSOLE", True, config.COLORS["muted"])
        self.surface.blit(hdr, hdr.get_rect(centerx=cx, top=self.rect.y + 8))

        # Percentage value
        if self._pct is not None:
            val_str  = f"{self._pct:.0f}"
            txt_col  = config.COLORS["text"]
        else:
            val_str  = "--"
            txt_col  = config.COLORS["muted"]

        val_surf  = self._font_val.render(val_str, True, txt_col)
        unit_surf = self._font_unit.render("%", True, config.COLORS["muted"])

        vy = self.rect.y + 26
        vx = cx - (val_surf.get_width() + unit_surf.get_width() + 4) // 2
        self.surface.blit(val_surf, (vx, vy))
        self.surface.blit(unit_surf, (vx + val_surf.get_width() + 4,
                                      vy + val_surf.get_height() - unit_surf.get_height() - 2))

        # Horizontal bar
        bar_y = vy + val_surf.get_height() + 10

        pygame.draw.rect(self.surface, config.COLORS["arc_bg"],
                         pygame.Rect(bar_x, bar_y, bar_w, bar_h), border_radius=3)

        if self._pct is not None:
            frac   = max(0.0, min(1.0, self._pct / 100.0))
            fill_w = int(frac * bar_w)
            if fill_w > 0:
                pygame.draw.rect(self.surface, color,
                                 pygame.Rect(bar_x, bar_y, fill_w, bar_h), border_radius=3)

        pygame.draw.rect(self.surface, config.COLORS["divider"],
                         pygame.Rect(bar_x, bar_y, bar_w, bar_h), 1, border_radius=3)

        # Tick marks at 25 / 50 / 75 %
        for pct_tick in (0, 25, 50, 75, 100):
            tx  = bar_x + int(pct_tick / 100 * bar_w)
            pygame.draw.line(self.surface, config.COLORS["divider"],
                             (tx, bar_y + bar_h - 4), (tx, bar_y + bar_h), 1)
            lbl = self._font_tick.render(str(pct_tick), True, config.COLORS["muted"])
            self.surface.blit(lbl, lbl.get_rect(centerx=tx, top=bar_y + bar_h + 3))

        # Status text
        if self._pct is not None:
            if self._plugged:
                st_str, st_ck = "CARREGANDO", "primary"
            elif self._pct < 15:
                st_str, st_ck = "BATERIA CRITICA", "danger"
            elif self._pct < 30:
                st_str, st_ck = "BATERIA BAIXA", "warning"
            else:
                st_str, st_ck = "NORMAL", "primary"
            st_surf = self._font_status.render(st_str, True, config.COLORS[st_ck])
            self.surface.blit(st_surf, st_surf.get_rect(
                centerx=cx, top=bar_y + bar_h + 22))
