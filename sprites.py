"""sprites.py — анимированная отрисовка животных (дыхание, моргание, уши, хвост)."""
import math
import pygame


def _shadow(screen, cx, cy, w, h=6):
    s = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 70), (0, 0, w, h))
    screen.blit(s, (cx - w // 2, cy - h // 2))


def _eye(screen, x, y, r=2):
    pygame.draw.circle(screen, (250, 250, 250), (int(x), int(y)), r + 1)
    pygame.draw.circle(screen, (20, 20, 20), (int(x), int(y)), r)


def _blink_eye(screen, x, y, r=2):
    pygame.draw.line(screen, (80, 50, 40), (x - r, y), (x + r, y), 2)


def _bob(phase, amp=2.0):
    return math.sin(phase) * amp


def _leg_swing(phase, side=0):
    return math.sin(phase + side * math.pi) * 3


def _breath(t):
    return (math.sin(t * 2) + 1) / 2


def draw_cow(screen, cx, cy, phase=0.0, moving=False, facing=1):
    w, h = 44, 26
    t = pygame.time.get_ticks() / 1000.0
    bob = _bob(phase, 1.5) if moving else math.sin(t * 2) * 0.8
    _shadow(screen, cx, cy, w + 10, 8)
    swing = _leg_swing(phase) if moving else 0

    for i, dx in enumerate((-14, -4, 4, 14)):
        lx = cx + dx + (swing if i % 2 == 0 else -swing) * 0.5
        pygame.draw.rect(screen, (60, 50, 45), (lx - 2, cy - 10, 4, 10))
        pygame.draw.rect(screen, (20, 20, 20), (lx - 3, cy - 1, 6, 3))

    body = pygame.Rect(cx - w // 2, int(cy - h - 10 + bob), w, h)
    pygame.draw.ellipse(screen, (245, 240, 235), body)
    pygame.draw.ellipse(screen, (200, 195, 190), body, 1)

    pygame.draw.ellipse(screen, (50, 45, 40), (body.x + 6, body.y + 4, 12, 9))
    pygame.draw.ellipse(screen, (50, 45, 40), (body.right - 16, body.y + 10, 10, 8))
    pygame.draw.ellipse(screen, (50, 45, 40), (body.centerx - 2, body.y + 2, 8, 6))

    tx = cx - facing * (w // 2 - 2)
    tail_sway = math.sin(t * 3 + cx * 0.1) * 3
    pygame.draw.line(screen, (200, 195, 190),
                     (tx, cy - h + bob), (tx - facing * 6 + tail_sway, cy - 4), 2)
    pygame.draw.circle(screen, (50, 45, 40),
                       (int(tx - facing * 6 + tail_sway), cy - 4), 2)

    hx = cx + facing * (w // 2 - 2)
    graze = 4 if not moving and int(t) % 6 < 2 else 0
    hy = cy - h - 2 + bob + graze
    head_r = 10
    pygame.draw.circle(screen, (250, 245, 240), (int(hx), int(hy)), head_r)
    pygame.draw.circle(screen, (200, 195, 190), (int(hx), int(hy)), head_r, 1)

    pygame.draw.line(screen, (220, 210, 180), (hx - 4, hy - head_r + 2), (hx - 7, hy - head_r - 4), 2)
    pygame.draw.line(screen, (220, 210, 180), (hx + 4, hy - head_r + 2), (hx + 7, hy - head_r - 4), 2)

    ear_twitch = math.sin(t * 5) * 1 if int(t * 3) % 4 == 0 else 0
    pygame.draw.ellipse(screen, (240, 220, 210), (hx - 10, hy - 2 - ear_twitch, 6, 4))
    pygame.draw.ellipse(screen, (240, 220, 210), (hx + 4, hy - 2 + ear_twitch, 6, 4))

    blink = (int(t * 2 + cx) % 5 == 0)
    if blink:
        _blink_eye(screen, hx + facing * 3 - 2, hy - 2, 2)
        _blink_eye(screen, hx + facing * 3 + 2, hy - 2, 2)
    else:
        _eye(screen, hx + facing * 3 - 2, hy - 2, 2)
        _eye(screen, hx + facing * 3 + 2, hy - 2, 2)

    pygame.draw.ellipse(screen, (230, 180, 180), (hx + facing * 4 - 4, hy + 3, 8, 5))
    pygame.draw.ellipse(screen, (50, 45, 40), (hx - 6, hy - head_r + 1, 6, 4))


def draw_sheep(screen, cx, cy, phase=0.0, moving=False, facing=1):
    w, h = 34, 22
    t = pygame.time.get_ticks() / 1000.0
    bob = _bob(phase, 1.3) if moving else math.sin(t * 2) * 0.6
    _shadow(screen, cx, cy, w + 8, 7)
    swing = _leg_swing(phase) if moving else 0

    for i, dx in enumerate((-10, -3, 3, 10)):
        lx = cx + dx + (swing if i % 2 == 0 else -swing) * 0.5
        pygame.draw.rect(screen, (60, 55, 50), (lx - 2, cy - 8, 4, 8))
        pygame.draw.rect(screen, (25, 25, 25), (lx - 3, cy - 1, 6, 3))

    breath = _breath(t)
    body_cx, body_cy = cx, int(cy - h - 6 + bob)
    extra = int(breath * 2)
    pygame.draw.ellipse(screen, (245, 245, 240),
                        (cx - w // 2 - extra // 2, body_cy - h // 2 - extra // 2,
                         w + extra, h + extra))
    for dx, dy, r in [(-10, -2, 8), (-3, -6, 9), (5, -6, 8), (11, -1, 8), (-7, 4, 7), (4, 4, 7)]:
        pygame.draw.circle(screen, (250, 250, 245), (body_cx + dx, body_cy + dy), r)
    for dx, dy, r in [(-10, -2, 7), (5, -6, 7), (11, -1, 7)]:
        pygame.draw.circle(screen, (220, 220, 215), (body_cx + dx + 1, body_cy + dy + 1), r - 2)

    graze = 4 if not moving and int(t) % 6 < 2 else 0
    hx = cx + facing * (w // 2 - 1)
    hy = body_cy - 1 + graze
    pygame.draw.circle(screen, (60, 55, 50), (int(hx), int(hy)), 7)
    ear_twitch = math.sin(t * 5) * 1 if int(t * 3) % 4 == 0 else 0
    pygame.draw.ellipse(screen, (60, 55, 50), (hx - 10, hy - 3 - ear_twitch, 6, 4))
    pygame.draw.ellipse(screen, (60, 55, 50), (hx + 4, hy - 3 + ear_twitch, 6, 4))
    blink = (int(t * 2 + cx) % 5 == 0)
    if blink:
        _blink_eye(screen, hx + facing * 2 - 1, hy - 1, 2)
        _blink_eye(screen, hx + facing * 2 + 3, hy - 1, 2)
    else:
        _eye(screen, hx + facing * 2 - 1, hy - 1, 2)
        _eye(screen, hx + facing * 2 + 3, hy - 1, 2)


def draw_chicken(screen, cx, cy, phase=0.0, moving=False, facing=1):
    w, h = 22, 16
    t = pygame.time.get_ticks() / 1000.0
    peck = 3 if int(t) % 3 == 0 else 0
    bob = (_bob(phase, 1.5) if moving else math.sin(t * 3) * 0.5) + peck
    _shadow(screen, cx, cy, w, 5)
    swing = _leg_swing(phase) if moving else 0

    for i, dx in enumerate((-5, 5)):
        lx = cx + dx + (swing if i == 0 else -swing) * 0.5
        pygame.draw.line(screen, (240, 180, 40), (lx, cy - 3), (lx, cy), 2)
        pygame.draw.line(screen, (240, 180, 40), (lx, cy), (lx - 3, cy + 2), 1)
        pygame.draw.line(screen, (240, 180, 40), (lx, cy), (lx + 3, cy + 2), 1)

    body = pygame.Rect(cx - w // 2, int(cy - h - 6 + bob), w, h)
    pygame.draw.ellipse(screen, (250, 245, 235), body)
    pygame.draw.ellipse(screen, (200, 190, 180), body, 1)

    wing_cx = cx - facing * 2
    wing_flap = abs(math.sin(t * 8)) * 2 if moving else 0
    pygame.draw.ellipse(screen, (230, 220, 205),
                        (wing_cx - 6, body.y + 3 - wing_flap, 12, 9))
    pygame.draw.ellipse(screen, (200, 190, 175),
                        (wing_cx - 6, body.y + 3 - wing_flap, 12, 9), 1)

    tx = cx - facing * (w // 2)
    pygame.draw.polygon(screen, (250, 245, 235),
                        [(tx, body.centery + 2), (tx - facing * 6, body.centery - 3),
                         (tx - facing * 5, body.centery + 5)])

    hx = cx + facing * (w // 2 - 2)
    hy = body.y + 2
    pygame.draw.circle(screen, (250, 245, 235), (int(hx), int(hy)), 7)
    pygame.draw.circle(screen, (220, 40, 40), (int(hx - 2), int(hy - 7)), 3)
    pygame.draw.circle(screen, (220, 40, 40), (int(hx + 1), int(hy - 8)), 3)
    pygame.draw.circle(screen, (220, 40, 40), (int(hx + 3), int(hy - 6)), 3)
    beak_x = hx + facing * 6
    pygame.draw.polygon(screen, (240, 170, 40),
                        [(beak_x, hy - 1), (beak_x + facing * 4, hy + 1), (beak_x, hy + 3)])
    blink = (int(t * 3 + cx) % 4 == 0)
    if blink:
        _blink_eye(screen, hx + facing * 2, hy - 1, 1)
    else:
        _eye(screen, hx + facing * 2, hy - 1, 1)
    pygame.draw.circle(screen, (220, 40, 40), (int(hx + facing * 2), int(hy + 6)), 2)


def draw_deer(screen, cx, cy, phase=0.0, moving=False, facing=1):
    w, h = 40, 24
    t = pygame.time.get_ticks() / 1000.0
    bob = _bob(phase, 2.0) if moving else math.sin(t * 2) * 0.8
    _shadow(screen, cx, cy, w + 6, 7)
    swing = _leg_swing(phase) if moving else 0

    for i, dx in enumerate((-12, -4, 4, 12)):
        lx = cx + dx + (swing if i % 2 == 0 else -swing)
        pygame.draw.line(screen, (110, 70, 40), (lx, cy - h + bob), (lx, cy - 2), 3)
        pygame.draw.line(screen, (40, 25, 15), (lx, cy - 2),
                         (lx + (1 if i % 2 == 0 else -1), cy), 3)

    body = pygame.Rect(cx - w // 2, int(cy - h - 10 + bob), w, h)
    pygame.draw.ellipse(screen, (170, 115, 60), body)
    pygame.draw.ellipse(screen, (120, 80, 40), body, 1)

    for dx, dy in [(-10, 2), (-4, 6), (5, 2), (12, 5)]:
        pygame.draw.circle(screen, (235, 220, 200), (body.centerx + dx, body.y + dy), 2)

    graze = 5 if not moving and int(t) % 8 < 3 else 0
    nx = cx + facing * (w // 2 - 4)
    ny = body.y + 2
    pygame.draw.line(screen, (170, 115, 60), (nx, ny), (nx + facing * 6, ny - 12 + graze), 6)

    hx = nx + facing * 6
    hy = ny - 14 + graze
    pygame.draw.ellipse(screen, (170, 115, 60), (hx - 6, hy - 5, 12, 9))
    ear_twitch = math.sin(t * 6) * 1 if int(t * 4) % 3 == 0 else 0
    pygame.draw.ellipse(screen, (140, 95, 50), (hx - 8, hy - 6 - ear_twitch, 5, 4))
    pygame.draw.circle(screen, (40, 30, 20), (int(hx + facing * 5), int(hy + 1)), 2)
    blink = (int(t * 2 + cx) % 5 == 0)
    if blink:
        _blink_eye(screen, hx + facing * 2, hy - 1, 1)
    else:
        _eye(screen, hx + facing * 2, hy - 1, 1)

    for sign in (-1, 1):
        base_x = hx + sign * 3
        base_y = hy - 5
        pygame.draw.line(screen, (140, 100, 60), (base_x, base_y),
                         (base_x + sign * 3, base_y - 6), 2)
        pygame.draw.line(screen, (140, 100, 60), (base_x + sign * 3, base_y - 6),
                         (base_x + sign * 6, base_y - 12), 2)
        pygame.draw.line(screen, (140, 100, 60), (base_x + sign * 3, base_y - 6),
                         (base_x + sign * 1, base_y - 12), 2)


def draw_rabbit(screen, cx, cy, phase=0.0, moving=False, facing=1):
    w, h = 18, 14
    t = pygame.time.get_ticks() / 1000.0
    nose_twitch = math.sin(t * 12) * 1
    ear_twitch = math.sin(t * 4) * 2
    bob = _bob(phase, 1.5) if moving else math.sin(t * 3) * 0.5
    _shadow(screen, cx, cy, w, 4)
    swing = _leg_swing(phase) if moving else 0

    for i, dx in enumerate((-5, 5)):
        lx = cx + dx + (swing if i == 0 else -swing) * 0.5
        pygame.draw.ellipse(screen, (230, 215, 195), (lx - 3, cy - 4, 6, 4))

    body = pygame.Rect(cx - w // 2, int(cy - h - 4 + bob), w, h)
    pygame.draw.ellipse(screen, (230, 215, 195), body)
    pygame.draw.ellipse(screen, (190, 175, 155), body, 1)

    tx = cx - facing * (w // 2 - 1)
    pygame.draw.circle(screen, (250, 250, 245), (int(tx), cy - h + bob), 3)

    hx = cx + facing * (w // 2 - 2)
    hy = body.y + 1
    pygame.draw.circle(screen, (230, 215, 195), (int(hx), int(hy)), 6)
    ex1 = hx - 2 + ear_twitch * 0.5
    ex2 = hx + 2 - ear_twitch * 0.5
    pygame.draw.ellipse(screen, (230, 215, 195), (ex1 - 2, hy - 16, 4, 12))
    pygame.draw.ellipse(screen, (230, 215, 195), (ex2 - 2, hy - 16, 4, 12))
    pygame.draw.ellipse(screen, (240, 180, 180), (ex1 - 1, hy - 14, 2, 8))
    pygame.draw.ellipse(screen, (240, 180, 180), (ex2 - 1, hy - 14, 2, 8))
    blink = (int(t * 3 + cx) % 4 == 0)
    if blink:
        _blink_eye(screen, hx + facing * 1, hy - 1, 1)
        _blink_eye(screen, hx + facing * 3, hy - 1, 1)
    else:
        _eye(screen, hx + facing * 1, hy - 1, 1)
        _eye(screen, hx + facing * 3, hy - 1, 1)
    pygame.draw.circle(screen, (240, 180, 180),
                       (int(hx + facing * 4 + nose_twitch), int(hy + 2)), 1)