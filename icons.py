"""
icons.py — процедурная отрисовка иконок предметов (вместо цветных квадратов).
Каждая иконка рисуется в прямоугольник rect.
"""
import math
import pygame


def _center(rect):
    return rect.centerx, rect.centery


# ---------- Иконки ----------
def draw_icon_wood(screen, rect):
    cx, cy = _center(rect)
    # бревно
    pygame.draw.rect(screen, (110, 70, 40),
                     (cx - 14, cy - 6, 28, 12), border_radius=3)
    pygame.draw.rect(screen, (150, 100, 55),
                     (cx - 14, cy - 6, 28, 4), border_radius=3)
    # торцы
    pygame.draw.circle(screen, (180, 130, 80), (cx - 14, cy), 6)
    pygame.draw.circle(screen, (140, 95, 55), (cx - 14, cy), 6, 1)
    pygame.draw.circle(screen, (180, 130, 80), (cx + 14, cy), 6)
    pygame.draw.circle(screen, (140, 95, 55), (cx + 14, cy), 6, 1)
    # годовые кольца
    pygame.draw.circle(screen, (120, 80, 45), (cx - 14, cy), 3, 1)
    pygame.draw.circle(screen, (120, 80, 45), (cx + 14, cy), 3, 1)


def draw_icon_stone(screen, rect):
    cx, cy = _center(rect)
    pygame.draw.polygon(screen, (130, 130, 135), [
        (cx - 12, cy + 8), (cx - 14, cy - 2), (cx - 4, cy - 10),
        (cx + 8, cy - 8), (cx + 14, cy + 2), (cx + 10, cy + 8),
    ])
    pygame.draw.polygon(screen, (100, 100, 105), [
        (cx - 12, cy + 8), (cx - 14, cy - 2), (cx - 4, cy - 10), (cx - 4, cy + 8),
    ])
    pygame.draw.circle(screen, (170, 170, 175), (cx + 2, cy - 2), 2)


def draw_icon_berry(screen, rect):
    cx, cy = _center(rect)
    # веточка
    pygame.draw.line(screen, (70, 110, 50), (cx, cy - 12), (cx, cy - 2), 2)
    pygame.draw.ellipse(screen, (70, 140, 60), (cx - 10, cy - 14, 8, 5))
    pygame.draw.ellipse(screen, (70, 140, 60), (cx + 2, cy - 14, 8, 5))
    # ягоды
    for dx, dy, r in [(-6, 2, 5), (2, -2, 5), (6, 6, 4), (-4, 8, 4)]:
        pygame.draw.circle(screen, (200, 40, 80), (cx + dx, cy + dy), r)
        pygame.draw.circle(screen, (255, 130, 150), (cx + dx - 1, cy + dy - 1), 1)


def draw_icon_iron(screen, rect):
    cx, cy = _center(rect)
    # руда: камни + блёстки
    pygame.draw.polygon(screen, (100, 100, 110), [
        (cx - 12, cy + 8), (cx - 14, cy - 2), (cx - 4, cy - 10),
        (cx + 8, cy - 8), (cx + 14, cy + 2), (cx + 10, cy + 8),
    ])
    # прожилки металла
    for dx, dy in [(-6, 0), (0, -4), (4, 2), (8, -2), (-2, 6)]:
        pygame.draw.circle(screen, (200, 200, 220), (cx + dx, cy + dy), 2)
        pygame.draw.circle(screen, (255, 255, 255), (cx + dx - 1, cy + dy - 1), 1)


def draw_icon_fish(screen, rect):
    cx, cy = _center(rect)
    # тело рыбы
    pygame.draw.ellipse(screen, (140, 190, 220), (cx - 14, cy - 5, 24, 10))
    # хвост
    pygame.draw.polygon(screen, (110, 160, 195), [
        (cx + 10, cy), (cx + 16, cy - 6), (cx + 16, cy + 6),
    ])
    # плавник
    pygame.draw.polygon(screen, (110, 160, 195), [
        (cx - 4, cy - 5), (cx + 2, cy - 10), (cx + 6, cy - 4),
    ])
    # глаз
    pygame.draw.circle(screen, (30, 30, 30), (cx - 8, cy - 1), 2)
    pygame.draw.circle(screen, (250, 250, 250), (cx - 9, cy - 2), 1)
    # чешуя
    for i in range(3):
        pygame.draw.arc(screen, (100, 150, 185),
                        (cx - 6 + i * 4, cy - 3, 6, 6), 0, 3.14, 1)


def draw_icon_raw_meat(screen, rect):
    cx, cy = _center(rect)
    # кусок мяса
    pygame.draw.ellipse(screen, (200, 90, 90), (cx - 12, cy - 6, 24, 14))
    pygame.draw.ellipse(screen, (170, 60, 60), (cx - 12, cy - 6, 24, 14), 1)
    # жир
    pygame.draw.ellipse(screen, (240, 200, 180), (cx - 6, cy - 3, 8, 5))
    # косточка
    pygame.draw.rect(screen, (230, 220, 200), (cx + 8, cy - 2, 8, 3), border_radius=1)
    pygame.draw.circle(screen, (230, 220, 200), (cx + 15, cy - 1), 2)


def draw_icon_cooked_meat(screen, rect):
    cx, cy = _center(rect)
    pygame.draw.ellipse(screen, (150, 80, 40), (cx - 12, cy - 6, 24, 14))
    pygame.draw.ellipse(screen, (110, 60, 30), (cx - 12, cy - 6, 24, 14), 1)
    # поджаренные полоски
    for dx in (-6, 0, 6):
        pygame.draw.line(screen, (70, 40, 20), (cx + dx, cy - 4), (cx + dx, cy + 4), 1)
    # косточка
    pygame.draw.rect(screen, (240, 230, 210), (cx + 8, cy - 2, 8, 3), border_radius=1)
    pygame.draw.circle(screen, (240, 230, 210), (cx + 15, cy - 1), 2)


def draw_icon_leather(screen, rect):
    cx, cy = _center(rect)
    pygame.draw.polygon(screen, (140, 95, 55), [
        (cx - 14, cy - 8), (cx + 12, cy - 10),
        (cx + 14, cy + 4), (cx + 8, cy + 10),
        (cx - 10, cy + 8), (cx - 14, cy + 2),
    ])
    pygame.draw.polygon(screen, (110, 70, 40), [
        (cx - 14, cy - 8), (cx + 12, cy - 10),
        (cx + 14, cy + 4), (cx + 8, cy + 10),
        (cx - 10, cy + 8), (cx - 14, cy + 2),
    ], 1)
    # складки
    pygame.draw.line(screen, (90, 55, 30), (cx - 6, cy - 6), (cx - 4, cy + 6), 1)
    pygame.draw.line(screen, (90, 55, 30), (cx + 4, cy - 6), (cx + 6, cy + 6), 1)


def draw_icon_water_flask(screen, rect):
    cx, cy = _center(rect)
    # фляга
    pygame.draw.rect(screen, (90, 90, 100),
                     (cx - 8, cy - 10, 16, 20), border_radius=4)
    # жидкость
    pygame.draw.rect(screen, (70, 140, 220),
                     (cx - 6, cy - 4, 12, 12), border_radius=2)
    # горлышко
    pygame.draw.rect(screen, (60, 60, 70), (cx - 3, cy - 14, 6, 6), border_radius=2)
    # крышка
    pygame.draw.rect(screen, (150, 120, 60), (cx - 4, cy - 16, 8, 3), border_radius=1)
    # блик
    pygame.draw.line(screen, (200, 200, 220), (cx - 5, cy - 6), (cx - 5, cy + 4), 1)


def draw_icon_axe(screen, rect):
    cx, cy = _center(rect)
    # топорище
    pygame.draw.line(screen, (110, 70, 40), (cx - 10, cy + 10), (cx + 8, cy - 8), 4)
    pygame.draw.line(screen, (80, 50, 25), (cx - 10, cy + 10), (cx + 8, cy - 8), 1)
    # лезвие
    pygame.draw.polygon(screen, (160, 160, 170), [
        (cx + 4, cy - 14), (cx + 14, cy - 12),
        (cx + 12, cy + 2), (cx + 2, cy - 2),
    ])
    pygame.draw.polygon(screen, (100, 100, 110), [
        (cx + 4, cy - 14), (cx + 14, cy - 12),
        (cx + 12, cy + 2), (cx + 2, cy - 2),
    ], 1)
    pygame.draw.line(screen, (220, 220, 230), (cx + 6, cy - 12), (cx + 12, cy - 10), 1)


def draw_icon_pickaxe(screen, rect):
    cx, cy = _center(rect)
    # ручка
    pygame.draw.line(screen, (110, 70, 40), (cx - 10, cy + 10), (cx + 6, cy - 6), 4)
    # кирка
    pygame.draw.arc(screen, (160, 160, 170), (cx - 4, cy - 18, 22, 20), 3.3, 6.1, 4)
    pygame.draw.arc(screen, (100, 100, 110), (cx - 4, cy - 18, 22, 20), 3.3, 6.1, 1)


def draw_icon_sword(screen, rect):
    cx, cy = _center(rect)
    # лезвие
    pygame.draw.polygon(screen, (200, 200, 220), [
        (cx - 10, cy + 10), (cx + 8, cy - 12), (cx + 12, cy - 12),
        (cx + 12, cy - 8), (cx - 6, cy + 14),
    ])
    pygame.draw.polygon(screen, (150, 150, 170), [
        (cx - 10, cy + 10), (cx + 8, cy - 12), (cx + 12, cy - 12),
        (cx + 12, cy - 8), (cx - 6, cy + 14),
    ], 1)
    # гарда
    pygame.draw.line(screen, (170, 120, 50), (cx - 10, cy + 2), (cx - 2, cy + 10), 3)
    # рукоять
    pygame.draw.line(screen, (100, 70, 40), (cx - 12, cy + 12), (cx - 6, cy + 16), 3)
    # блик
    pygame.draw.line(screen, (255, 255, 255), (cx - 4, cy - 4), (cx + 6, cy - 10), 1)


def draw_icon_rod(screen, rect):
    cx, cy = _center(rect)
    # удилище
    pygame.draw.line(screen, (140, 90, 50), (cx - 12, cy + 10), (cx + 10, cy - 12), 2)
    # леска
    pygame.draw.line(screen, (200, 200, 200), (cx + 10, cy - 12), (cx + 12, cy + 8), 1)
    # поплавок
    pygame.draw.circle(screen, (220, 60, 60), (cx + 12, cy + 8), 2)
    # крючок
    pygame.draw.arc(screen, (180, 180, 190), (cx + 10, cy + 8, 6, 6), 0, 3.14, 1)


def draw_icon_torch(screen, rect):
    cx, cy = _center(rect)
    # рукоять
    pygame.draw.rect(screen, (110, 70, 40), (cx - 2, cy - 2, 4, 14))
    pygame.draw.line(screen, (80, 50, 25), (cx, cy), (cx, cy + 12), 1)
    # пламя
    t = pygame.time.get_ticks() / 100.0
    pygame.draw.polygon(screen, (230, 100, 40), [
        (cx - 6, cy - 4), (cx, cy - 16 + math.sin(t) * 2), (cx + 6, cy - 4),
    ])
    pygame.draw.polygon(screen, (250, 200, 60), [
        (cx - 3, cy - 4), (cx, cy - 12 + math.sin(t) * 2), (cx + 3, cy - 4),
    ])


def draw_icon_wall(screen, rect):
    cx, cy = _center(rect)
    # кирпичи
    for row in range(3):
        for col in range(2):
            bx = cx - 12 + col * 12 + (row % 2) * 6
            by = cy - 10 + row * 7
            pygame.draw.rect(screen, (150, 110, 70), (bx, by, 10, 6))
            pygame.draw.rect(screen, (100, 70, 40), (bx, by, 10, 6), 1)


def draw_icon_door(screen, rect):
    cx, cy = _center(rect)
    pygame.draw.rect(screen, (150, 100, 60), (cx - 10, cy - 14, 20, 28), border_radius=2)
    pygame.draw.rect(screen, (100, 70, 40), (cx - 10, cy - 14, 20, 28), 1, border_radius=2)
    # доски
    for dx in (-5, 0, 5):
        pygame.draw.line(screen, (110, 75, 45),
                         (cx + dx, cy - 13), (cx + dx, cy + 13), 1)
    # ручка
    pygame.draw.circle(screen, (230, 200, 60), (cx + 5, cy), 2)


def draw_icon_bed(screen, rect):
    cx, cy = _center(rect)
    # одеяло
    pygame.draw.rect(screen, (200, 80, 80), (cx - 14, cy - 4, 28, 14), border_radius=3)
    pygame.draw.rect(screen, (170, 60, 60), (cx - 14, cy - 4, 28, 14), 1, border_radius=3)
    # подушка
    pygame.draw.rect(screen, (240, 240, 240), (cx - 12, cy - 8, 10, 6), border_radius=2)
    pygame.draw.rect(screen, (200, 200, 210), (cx - 12, cy - 8, 10, 6), 1, border_radius=2)
    # изголовье
    pygame.draw.rect(screen, (140, 90, 50), (cx - 14, cy - 10, 28, 3), border_radius=1)


def draw_icon_campfire(screen, rect):
    cx, cy = _center(rect)
    # дрова
    pygame.draw.line(screen, (100, 60, 30), (cx - 12, cy + 8), (cx + 12, cy + 8), 3)
    pygame.draw.line(screen, (80, 50, 25), (cx - 10, cy + 6), (cx + 10, cy + 10), 2)
    # пламя
    t = pygame.time.get_ticks() / 100.0
    pygame.draw.polygon(screen, (230, 100, 40), [
        (cx - 8, cy + 6), (cx, cy - 16 + math.sin(t) * 3), (cx + 8, cy + 6),
    ])
    pygame.draw.polygon(screen, (250, 200, 60), [
        (cx - 5, cy + 6), (cx, cy - 10 + math.sin(t + 1) * 2), (cx + 5, cy + 6),
    ])
    pygame.draw.polygon(screen, (255, 240, 150), [
        (cx - 2, cy + 4), (cx, cy - 4 + math.sin(t + 2) * 1), (cx + 2, cy + 4),
    ])


def draw_icon_roof(screen, rect):
    cx, cy = _center(rect)
    pygame.draw.polygon(screen, (100, 70, 40), [
        (cx - 14, cy + 8), (cx, cy - 12), (cx + 14, cy + 8),
    ])
    pygame.draw.polygon(screen, (100, 70, 40), [
        (cx - 14, cy + 8), (cx, cy - 12), (cx + 14, cy + 8),
    ], 1)
    # «черепица»
    for i in range(3):
        y = cy - 4 + i * 5
        pygame.draw.line(screen, (60, 40, 20), (cx - 10 + i * 2, y), (cx + 10 - i * 2, y), 1)


def draw_icon_feather(screen, rect):
    cx, cy = _center(rect)
    # перо
    pygame.draw.ellipse(screen, (230, 230, 240), (cx - 6, cy - 14, 12, 24))
    pygame.draw.line(screen, (150, 150, 160), (cx, cy - 12), (cx, cy + 10), 1)
    for i in range(5):
        y = cy - 10 + i * 4
        pygame.draw.line(screen, (180, 180, 190), (cx, y), (cx + 4, y + 2), 1)
        pygame.draw.line(screen, (180, 180, 190), (cx, y), (cx - 4, y + 2), 1)


def draw_icon_wool(screen, rect):
    cx, cy = _center(rect)
    for dx, dy, r in [(-6, -6, 6), (0, -8, 7), (6, -6, 6), (-8, 0, 6),
                      (0, 0, 7), (8, 0, 6), (-6, 6, 6), (0, 8, 6), (6, 6, 6)]:
        pygame.draw.circle(screen, (240, 235, 220), (cx + dx, cy + dy), r)
    for dx, dy, r in [(-4, -4, 4), (2, -2, 4), (-2, 4, 4)]:
        pygame.draw.circle(screen, (200, 195, 180), (cx + dx, cy + dy), r)


def draw_icon_egg(screen, rect):
    cx, cy = _center(rect)
    pygame.draw.ellipse(screen, (250, 245, 230), (cx - 8, cy - 12, 16, 22))
    pygame.draw.ellipse(screen, (210, 200, 180), (cx - 8, cy - 12, 16, 22), 1)
    pygame.draw.ellipse(screen, (255, 255, 250), (cx - 4, cy - 8, 4, 6))


def draw_icon_milk(screen, rect):
    cx, cy = _center(rect)
    # кувшин
    pygame.draw.rect(screen, (230, 230, 240),
                     (cx - 8, cy - 8, 16, 18), border_radius=2)
    pygame.draw.rect(screen, (180, 180, 190),
                     (cx - 8, cy - 8, 16, 18), 1, border_radius=2)
    # молоко
    pygame.draw.rect(screen, (250, 250, 250),
                     (cx - 7, cy + 2, 14, 8), border_radius=1)
    # горлышко
    pygame.draw.rect(screen, (230, 230, 240), (cx - 4, cy - 12, 8, 5))
    pygame.draw.rect(screen, (180, 180, 190), (cx - 4, cy - 12, 8, 5), 1)


ICON_FUNCS = {
    "wood": draw_icon_wood,
    "stone": draw_icon_stone,
    "berry": draw_icon_berry,
    "iron_ore": draw_icon_iron,
    "fish": draw_icon_fish,
    "raw_meat": draw_icon_raw_meat,
    "cooked_meat": draw_icon_cooked_meat,
    "leather": draw_icon_leather,
    "water_flask": draw_icon_water_flask,
    "axe": draw_icon_axe,
    "pickaxe": draw_icon_pickaxe,
    "sword": draw_icon_sword,
    "rod": draw_icon_rod,
    "torch": draw_icon_torch,
    "wall": draw_icon_wall,
    "door": draw_icon_door,
    "bed": draw_icon_bed,
    "campfire": draw_icon_campfire,
    "roof": draw_icon_roof,
    "feather": draw_icon_feather,
    "wool": draw_icon_wool,
    "egg": draw_icon_egg,
    "milk": draw_icon_milk,
}


def draw_item_icon(screen, item_id, rect):
    """
    Главная функция: рисует иконку предмета в заданном прямоугольнике.
    Если для предмета нет функции — рисует цветной квадрат-заглушку.
    """
    rect = pygame.Rect(rect)
    fn = ICON_FUNCS.get(item_id)
    if fn:
        fn(screen, rect)
    else:
        from settings import ITEMS
        color = ITEMS[item_id][1] if item_id in ITEMS else (150, 150, 150)
        pygame.draw.rect(screen, color, rect, border_radius=4)
        pygame.draw.rect(screen, (30, 30, 30), rect, 1, border_radius=4)