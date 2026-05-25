import pygame
from collections import deque
import config
from dashboard.widgets.base import Widget

_SCALE_TEMPS = [40, 80, 120]
_LABEL_W     = 30


def _draw_dashed_hline(surface, color, x, y, w, dash=5, gap=4):
    for i in range(0, w, dash + gap):
        pygame.draw.line(surface, color, (x + i, y), (x + min(i + dash, w), y), 1)


class TempGraph(Widget):
    def __init__(self, surface, rect):
        super().__init__(surface, rect)
        self.history   = deque([0.0] * config.TEMP_HISTORY, maxlen=config.TEMP_HISTORY)
        self.oil_temp  = 0.0
        self.water_temp = 0.0
        self._font        = pygame.font.SysFont("monospace", 20, bold=True)
        self._font_sec    = pygame.font.SysFont("monospace", 16, bold=True)
        self._font_small  = pygame.font.SysFont("monospace", 12)
        self._font_scale  = pygame.font.SysFont("monospace", 10)
        self._gx = rect.x + _LABEL_W
        self._gw = rect.width - _LABEL_W

    def update(self, data):
        self.oil_temp   = data.get("oil_temp",   0)
        self.water_temp = data.get("water_temp", 0)
        primary = self.oil_temp if self.oil_temp > 0 else self.water_temp
        self.history.append(primary)

    def _temp_to_y(self, t):
        norm = (t - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)
        return self.rect.bottom - int(max(0.0, min(1.0, norm)) * self.rect.height)

    def _color_for(self, temp):
        return config.COLORS["danger"] if temp > 105 else config.COLORS["primary"]

    def _draw_thermometer(self, x, y, fill_frac, color):
        stem_h, stem_w, bulb_r = 18, 6, 5
        cx = x + bulb_r
        stem_rect = pygame.Rect(cx - stem_w // 2, y, stem_w, stem_h)
        pygame.draw.rect(self.surface, config.COLORS["arc_bg"], stem_rect, border_radius=2)
        fill_h = int(stem_h * fill_frac)
        if fill_h > 0:
            pygame.draw.rect(self.surface, color,
                             pygame.Rect(cx - stem_w // 2 + 1, y + stem_h - fill_h,
                                         stem_w - 2, fill_h))
        pygame.draw.rect(self.surface, color, stem_rect, 1, border_radius=2)
        by = y + stem_h + bulb_r
        pygame.draw.circle(self.surface, config.COLORS["arc_bg"], (cx, by), bulb_r)
        pygame.draw.circle(self.surface, color, (cx, by), bulb_r - 1)
        pygame.draw.circle(self.surface, color, (cx, by), bulb_r, 1)

    def draw(self):
        pygame.draw.rect(self.surface, config.COLORS["panel"], self.rect)

        # ── Eixo Y ──
        for t in _SCALE_TEMPS:
            py = self._temp_to_y(t)
            lbl = self._font_scale.render(str(t), True, config.COLORS["muted"])
            self.surface.blit(lbl, (self.rect.x, py - lbl.get_height() // 2))
            _draw_dashed_hline(self.surface, config.COLORS["divider"], self._gx, py, self._gw)
        pygame.draw.line(self.surface, config.COLORS["divider"],
                         (self._gx, self.rect.y), (self._gx, self.rect.bottom), 1)

        # ── Gráfico ──
        n = len(self.history)
        pts = [(self._gx + int(i * self._gw / max(n - 1, 1)), self._temp_to_y(v))
               for i, v in enumerate(self.history)]
        primary = self.oil_temp if self.oil_temp > 0 else self.water_temp
        if len(pts) > 1:
            pygame.draw.lines(self.surface, self._color_for(primary), False, pts, 2)

        # ── Cabeçalho ──
        hx = self.rect.x
        hy = self.rect.y - 30

        # Temperatura principal (óleo, se disponível; senão arrefecimento)
        if self.oil_temp > 0:
            frac = max(0.0, min(1.0, (self.oil_temp - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)))
            self._draw_thermometer(hx, hy, frac, self._color_for(self.oil_temp))
            oil_surf = self._font.render(f"{int(self.oil_temp)}°C", True, config.COLORS["text"])
            self.surface.blit(oil_surf, (hx + 14, hy))
            lbl1 = self._font_small.render("OIL", True, config.COLORS["muted"])
            self.surface.blit(lbl1, (hx + 14 + oil_surf.get_width() + 4, hy + 5))
            cursor_x = hx + 14 + oil_surf.get_width() + 4 + lbl1.get_width() + 10
        else:
            cursor_x = hx

        # Temperatura de arrefecimento (sempre exibida)
        if self.water_temp > 0:
            w_color = self._color_for(self.water_temp)
            w_surf  = self._font_sec.render(f"{int(self.water_temp)}°C", True,
                                            config.COLORS["text"] if self.oil_temp > 0 else config.COLORS["text"])
            if self.oil_temp == 0:
                frac = max(0.0, min(1.0, (self.water_temp - config.TEMP_MIN) / (config.TEMP_MAX - config.TEMP_MIN)))
                self._draw_thermometer(hx, hy, frac, w_color)
                self.surface.blit(w_surf, (hx + 14, hy + 2))
                lbl2 = self._font_small.render("WATER", True, config.COLORS["muted"])
                self.surface.blit(lbl2, (hx + 14 + w_surf.get_width() + 4, hy + 6))
            else:
                # Exibe como valor secundário ao lado
                self.surface.blit(w_surf, (cursor_x, hy + 2))
                lbl2 = self._font_small.render("WATER", True, config.COLORS["muted"])
                self.surface.blit(lbl2, (cursor_x + w_surf.get_width() + 4, hy + 6))
