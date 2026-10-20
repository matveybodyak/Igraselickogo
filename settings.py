"""settings.py — глобальные константы, предметы, рецепты, шахты, фермерство."""
import pygame

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
TILE_SIZE = 32

WORLD_SIZES = {
    "small":   (120, 120),
    "medium":  (200, 200),
    "large":   (320, 320),
    "huge":    (500, 500),
}
WORLD_SIZE_NAMES = {
    "small":   "Маленький",
    "medium":  "Средний",
    "large":   "Большой",
    "huge":    "Огромный",
}
WORLD_SIZE_ORDER = ["small", "medium", "large", "huge"]
DEFAULT_WORLD_SIZE = "medium"

MAP_WIDTH = WORLD_SIZES[DEFAULT_WORLD_SIZE][0]
MAP_HEIGHT = WORLD_SIZES[DEFAULT_WORLD_SIZE][1]

GFX_LOW = "low"
GFX_MEDIUM = "medium"
GFX_HIGH = "high"
GFX_NAMES = {GFX_LOW: "Низкое", GFX_MEDIUM: "Среднее", GFX_HIGH: "Высокое"}
GFX_ORDER = [GFX_LOW, GFX_MEDIUM, GFX_HIGH]
DEFAULT_GFX = GFX_MEDIUM

TENT_INTERIOR_W = 20
TENT_INTERIOR_H = 14
MINE_INTERIOR_W = 40
MINE_INTERIOR_H = 30

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 120)
DARK_GRAY = (60, 60, 60)
LIGHT_GRAY = (200, 200, 200)
RED = (200, 60, 60)
GREEN = (60, 160, 60)
DARK_GREEN = (34, 100, 34)
BLUE = (70, 130, 200)
YELLOW = (230, 200, 60)
ORANGE = (230, 140, 50)
BROWN = (140, 90, 50)
DARK_BROWN = (90, 55, 30)
SKIN = (230, 190, 150)
WOOD = (160, 110, 60)
STONE = (130, 130, 130)
IRON = (170, 170, 190)
WATER = (50, 110, 200)
SAND = (230, 210, 150)
SNOW = (240, 240, 250)

BIOME_WATER = 0
BIOME_BEACH = 1
BIOME_GRASS = 2
BIOME_FOREST = 3
BIOME_MOUNTAIN = 4
BIOME_SNOW = 5

BIOME_COLORS = {
    BIOME_WATER: (55, 115, 200),
    BIOME_BEACH: (232, 214, 155),
    BIOME_GRASS: (105, 175, 85),
    BIOME_FOREST: (65, 135, 65),
    BIOME_MOUNTAIN: (80, 80, 85),
    BIOME_SNOW: (235, 235, 245),
}

SEASON_SPRING = 0
SEASON_SUMMER = 1
SEASON_AUTUMN = 2
SEASON_WINTER = 3
SEASON_NAMES = ["Весна", "Лето", "Осень", "Зима"]
SEASON_DAYS = 3
DAY_LENGTH_SECONDS = 600

DIFFICULTY_EASY = 0
DIFFICULTY_NORMAL = 1
DIFFICULTY_HARD = 2
DIFFICULTY_NAMES = ["Лёгкая", "Средняя", "Сложная"]
DIFFICULTY_MULT = {DIFFICULTY_EASY: 0.6, DIFFICULTY_NORMAL: 1.0, DIFFICULTY_HARD: 1.6}

PLAYER_SPEED = 3.2
PLAYER_MAX_HP = 100
PLAYER_MAX_HUNGER = 100
PLAYER_MAX_THIRST = 100
PLAYER_TEMP_DEFAULT = 50
PLAYER_TEMP_MAX = 100

HUNGER_RATE = 0.35
THIRST_RATE = 0.45
TEMP_COLD_RATE = 4.0
TEMP_HOT_RATE = 3.0

INV_COLS = 5
INV_ROWS = 6
SLOT_SIZE = 56
SLOT_PAD = 6
STACK_MAX = 64

# ---------- Культуры ----------
# seed → (имя урожая, время роста в секундах, кол-во урожая)
CROPS = {
    "wheat_seeds":   {"name": "Пшеница", "grow_time": 90.0,  "yield": 3, "color": (220, 190, 80)},
    "carrot_seeds":  {"name": "Морковь", "grow_time": 120.0, "yield": 2, "color": (230, 130, 50)},
    "pumpkin_seeds": {"name": "Тыква",   "grow_time": 180.0, "yield": 1, "color": (230, 150, 40)},
}
# seed → id урожая
CROP_RESULT = {
    "wheat_seeds":   "wheat",
    "carrot_seeds":  "carrot",
    "pumpkin_seeds": "pumpkin",
}

ITEMS = {
    "wood":        ("Дерево",         (160, 110, 60),  True),
    "stone":       ("Камень",         (130, 130, 130), True),
    "berry":       ("Ягоды",          (200, 60, 90),   True),
    "iron_ore":    ("Железная руда",  (150, 150, 180), True),
    "gold_ore":    ("Золотая руда",   (220, 190, 60),  True),
    "diamond":     ("Алмаз",          (180, 230, 250), True),
    "coal":        ("Уголь",          (40, 40, 45),    True),
    "fish":        ("Сырая рыба",     (120, 180, 200), True),
    "raw_meat":    ("Сырое мясо",     (200, 100, 100), True),
    "cooked_meat": ("Жареное мясо",   (150, 90, 50),   True),
    "leather":     ("Шкура",          (140, 100, 60),  True),
    "water_flask": ("Фляга воды",     (70, 130, 200),  False),
    "feather":     ("Перо",           (240, 240, 250), True),
    "wool":        ("Шерсть",         (230, 220, 200), True),
    "egg":         ("Яйцо",           (250, 245, 230), True),
    "milk":        ("Молоко",         (245, 245, 235), True),

    # семена и урожай
    "wheat_seeds":   ("Семена пшеницы",  (220, 190, 80),  True),
    "carrot_seeds":  ("Семена моркови",  (230, 150, 80),  True),
    "pumpkin_seeds": ("Семена тыквы",    (230, 170, 60),  True),
    "wheat":         ("Пшеница",         (230, 200, 90),  True),
    "carrot":        ("Морковь",         (230, 120, 40),  True),
    "pumpkin":       ("Тыква",           (230, 150, 40),  True),
    "farm_plot":     ("Грядка",          (110, 80, 50),   False),

    "axe":         ("Топор",          (120, 120, 120), False),
    "pickaxe":     ("Кирка",          (140, 140, 160), False),
    "rod":         ("Удочка",         (140, 100, 60),  False),
    "torch":       ("Факел",          (230, 160, 60),  True),
    "iron_pickaxe": ("Железная кирка", (170, 170, 190), False),

    "sword":       ("Меч",            (200, 200, 220), False),
    "iron_sword":  ("Железный меч",   (190, 200, 220), False),
    "diamond_sword": ("Алмазный меч", (170, 240, 250), False),
    "bow":         ("Лук",            (140, 90, 50),   False),

    "leather_armor": ("Кожаная броня", (150, 100, 60),  False),
    "iron_armor":    ("Железная броня", (170, 170, 190), False),
    "diamond_armor": ("Алмазная броня", (170, 230, 245), False),

    "wall":        ("Стена",          (120, 90, 60),   True),
    "door":        ("Дверь",          (150, 100, 60),  True),
    "bed":         ("Кровать",        (200, 80, 80),   False),
    "campfire":    ("Костёр",         (230, 100, 40),  True),
    "roof":        ("Крыша",          (100, 70, 40),   True),
    "tent":        ("Палатка",        (180, 100, 60),  False),
    "chest":       ("Сундук",         (150, 110, 60),  False),
}

WEAPONS = {
    "sword":         {"damage": 35},
    "iron_sword":    {"damage": 50},
    "diamond_sword": {"damage": 75},
    "bow":           {"damage": 40},
}

ARMOR = {
    "leather_armor": {"hp_bonus": 15},
    "iron_armor":    {"hp_bonus": 30},
    "diamond_armor": {"hp_bonus": 50},
}

# Еда, восстанавливаемая из культур
FOOD_VALUES = {
    "wheat":   {"hunger": 15, "thirst": 0},
    "carrot":  {"hunger": 20, "thirst": 5},
    "pumpkin": {"hunger": 35, "thirst": 10},
}

RECIPES = [
    {"name": "Топор",            "result": "axe",         "count": 1, "requires": {"wood": 3, "stone": 2}},
    {"name": "Кирка",            "result": "pickaxe",     "count": 1, "requires": {"wood": 3, "stone": 3}},
    {"name": "Железная кирка",   "result": "iron_pickaxe", "count": 1, "requires": {"wood": 2, "iron_ore": 3}},
    {"name": "Удочка",           "result": "rod",         "count": 1, "requires": {"wood": 4}},
    {"name": "Факел",            "result": "torch",       "count": 2, "requires": {"wood": 1, "coal": 1}},
    {"name": "Меч",              "result": "sword",       "count": 1, "requires": {"wood": 2, "iron_ore": 3}},
    {"name": "Железный меч",     "result": "iron_sword",  "count": 1, "requires": {"wood": 1, "iron_ore": 5, "coal": 2}},
    {"name": "Алмазный меч",     "result": "diamond_sword", "count": 1, "requires": {"wood": 1, "diamond": 3, "gold_ore": 2}},
    {"name": "Лук",              "result": "bow",         "count": 1, "requires": {"wood": 4, "feather": 2}},
    {"name": "Кожаная броня",    "result": "leather_armor", "count": 1, "requires": {"leather": 5, "wool": 2}},
    {"name": "Железная броня",   "result": "iron_armor",  "count": 1, "requires": {"iron_ore": 8, "leather": 2, "coal": 2}},
    {"name": "Алмазная броня",   "result": "diamond_armor", "count": 1, "requires": {"diamond": 5, "gold_ore": 3, "leather": 3}},
    {"name": "Стена",            "result": "wall",        "count": 2, "requires": {"wood": 3}},
    {"name": "Дверь",            "result": "door",        "count": 1, "requires": {"wood": 4}},
    {"name": "Кровать",          "result": "bed",         "count": 1, "requires": {"wood": 6, "leather": 2}},
    {"name": "Костёр",           "result": "campfire",    "count": 1, "requires": {"wood": 4, "stone": 3}},
    {"name": "Крыша",            "result": "roof",        "count": 2, "requires": {"wood": 2}},
    {"name": "Палатка",          "result": "tent",        "count": 1, "requires": {"wood": 8, "leather": 4}},
    {"name": "Сундук",           "result": "chest",       "count": 1, "requires": {"wood": 6}},
    {"name": "Грядка",           "result": "farm_plot",   "count": 1, "requires": {"wood": 4, "stone": 2}},
    {"name": "Омлет",            "result": "cooked_meat", "count": 1, "requires": {"egg": 2}},
    {"name": "Тёплый плед",      "result": "bed",         "count": 1, "requires": {"wool": 4, "wood": 2}},
    {"name": "Семена пшеницы",   "result": "wheat_seeds", "count": 2, "requires": {"berry": 3}},
    {"name": "Семена моркови",   "result": "carrot_seeds", "count": 2, "requires": {"berry": 2, "wheat": 1}},
    {"name": "Семена тыквы",     "result": "pumpkin_seeds", "count": 1, "requires": {"wheat": 2, "carrot": 1}},
]

DEFAULT_CONTROLS = {
    "up": pygame.K_w, "down": pygame.K_s, "left": pygame.K_a, "right": pygame.K_d,
    "interact": pygame.K_e, "inventory": pygame.K_i, "craft": pygame.K_c,
    "build": pygame.K_b, "attack": pygame.K_f, "sleep": pygame.K_SPACE,
    "pause": pygame.K_ESCAPE, "map": pygame.K_m, "travel": pygame.K_t,
    "enter": pygame.K_RETURN,
}

SAVE_DIR = "saves"
SETTINGS_FILE = "settings.json"

DEFAULT_MUSIC_VOLUME = 0.5
DEFAULT_SFX_VOLUME = 0.7
AUTOSAVE_ENABLED = True
AUTOSAVE_NAME = "autosave"


def get_font(size, bold=False):
    return pygame.font.SysFont("arial", size, bold=bold)