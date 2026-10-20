"""heroine.py — девушка с кастомизацией + idle-анимации и анимации удара/урона."""
import math
import random
import pygame


SKIN_COLORS = {
    "light":  {"name": "Светлая",   "base": (250, 215, 190), "shadow": (220, 185, 160)},
    "warm":   {"name": "Тёплая",    "base": (245, 205, 175), "shadow": (215, 175, 145)},
    "tan":    {"name": "Загорелая", "base": (220, 170, 130), "shadow": (190, 140, 100)},
    "dark":   {"name": "Тёмная",    "base": (150, 100, 70),  "shadow": (120, 75, 50)},
}

HAIR_COLORS = {
    "brown":   {"name": "Каштан",  "base": (110, 70, 35),  "light": (150, 100, 55)},
    "black":   {"name": "Чёрный",  "base": (40, 30, 30),   "light": (70, 55, 55)},
    "blonde":  {"name": "Блонд",   "base": (240, 210, 120), "light": (255, 235, 160)},
    "red":     {"name": "Рыжий",   "base": (200, 100, 50), "light": (230, 140, 80)},
    "pink":    {"name": "Розовый", "base": (230, 120, 180), "light": (250, 160, 210)},
    "blue":    {"name": "Синий",   "base": (90, 130, 200), "light": (130, 170, 230)},
}

HAIRSTYLES = ["short", "long", "ponytail", "buns", "braid"]
HAIRSTYLE_NAMES = {"short": "Короткие", "long": "Длинные",
                   "ponytail": "Хвост", "buns": "Пучки", "braid": "Коса"}

TOP_STYLES = ["none", "tank", "shirt", "hoodie", "bikini"]
TOP_NAMES = {"none": "Без верха", "tank": "Майка",
             "shirt": "Рубашка", "hoodie": "Худи", "bikini": "Купальник"}
TOP_COLORS = {"tank": (70, 120, 60), "shirt": (200, 70, 110),
              "hoodie": (90, 90, 150), "bikini": (240, 200, 60)}

BOTTOM_STYLES = ["none", "shorts", "skirt", "jeans", "bikini"]
BOTTOM_NAMES = {"none": "Без низа", "shorts": "Шорты",
                "skirt": "Юбка", "jeans": "Джинсы", "bikini": "Купальник"}
BOTTOM_COLORS = {"shorts": (95, 70, 45), "skirt": (200, 80, 80),
                 "jeans": (50, 60, 110), "bikini": (240, 90, 90)}

SHOES_STYLES = ["bare", "shoes", "sandals", "boots"]
SHOES_NAMES = {"bare": "Босиком", "shoes": "Кроссовки",
               "sandals": "Сандалии", "boots": "Ботинки"}

ACCESSORY_STYLES = ["none", "leaf", "clip", "flower", "glasses", "hat"]
ACCESSORY_NAMES = {"none": "Нет", "leaf": "Листик", "clip": "Заколка",
                   "flower": "Цветок", "glasses": "Очки", "hat": "Шляпа"}

DEFAULT_LOOK = {
    "skin": "warm", "hair_color": "brown", "hairstyle": "long",
    "top": "tank", "bottom": "skirt", "shoes": "shoes", "accessory": "leaf",
}

SLOT_ORDER = ["skin", "hair_color", "hairstyle", "top", "bottom", "shoes", "accessory"]
SLOT_NAMES = {"skin": "Кожа", "hair_color": "Цвет волос", "hairstyle": "Причёска",
              "top": "Верх", "bottom": "Низ", "shoes": "Обувь", "accessory": "Аксессуар"}
SLOT_OPTIONS = {
    "skin": list(SKIN_COLORS.keys()),
    "hair_color": list(HAIR_COLORS.keys()),
    "hairstyle": HAIRSTYLES,
    "top": TOP_STYLES, "bottom": BOTTOM_STYLES,
    "shoes": SHOES_STYLES, "accessory": ACCESSORY_STYLES,
}
SLOT_DISPLAY_NAMES = {
    "skin": {k: v["name"] for k, v in SKIN_COLORS.items()},
    "hair_color": {k: v["name"] for k, v in HAIR_COLORS.items()},
    "hairstyle": HAIRSTYLE_NAMES,
    "top": TOP_NAMES, "bottom": BOTTOM_NAMES,
    "shoes": SHOES_NAMES, "accessory": ACCESSORY_NAMES,
}


def normalize_look(look):
    out = dict(DEFAULT_LOOK)
    if look:
        out.update(look)
    for slot in SLOT_ORDER:
        if out.get(slot) not in SLOT_OPTIONS[slot]:
            out[slot] = DEFAULT_LOOK[slot]
    return out


def random_look():
    return {
        "skin": random.choice(list(SKIN_COLORS.keys())),
        "hair_color": random.choice(list(HAIR_COLORS.keys())),
        "hairstyle": random.choice(HAIRSTYLES),
        "top": random.choice(TOP_STYLES),
        "bottom": random.choice(BOTTOM_STYLES),
        "shoes": random.choice(SHOES_STYLES),
        "accessory": random.choice(ACCESSORY_STYLES),
    }


def _shadow(screen, cx, cy, w, h=8):
    s = pygame.Surface((max(1, w), max(1, h)), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 80), (0, 0, w, h))
    screen.blit(s, (cx - w // 2, cy - h // 2))


def _draw_hair_back(screen, hx, hy, look, bob, sway, facing):
    style = look["hairstyle"]
    hc = HAIR_COLORS[look["hair_color"]]
    base = hc["base"]
    if style == "short":
        pygame.draw.ellipse(screen, base, (hx - 11 + sway, hy - 8 + bob, 22, 16))
    elif style == "long":
        pygame.draw.ellipse(screen, base, (hx - 12 + sway, hy - 10 + bob, 24, 20))
        pygame.draw.polygon(screen, base, [
            (hx - 12 + sway, hy - 4 + bob), (hx - 14 + sway, hy + 22 + bob),
            (hx - 4 + sway, hy + 24 + bob), (hx - 2 + sway, hy - 2 + bob)])
        pygame.draw.polygon(screen, base, [
            (hx + 12 + sway, hy - 4 + bob), (hx + 14 + sway, hy + 22 + bob),
            (hx + 4 + sway, hy + 24 + bob), (hx + 2 + sway, hy - 2 + bob)])
    elif style == "ponytail":
        pygame.draw.ellipse(screen, base, (hx - 11 + sway, hy - 9 + bob, 22, 18))
        tail_dir = -facing
        pygame.draw.polygon(screen, base, [
            (hx + tail_dir * 8 + sway, hy - 6 + bob),
            (hx + tail_dir * 20 + sway, hy + 4 + bob),
            (hx + tail_dir * 22 + sway, hy + 18 + bob),
            (hx + tail_dir * 12 + sway, hy + 14 + bob),
            (hx + tail_dir * 6 + sway, hy + 2 + bob)])
    elif style == "buns":
        pygame.draw.ellipse(screen, base, (hx - 10 + sway, hy - 9 + bob, 20, 16))
        pygame.draw.circle(screen, base, (hx - 9 + sway, hy - 9 + bob), 5)
        pygame.draw.circle(screen, base, (hx + 9 + sway, hy - 9 + bob), 5)
    elif style == "braid":
        pygame.draw.ellipse(screen, base, (hx - 11 + sway, hy - 9 + bob, 22, 18))
        braid_x = hx - facing * 10 + sway
        for i in range(5):
            by = hy + 2 + bob + i * 5
            pygame.draw.circle(screen, base, (int(braid_x), int(by)), 4)
            pygame.draw.circle(screen, hc["light"], (int(braid_x) - 1, int(by) - 1), 2)


def _draw_hair_front(screen, hx, hy, look, bob, sway, facing):
    style = look["hairstyle"]
    hc = HAIR_COLORS[look["hair_color"]]
    base, light = hc["base"], hc["light"]
    if style in ("long", "ponytail", "braid"):
        pygame.draw.ellipse(screen, base, (hx - 11 + sway, hy - 11 + bob, 22, 9))
    elif style == "short":
        pygame.draw.ellipse(screen, base, (hx - 10 + sway, hy - 11 + bob, 20, 8))
    elif style == "buns":
        pygame.draw.ellipse(screen, base, (hx - 10 + sway, hy - 10 + bob, 20, 8))
    pygame.draw.ellipse(screen, light, (hx - 7 + sway, hy - 9 + bob, 6, 3))
    pygame.draw.line(screen, light, (hx + facing * 2, hy - 9 + bob),
                     (hx + facing * 6, hy - 5 + bob), 1)


def _draw_legs(screen, cx, cy, look, bob, moving, leg_swing):
    skin = SKIN_COLORS[look["skin"]]
    shoes = look["shoes"]
    for i, dx in enumerate((-4, 4)):
        lx = cx + dx
        # leg_swing теперь float — округляем для rect
        offset = int(leg_swing) if moving else 0
        if moving:
            lx += offset if i == 0 else -offset
        pygame.draw.rect(screen, skin["base"], (lx - 3, cy - 14, 6, 12))
        pygame.draw.line(screen, skin["shadow"], (cx, cy - 13), (cx, cy - 3), 1)
        if shoes == "shoes":
            pygame.draw.rect(screen, (30, 30, 40), (lx - 4, cy - 3, 8, 4), border_radius=2)
            pygame.draw.rect(screen, (200, 200, 210), (lx - 4, cy - 3, 8, 1))
        elif shoes == "sandals":
            pygame.draw.rect(screen, (250, 245, 235), (lx - 4, cy - 2, 8, 2))
            pygame.draw.line(screen, (180, 140, 100), (lx - 3, cy - 3), (lx + 3, cy - 3), 1)
        elif shoes == "boots":
            pygame.draw.rect(screen, (80, 50, 30), (lx - 4, cy - 8, 8, 9), border_radius=2)
            pygame.draw.line(screen, (50, 30, 15), (lx - 4, cy - 4), (lx + 4, cy - 4), 1)


def _draw_torso_and_arms(screen, cx, cy, look, bob, moving, phase, facing,
                        arm_reach=0.0, hurt_offset=0, breath=0.0):
    """breath — 0..1, добавляет подъём плеч при дыхании."""
    skin = SKIN_COLORS[look["skin"]]
    top = look["top"]
    cx += hurt_offset
    breath_offset = int(breath * 1.5)
    torso = pygame.Rect(cx - 7, cy - 36 + bob - breath_offset, 14, 16)

    if top == "none":
        pygame.draw.rect(screen, skin["base"], torso, border_radius=4)
        pygame.draw.line(screen, skin["shadow"], (cx, cy - 34 + bob), (cx, cy - 22 + bob), 1)
    elif top == "bikini":
        pygame.draw.rect(screen, skin["base"], torso, border_radius=4)
        pygame.draw.ellipse(screen, TOP_COLORS["bikini"], (cx - 7, cy - 32 + bob, 7, 5))
        pygame.draw.ellipse(screen, TOP_COLORS["bikini"], (cx, cy - 32 + bob, 7, 5))
        pygame.draw.rect(screen, TOP_COLORS["bikini"], (cx - 7, cy - 27 + bob, 14, 2))
    else:
        color = TOP_COLORS.get(top, (100, 100, 100))
        pygame.draw.rect(screen, color, torso, border_radius=4)
        pygame.draw.rect(screen, tuple(max(0, c - 30) for c in color),
                         torso, 1, border_radius=4)

    arm_swing = math.sin(phase) * 3 if moving else 0
    for sign in (-1, 1):
        shoulder_x = cx + sign * 8
        shoulder_y = cy - 33 + bob - breath_offset
        reach = arm_reach if sign == facing else 0
        hand_x = cx + sign * (11 + arm_swing * sign * 0.5) + facing * reach * 14
        hand_y = cy - 22 + bob - reach * 4 - breath_offset
        pygame.draw.line(screen, skin["base"], (shoulder_x, shoulder_y + 3),
                         (hand_x, hand_y), 4)
        pygame.draw.circle(screen, skin["base"], (int(hand_x), int(hand_y)), 3)


def _draw_bottom(screen, cx, cy, look, bob, moving, phase, hurt_offset=0):
    cx += hurt_offset
    bottom = look["bottom"]
    if bottom == "none":
        return
    color = BOTTOM_COLORS.get(bottom, (80, 80, 80))
    dark = tuple(max(0, c - 30) for c in color)
    if bottom == "shorts":
        rect = pygame.Rect(cx - 9, cy - 24 + bob, 18, 10)
        pygame.draw.rect(screen, color, rect, border_radius=3)
    elif bottom == "skirt":
        rect = pygame.Rect(cx - 11, cy - 24 + bob, 22, 12)
        pygame.draw.polygon(screen, color, [
            (rect.x, rect.y), (rect.right, rect.y),
            (rect.right + 3, rect.bottom), (rect.x - 3, rect.bottom)])
        pygame.draw.line(screen, dark, (rect.x, rect.y), (rect.right, rect.y), 1)
    elif bottom == "jeans":
        rect = pygame.Rect(cx - 9, cy - 24 + bob, 18, 12)
        pygame.draw.rect(screen, color, rect, border_radius=2)
        pygame.draw.line(screen, dark, (cx, rect.y + 1), (cx, rect.bottom), 1)
    elif bottom == "bikini":
        rect = pygame.Rect(cx - 8, cy - 24 + bob, 16, 6)
        pygame.draw.ellipse(screen, color, rect)


def _draw_head(screen, hx, hy, look, bob, facing, blink, eye_dx, eye_dy, hurt=False):
    skin = SKIN_COLORS[look["skin"]]
    pygame.draw.rect(screen, skin["shadow"], (hx - 3, hy + 8 + bob, 6, 6))
    pygame.draw.circle(screen, skin["base"], (hx, hy + bob), 10)
    pygame.draw.circle(screen, skin["shadow"], (hx, hy + bob), 10, 1)
    pygame.draw.circle(screen, (245, 160, 160), (hx - 5 + facing * 2, hy + 3 + bob), 2)
    pygame.draw.circle(screen, (245, 160, 160), (hx + 5 + facing * 2, hy + 3 + bob), 2)
    base_x = hx + facing * 1
    base_y = hy - 1 + bob
    for sign in (-1, 1):
        ex = base_x + sign * 4
        if blink or hurt:
            pygame.draw.line(screen, (80, 50, 40),
                             (ex - 2, base_y + eye_dy // 3),
                             (ex + 2, base_y + eye_dy // 3), 2)
        else:
            pygame.draw.ellipse(screen, (250, 250, 250),
                                (ex - 3, base_y - 3 + eye_dy // 2, 6, 6))
            pygame.draw.ellipse(screen, (100, 80, 70),
                                (ex - 3, base_y - 3 + eye_dy // 2, 6, 6), 1)
            px, py = ex + eye_dx, base_y + eye_dy
            pygame.draw.circle(screen, (40, 30, 30), (int(px), int(py)), 2)
            pygame.draw.circle(screen, (255, 255, 255), (int(px) + 1, int(py) - 1), 1)
    if hurt:
        pygame.draw.ellipse(screen, (120, 40, 40), (hx - 3, hy + 4 + bob, 6, 5))
    else:
        pygame.draw.arc(screen, (170, 80, 80), (hx - 3, hy + 4 + bob, 6, 4), 3.14, 6.28, 1)
    if look["accessory"] == "glasses":
        pygame.draw.circle(screen, (40, 40, 40), (hx - 4, hy - 1 + bob), 4, 1)
        pygame.draw.circle(screen, (40, 40, 40), (hx + 4, hy - 1 + bob), 4, 1)
        pygame.draw.line(screen, (40, 40, 40), (hx - 1, hy - 1 + bob), (hx + 1, hy - 1 + bob), 1)


def _draw_accessory(screen, hx, hy, look, bob, facing):
    acc = look["accessory"]
    if acc == "leaf":
        pygame.draw.ellipse(screen, (120, 190, 90), (hx + facing * 8, hy - 10 + bob, 5, 3))
    elif acc == "clip":
        pygame.draw.circle(screen, (240, 220, 100), (hx - facing * 8, hy - 8 + bob), 2)
    elif acc == "flower":
        fx, fy = hx + facing * 8, hy - 8 + bob
        for dx, dy in ((0, -3), (3, 0), (0, 3), (-3, 0)):
            pygame.draw.circle(screen, (250, 130, 160), (int(fx + dx), int(fy + dy)), 2)
        pygame.draw.circle(screen, (250, 230, 120), (int(fx), int(fy)), 2)
    elif acc == "hat":
        pygame.draw.ellipse(screen, (140, 100, 60), (hx - 14, hy - 8 + bob, 28, 5))
        pygame.draw.rect(screen, (140, 100, 60), (hx - 9, hy - 18 + bob, 18, 10), border_radius=3)


def draw_heroine(screen, cx, cy, look, phase=0.0, moving=False,
                 facing=1, blink=False, eye_dir=(0, 0), scale=0.8,
                 attacking=0.0, hurt=0.0, shiver=0.0,
                 idle_time=0.0, anim_phase_blend=0.0):
    """
    idle_time — сколько секунд стоит без движения (для idle-анимаций).
    anim_phase_blend — 0..1: 1 = полностью анимация ходьбы, 0 = полностью покой.
                       Плавный переход между ходьбой и покоем.
    """
    look = normalize_look(look)
    t = pygame.time.get_ticks() / 1000.0

    # Плавное смешивание анимаций
    walk_amt = anim_phase_blend
    idle_amt = 1.0 - walk_amt

    # === Анимация ходьбы ===
    walk_bob = math.sin(phase) * 1.5 if moving else 0
    walk_sway = math.sin(phase + 0.5) * 2 if moving else 0
    walk_leg = math.sin(phase) * 2 if moving else 0

    # === Idle-анимации ===
    # Дыхание: всегда лёгкое, но медленнее
    breath = (math.sin(t * 2.0) + 1) / 2  # 0..1
    idle_breath_offset = breath * 0.8
    # Лёгкое покачивание тела
    idle_sway = math.sin(t * 1.2) * 1.2
    # Иногда потягивание (раз в ~8 сек)
    stretch_cycle = t % 8.0
    stretch = 0.0
    if stretch_cycle < 1.5 and idle_time > 2:
        # 0..1..0
        p = stretch_cycle / 1.5
        stretch = math.sin(p * math.pi) * 3
    # Иногда поворот головы (раз в ~5 сек)
    head_turn_cycle = t % 5.0
    head_turn = 0.0
    if idle_time > 1.5 and head_turn_cycle < 1.0:
        head_turn = math.sin(head_turn_cycle / 1.0 * math.pi) * 2

    # === Смешиваем ===
    bob = walk_bob * walk_amt + (-idle_breath_offset) * idle_amt + stretch * 0.3
    sway = walk_sway * walk_amt + idle_sway * idle_amt
    leg_swing = walk_leg * walk_amt

    # Смещение при уроне
    hurt_offset = int(hurt * 6 * -facing)
    if shiver > 0:
        hurt_offset += int(math.sin(t * 30) * shiver * 2)

    BASE_W = 90
    BASE_H = 140
    GROUND_Y = BASE_H - 10

    tmp = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
    lx, ly = BASE_W // 2, GROUND_Y

    head_x = lx + facing
    head_y = ly - 46 + bob

    _draw_hair_back(tmp, head_x, head_y, look, bob, sway, facing)
    _draw_legs(tmp, lx + hurt_offset, ly, look, bob, moving and walk_amt > 0.5, leg_swing)
    _draw_bottom(tmp, lx + hurt_offset, ly, look, bob, moving, phase, hurt_offset=0)
    _draw_torso_and_arms(tmp, lx, ly, look, bob, moving, phase, facing,
                        arm_reach=attacking, hurt_offset=hurt_offset,
                        breath=breath * idle_amt)
    edx, edy = eye_dir
    _draw_head(tmp, head_x + hurt_offset + head_turn, head_y, look, bob, facing, blink,
               int(edx * 1.5), int(edy * 1.5), hurt=(hurt > 0.5))
    _draw_hair_front(tmp, head_x + hurt_offset + head_turn, head_y, look, bob, sway, facing)
    if look["accessory"] != "glasses":
        _draw_accessory(tmp, head_x + hurt_offset + head_turn, head_y, look, bob, facing)

    if hurt > 0:
        flash = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
        flash.fill((255, 40, 40, int(100 * hurt)))
        tmp.blit(flash, (0, 0))

    if shiver > 0.3:
        cold = pygame.Surface((BASE_W, BASE_H), pygame.SRCALPHA)
        cold.fill((100, 150, 255, int(60 * shiver)))
        tmp.blit(cold, (0, 0))

    if abs(scale - 1.0) < 0.001:
        screen.blit(tmp, (cx - BASE_W // 2, cy - GROUND_Y))
    else:
        new_w = int(BASE_W * scale)
        new_h = int(BASE_H * scale)
        scaled = pygame.transform.smoothscale(tmp, (new_w, new_h))
        blit_y = cy - int(GROUND_Y * scale)
        screen.blit(scaled, (cx - new_w // 2, blit_y))


def draw_style_preview(screen, look, cx, cy, scale=1.0):
    r = int(10 * scale)
    skin = SKIN_COLORS[look["skin"]]
    hc = HAIR_COLORS[look["hair_color"]]
    pygame.draw.circle(screen, hc["base"], (cx, cy), r + 3)
    pygame.draw.circle(screen, skin["base"], (cx, cy), r)
    pygame.draw.circle(screen, (250, 250, 250), (cx - 3, cy - 1), 2)
    pygame.draw.circle(screen, (250, 250, 250), (cx + 3, cy - 1), 2)
    pygame.draw.circle(screen, (40, 30, 30), (cx - 3, cy - 1), 1)
    pygame.draw.circle(screen, (40, 30, 30), (cx + 3, cy - 1), 1)
    pygame.draw.ellipse(screen, hc["base"], (cx - r, cy - r - 2, r * 2, int(r * 0.8)))