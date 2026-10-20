"""camera.py — камера, следующая за игроком. Размер мира задаётся извне."""
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TILE_SIZE


class Camera:
    def __init__(self, width=SCREEN_WIDTH, height=SCREEN_HEIGHT):
        self.width = width
        self.height = height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.smooth = 0.15
        # Размеры мира в пикселях (по умолчанию — как 200x200 тайлов)
        self.world_w = 200 * TILE_SIZE
        self.world_h = 200 * TILE_SIZE

    def set_world_size(self, map_w_tiles, map_h_tiles):
        """Вызывается из Game при смене локации/мира."""
        self.world_w = map_w_tiles * TILE_SIZE
        self.world_h = map_h_tiles * TILE_SIZE

    def follow(self, world_x, world_y):
        self.target_x = world_x - self.width / 2
        self.target_y = world_y - self.height / 2

    def update(self):
        self.x += (self.target_x - self.x) * self.smooth
        self.y += (self.target_y - self.y) * self.smooth
        max_x = self.world_w - self.width
        max_y = self.world_h - self.height
        if self.x < 0: self.x = 0
        if self.y < 0: self.y = 0
        if self.x > max_x: self.x = max_x
        if self.y > max_y: self.y = max_y

    def apply(self, pos):
        return int(pos[0] - self.x), int(pos[1] - self.y)

    def apply_rect(self, rect):
        return pygame.Rect(rect.x - self.x, rect.y - self.y, rect.w, rect.h)

    @property
    def offset(self):
        return self.x, self.y