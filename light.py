"""
light.py — локальный свет ночью.
Рисуем затемняющий слой, вырезая в нём круги вокруг игрока и костров.
"""
import pygame

SCALE = 0.25  # отрисовка маски в уменьшенном размере → быстро


def make_light_mask(screen_w, screen_h, darkness_color, alpha, light_sources):
    """
    light_sources: список (cx, cy, radius, intensity), где intensity 0..1.
    Возвращает поверхность размера экрана для наложения.
    """
    small_w = max(1, int(screen_w * SCALE))
    small_h = max(1, int(screen_h * SCALE))
    small = pygame.Surface((small_w, small_h), pygame.SRCALPHA)
    r, g, b = darkness_color
    small.fill((r, g, b, alpha))

    if light_sources:
        for (cx, cy, radius, intensity) in light_sources:
            sx = int(cx * SCALE)
            sy = int(cy * SCALE)
            rad = max(1, int(radius * SCALE))
            if sx < -rad or sy < -rad or sx > small_w + rad or sy > small_h + rad:
                continue
            steps = 4
            for i in range(steps, 0, -1):
                frac = i / steps
                r_i = int(rad * frac)
                a_cut = int(alpha * intensity * (1 - frac) * 1.5)
                if r_i <= 0 or a_cut <= 0:
                    continue
                s = pygame.Surface((r_i * 2, r_i * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (0, 0, 0, min(255, a_cut)), (r_i, r_i), r_i)
                small.blit(s, (sx - r_i, sy - r_i),
                           special_flags=pygame.BLEND_RGBA_SUB)

    return pygame.transform.smoothscale(small, (screen_w, screen_h))