import pygame
import config
from dashboard.widgets.temp_gauge       import TempGauge
from dashboard.widgets.volt_gauge       import VoltGauge
from dashboard.widgets.console_battery  import ConsoleBatteryWidget
from dashboard.alarm                    import AlarmManager

_DIVIDER_Y = 310   # split between temperature gauges and battery section

# Rects for each sensor zone — used for alarm border drawing
def _sensor_rects(W):
    half   = W // 2
    volt_h = config.SCREEN_HEIGHT - _DIVIDER_Y - 10
    return {
        "oil_temp":   pygame.Rect(0,    0,               half, _DIVIDER_Y),
        "water_temp": pygame.Rect(half, 0,               half, _DIVIDER_Y),
        "voltage":    pygame.Rect(0,    _DIVIDER_Y + 10, half, volt_h),
    }


class AppExtras:
    """Dashboard focused on oil temp, coolant temp, and battery voltage."""

    def __init__(self, store):
        pygame.init()
        flags = pygame.FULLSCREEN if config.FULLSCREEN else 0
        self.screen  = pygame.display.set_mode(
            (config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Car HUD — Extra")
        self.clock   = pygame.time.Clock()
        self.store   = store
        self.running = True
        self.alarm   = AlarmManager()

        self._font_status = pygame.font.SysFont("monospace", 11)

        W      = config.SCREEN_WIDTH
        half   = W // 2
        volt_h = config.SCREEN_HEIGHT - _DIVIDER_Y - 10

        self.widgets = [
            TempGauge(self.screen, pygame.Rect(0,    0,               half, _DIVIDER_Y),
                      "OLEO",          "oil_temp"),
            TempGauge(self.screen, pygame.Rect(half, 0,               half, _DIVIDER_Y),
                      "ARREFECIMENTO", "water_temp"),
            VoltGauge(self.screen,       pygame.Rect(0,    _DIVIDER_Y + 10, half, volt_h)),
            ConsoleBatteryWidget(self.screen, pygame.Rect(half, _DIVIDER_Y + 10, half, volt_h)),
        ]

    # ── Chrome ───────────────────────────────────────────────────────────────

    def _draw_chrome(self, connected: bool, port: str = ""):
        W = config.SCREEN_WIDTH
        pygame.draw.line(self.screen, config.COLORS["divider"],
                         (20, _DIVIDER_Y), (W - 20, _DIVIDER_Y), 1)
        pygame.draw.line(self.screen, config.COLORS["divider"],
                         (W // 2, 20), (W // 2, _DIVIDER_Y - 20), 1)
        pygame.draw.line(self.screen, config.COLORS["divider"],
                         (W // 2, _DIVIDER_Y + 20), (W // 2, config.SCREEN_HEIGHT - 10), 1)
        dot_color = config.COLORS["primary"] if connected else config.COLORS["danger"]
        dot_label = "OBD" if connected else "—"
        lbl = self._font_status.render(dot_label, True, dot_color)
        pygame.draw.circle(self.screen, dot_color, (W - 8, 8), 4)
        self.screen.blit(lbl, (W - lbl.get_width() - 16, 2))
        if port:
            port_short = port.replace("/dev/", "")
            port_lbl = self._font_status.render(port_short, True, config.COLORS["muted"])
            self.screen.blit(port_lbl, (W - port_lbl.get_width() - 4, 14))

    def _draw_alarm_borders(self):
        """Draw blinking colored borders on top of widgets in alarm state."""
        alarm = self.alarm
        if not alarm.blink_on:
            return

        W = config.SCREEN_WIDTH
        rects = _sensor_rects(W)

        for key, rect in rects.items():
            lvl = alarm.level(key)
            if lvl == 0:
                continue
            color = config.COLORS["danger"] if lvl == 2 else config.COLORS["warning"]
            pygame.draw.rect(self.screen, color, rect, 2)

        # Full-screen border when any sensor is in danger
        if alarm.overall() == 2:
            pygame.draw.rect(self.screen, config.COLORS["danger"],
                             pygame.Rect(0, 0, W, config.SCREEN_HEIGHT), 2)

    # ── Main loop ────────────────────────────────────────────────────────────

    def run(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self.running = False

                data = self.store.snapshot()
                self.alarm.update(data)

                self.screen.fill(config.COLORS["bg"])

                for widget in self.widgets:
                    widget.update(data)
                    widget.draw()

                self._draw_chrome(data.get("connected", False), data.get("esp32_port", ""))
                self._draw_alarm_borders()   # drawn last so borders sit on top
                pygame.display.flip()
                self.clock.tick(config.FPS)
        finally:
            pygame.quit()
