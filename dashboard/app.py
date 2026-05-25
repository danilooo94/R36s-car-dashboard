import pygame
import config
from dashboard.widgets.speed      import SpeedDisplay
from dashboard.widgets.temp_graph import TempGraph
from dashboard.widgets.battery    import BatteryWidget

_SEP_Y = 340   # y position of the divider line

class App:
    def __init__(self, store):
        pygame.init()
        flags = pygame.FULLSCREEN if config.FULLSCREEN else 0
        self.screen  = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT), flags)
        pygame.display.set_caption("Car HUD")
        self.clock   = pygame.time.Clock()
        self.store   = store
        self.running = True

        self._font_status = pygame.font.SysFont("monospace", 11)

        W = config.SCREEN_WIDTH
        self.widgets = [
            SpeedDisplay( self.screen, pygame.Rect(0,   0,   W,        _SEP_Y)),
            TempGraph(    self.screen, pygame.Rect(20,  370, 275,      100)),
            BatteryWidget(self.screen, pygame.Rect(345, 365, W - 365,  110)),
        ]

    def _draw_chrome(self, connected):
        W = config.SCREEN_WIDTH
        # Separator line
        pygame.draw.line(self.screen, config.COLORS["divider"], (20, _SEP_Y), (W - 20, _SEP_Y), 1)

        # OBD status dot
        dot_color = config.COLORS["primary"] if connected else config.COLORS["danger"]
        dot_label = "OBD" if connected else "—"
        lbl = self._font_status.render(dot_label, True, dot_color)
        pygame.draw.circle(self.screen, dot_color, (W - 8, 8), 4)
        self.screen.blit(lbl, (W - lbl.get_width() - 16, 2))

    def run(self):
        try:
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.KEYDOWN:
                        self.running = False

                data = self.store.snapshot()
                self.screen.fill(config.COLORS["bg"])

                for widget in self.widgets:
                    widget.update(data)
                    widget.draw()

                self._draw_chrome(data.get("connected", False))
                pygame.display.flip()
                self.clock.tick(config.FPS)
        finally:
            pygame.quit()
