import pygame
import config
from dashboard.widgets.base import Widget

class RPMBar(Widget):
    def __init__(self, surface, rect):
        super().__init__(surface, rect)
        self.rpm = 0

    def update(self, data):
        self.rpm = data.get("rpm", 0)

    def draw(self):
        bar_w = int((min(self.rpm, config.RPM_MAX) / config.RPM_MAX) * self.rect.width)
        color = config.COLORS["primary"] if self.rpm < config.RPM_REDLINE else config.COLORS["danger"]
        pygame.draw.rect(self.surface, color, (self.rect.x, self.rect.y, bar_w, self.rect.height))
