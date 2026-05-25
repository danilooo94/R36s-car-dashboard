import pygame
import config
from dashboard.widgets.base import Widget

_VOLT_MIN = 11.5   # 0 % de carga
_VOLT_MAX = 14.8   # 100 % de carga
_SEGMENTS = 4


class BatteryWidget(Widget):
    def __init__(self, surface, rect):
        super().__init__(surface, rect)
        self.voltage = 0.0
        self._font_big   = pygame.font.SysFont("monospace", 42, bold=True)
        self._font_small = pygame.font.SysFont("monospace", 13)

    def update(self, data):
        self.voltage = data.get("voltage", 0.0)

    def _color(self):
        if self.voltage < 12.0:
            return config.COLORS["danger"]
        if self.voltage < 12.5:
            return config.COLORS["warning"]
        return config.COLORS["primary"]

    def _draw_battery_icon(self, cx, y, color):
        bw, bh = 64, 20
        x = cx - bw // 2

        fill = max(0.0, min(1.0, (self.voltage - _VOLT_MIN) / (_VOLT_MAX - _VOLT_MIN)))

        # Preenchimento
        fill_w = int((bw - 6) * fill)
        if fill_w > 0:
            pygame.draw.rect(self.surface, color,
                             pygame.Rect(x + 3, y + 3, fill_w, bh - 6))

        # Divisórias dos segmentos
        seg_inner = bw - 6
        for i in range(1, _SEGMENTS):
            sx = x + 3 + int(seg_inner * i / _SEGMENTS)
            pygame.draw.line(self.surface, config.COLORS["panel"],
                             (sx, y + 1), (sx, y + bh - 1), 2)

        # Contorno do corpo
        pygame.draw.rect(self.surface, color,
                         pygame.Rect(x, y, bw, bh), 2)

        # Terminal positivo (nub)
        pygame.draw.rect(self.surface, color,
                         pygame.Rect(x + bw, y + bh // 2 - 4, 5, 8))

    def draw(self):
        pygame.draw.rect(self.surface, config.COLORS["panel"], self.rect)
        color = self._color()
        cx    = self.rect.centerx

        # Label
        lbl = self._font_small.render("BATERIA", True, config.COLORS["muted"])
        self.surface.blit(lbl, lbl.get_rect(centerx=cx, top=self.rect.top + 6))

        # Ícone de bateria
        self._draw_battery_icon(cx, self.rect.top + 26, color)

        # Tensão
        val = self._font_big.render(f"{self.voltage:.1f}V", True, color)
        self.surface.blit(val, val.get_rect(centerx=cx, top=self.rect.top + 54))
