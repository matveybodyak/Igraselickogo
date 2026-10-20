"""building.py — режим строительства: стены, двери, палатка, сундук, грядка."""
import pygame
from settings import (
    TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, GREEN, RED,
    DARK_GRAY, ITEMS, get_font,
)


class BuildManager:
    BUILDABLES = ["wall", "door", "campfire", "bed", "roof", "tent", "chest", "farm_plot"]

    def __init__(self):
        self.active = False
        self.selected = 0
        self.hover_cell = None
        self.font = get_font(18)
        self.font_small = get_font(14)

    def toggle(self): self.active = not self.active
    def select_next(self, d=1):
        self.selected = (self.selected + d) % len(self.BUILDABLES)
    def selected_item(self): return self.BUILDABLES[self.selected]

    def handle_event(self, event, player, world, camera):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_b, pygame.K_ESCAPE):
                self.active = False
                return True
            if event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4,
                             pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8):
                idx = event.key - pygame.K_1
                if idx < len(self.BUILDABLES):
                    self.selected = idx
                return True
            if event.key == pygame.K_RIGHT:
                self.select_next(1); return True
            if event.key == pygame.K_LEFT:
                self.select_next(-1); return True
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._try_place(player, world, camera)
                return True
            if event.button == 3:
                self.active = False; return True
            if event.button == 4:
                self.select_next(-1); return True
            if event.button == 5:
                self.select_next(1); return True
        if event.type == pygame.MOUSEMOTION:
            cam_x, cam_y = camera.offset
            wx, wy = event.pos[0] + cam_x, event.pos[1] + cam_y
            self.hover_cell = (int(wx // TILE_SIZE), int(wy // TILE_SIZE))
        return False

    def _try_place(self, player, world, camera):
        if not self.hover_cell:
            return
        gx, gy = self.hover_cell
        item = self.selected_item()
        if player.inventory.count_item(item) <= 0:
            return
        if not world.can_place(gx, gy, item):
            return
        if world.place_building(gx, gy, item):
            player.inventory.remove_item(item, 1)

    def draw(self, screen, player, world, camera):
        if not self.active:
            return
        if self.hover_cell:
            gx, gy = self.hover_cell
            cam_x, cam_y = camera.offset
            sx, sy = gx * TILE_SIZE - cam_x, gy * TILE_SIZE - cam_y
            item = self.selected_item()
            ok = world.can_place(gx, gy, item) and player.inventory.count_item(item) > 0
            color = GREEN if ok else RED
            s = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            s.fill((*color, 90))
            screen.blit(s, (sx, sy))
            pygame.draw.rect(screen, color, (sx, sy, TILE_SIZE, TILE_SIZE), 2)

        slot_w = 60
        gap = 6
        count = len(self.BUILDABLES)
        total = count * (slot_w + gap) - gap
        panel_w = total + 20
        panel_h = 80
        px = (SCREEN_WIDTH - panel_w) // 2
        py = SCREEN_HEIGHT - panel_h - 10
        surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 160))
        screen.blit(surf, (px, py))
        pygame.draw.rect(screen, WHITE, (px, py, panel_w, panel_h), 2, border_radius=8)
        start_x = px + 10
        for i, item in enumerate(self.BUILDABLES):
            ix = start_x + i * (slot_w + gap)
            iy = py + 10
            rect = pygame.Rect(ix, iy, slot_w, slot_w)
            sel = (i == self.selected)
            pygame.draw.rect(screen, (90, 120, 70) if sel else DARK_GRAY, rect, border_radius=6)
            pygame.draw.rect(screen, WHITE if sel else (120, 120, 120), rect, 2, border_radius=6)
            pygame.draw.rect(screen, ITEMS[item][1], rect.inflate(-16, -16), border_radius=4)
            num = self.font_small.render(str(i + 1), True, WHITE)
            screen.blit(num, (rect.x + 4, rect.y + 2))
            cnt = player.inventory.count_item(item)
            cnt_s = self.font.render(str(cnt), True, WHITE if cnt > 0 else RED)
            screen.blit(cnt_s, (rect.x + slot_w - 16, rect.y + slot_w - 20))
        hint = self.font_small.render(
            "B/Esc/ПКМ — выйти · 1..8 или колесо — выбор · ЛКМ — разместить",
            True, (220, 220, 230))
        screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, py - 14)))