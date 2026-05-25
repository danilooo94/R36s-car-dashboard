import pygame
import math
import config
from dashboard.widgets.base import Widget

_START = 210   # arc start (degrees, screen-space)
_SPAN  = 240   # arc sweep
_STEPS = 100   # segments

class SpeedDisplay(Widget):
    def __init__(self, surface, rect):
        super().__init__(surface, rect)
        self.speed = 0
        self.rpm   = 0
        self._cx     = rect.centerx
        self._cy     = rect.centery - 5
        self._radius = 135
        self._font_speed = pygame.font.SysFont("monospace", 110, bold=True)
        self._font_label = pygame.font.SysFont("monospace", 20)

    def update(self, data):
        self.speed = data.get("speed", 0)
        self.rpm   = data.get("rpm", 0)

    def _arc_point(self, frac):
        a = math.radians(_START - _SPAN * frac)
        return (self._cx + self._radius * math.cos(a),
                self._cy - self._radius * math.sin(a))

    def _draw_arc(self):
        progress  = min(self.rpm / config.RPM_MAX, 1.0)
        rl_frac   = config.RPM_REDLINE / config.RPM_MAX

        # Background ring (faint)
        bg_pts = [self._arc_point(i / _STEPS) for i in range(_STEPS + 1)]
        if len(bg_pts) > 1:
            pygame.draw.lines(self.surface, config.COLORS["arc_bg"], False, bg_pts, 6)

        # Filled arc — simulated glow: draw wide + dim first, then sharp
        fill_n = max(0, int(_STEPS * progress))
        if fill_n > 1:
            normal_n = int(_STEPS * rl_frac)

            def draw_segment(pts, color, wide_color):
                if len(pts) < 2:
                    return
                pygame.draw.lines(self.surface, wide_color, False, pts, 9)
                pygame.draw.lines(self.surface, color,      False, pts, 3)

            all_pts = [self._arc_point(i / _STEPS) for i in range(fill_n + 1)]

            if fill_n <= normal_n:
                dim = tuple(max(0, c // 3) for c in config.COLORS["primary"])
                draw_segment(all_pts, config.COLORS["primary"], dim)
            else:
                n_pts = all_pts[: normal_n + 1]
                d_pts = all_pts[normal_n :]
                dim_p = tuple(max(0, c // 3) for c in config.COLORS["primary"])
                dim_d = tuple(max(0, c // 3) for c in config.COLORS["danger"])
                draw_segment(n_pts, config.COLORS["primary"], dim_p)
                draw_segment(d_pts, config.COLORS["danger"],  dim_d)

        # Tick marks at every 1000 RPM
        for tick in range(0, config.RPM_MAX + 1, 1000):
            frac  = tick / config.RPM_MAX
            angle = math.radians(_START - _SPAN * frac)
            cos_a, sin_a = math.cos(angle), math.sin(angle)
            r = self._radius
            x1 = self._cx + (r - 11) * cos_a
            y1 = self._cy - (r - 11) * sin_a
            x2 = self._cx + (r +  7) * cos_a
            y2 = self._cy - (r +  7) * sin_a
            pygame.draw.line(self.surface, config.COLORS["divider"], (x1, y1), (x2, y2), 2)

    def draw(self):
        self._draw_arc()

        # Speed number with glow
        spd_surf = self._font_speed.render(f"{int(self.speed)}", True, config.COLORS["text"])
        sx = self._cx - spd_surf.get_width()  // 2
        sy = self._cy - spd_surf.get_height() // 2 - 5
        self.surface.blit(spd_surf, (sx, sy))

        # "km/h" unit
        unit_surf = self._font_label.render("km/h", True, config.COLORS["muted"])
        self.surface.blit(unit_surf, unit_surf.get_rect(
            centerx=self._cx, top=sy + spd_surf.get_height() - 12))

        # RPM value
        rpm_surf = self._font_label.render(f"{int(self.rpm):,} rpm", True, config.COLORS["muted"])
        self.surface.blit(rpm_surf, rpm_surf.get_rect(
            centerx=self._cx, top=sy + spd_surf.get_height() + 12))
