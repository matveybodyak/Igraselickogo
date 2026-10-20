"""game.py — Game: меню, пролог, HUD, шахта, фермерство."""
import json
import os
import math
import random
import pygame
from settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, GRAY, DARK_GRAY, GREEN, RED,
    YELLOW, BLUE, ORANGE, DEFAULT_CONTROLS, SETTINGS_FILE, DIFFICULTY_NAMES,
    DIFFICULTY_NORMAL, DAY_LENGTH_SECONDS, get_font, RECIPES, ITEMS,
    INV_COLS, INV_ROWS, SLOT_SIZE, SLOT_PAD, TILE_SIZE,
    AUTOSAVE_NAME, AUTOSAVE_ENABLED,
    DEFAULT_MUSIC_VOLUME, DEFAULT_SFX_VOLUME,
    WORLD_SIZE_NAMES, WORLD_SIZE_ORDER, GFX_NAMES, GFX_ORDER,
)
import heroine
import icons
import story
from audio import AudioManager
from particles import ParticleSystem


class Button:
    def __init__(self, rect, text, callback=None, color=DARK_GRAY, hover=(80, 80, 80)):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = hover
        self.font = get_font(28, bold=True)

    def draw(self, screen, mouse_pos):
        hovered = self.rect.collidepoint(mouse_pos)
        pygame.draw.rect(screen, self.hover_color if hovered else self.color,
                         self.rect, border_radius=8)
        pygame.draw.rect(screen, WHITE, self.rect, 2, border_radius=8)
        surf = self.font.render(self.text, True, WHITE)
        screen.blit(surf, surf.get_rect(center=self.rect.center))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) and self.callback:
                self.callback()


class Slider:
    def __init__(self, rect, value=0.5, label="Громкость", on_change=None):
        self.rect = pygame.Rect(rect)
        self.value = value
        self.label = label
        self.dragging = False
        self.on_change = on_change
        self.font = get_font(20)

    def draw(self, screen):
        pygame.draw.rect(screen, DARK_GRAY, self.rect, border_radius=4)
        fw = int(self.rect.w * self.value)
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y, fw, self.rect.h),
                         border_radius=4)
        pygame.draw.rect(screen, WHITE, self.rect, 1, border_radius=4)
        pygame.draw.circle(screen, WHITE, (self.rect.x + fw, self.rect.centery), 7)
        txt = self.font.render(f"{self.label}: {int(self.value * 100)}%", True, WHITE)
        screen.blit(txt, (self.rect.x, self.rect.y - 24))

    def handle(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(0, 20).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            rel = (event.pos[0] - self.rect.x) / self.rect.w
            self.value = max(0.0, min(1.0, rel))
            if self.on_change:
                self.on_change(self.value)


def _draw_bg_forest(screen, t):
    for y in range(SCREEN_HEIGHT):
        k = y / SCREEN_HEIGHT
        pygame.draw.line(screen, (int(120 + 60 * k), int(180 + 40 * k), int(100 + 40 * k)),
                         (0, y), (SCREEN_WIDTH, y))
    pygame.draw.circle(screen, (255, 240, 180), (SCREEN_WIDTH - 180, 130), 50)
    pygame.draw.circle(screen, (255, 250, 220), (SCREEN_WIDTH - 180, 130), 34)
    for i in range(28):
        tx = i * 50 - 20 + (t * 8) % 50
        th = 60 + (i * 13) % 40
        ty = SCREEN_HEIGHT - 120
        pygame.draw.rect(screen, (60, 40, 20), (tx, ty, 8, th))
        pygame.draw.circle(screen, (40, 100, 40), (tx + 4, ty - 10), th // 2 + 6)
        pygame.draw.circle(screen, (60, 130, 60), (tx + 4, ty - 10), th // 2)
    pygame.draw.rect(screen, (60, 130, 50), (0, SCREEN_HEIGHT - 130, SCREEN_WIDTH, 130))


def _draw_bg_city(screen, t):
    for y in range(SCREEN_HEIGHT):
        k = y / SCREEN_HEIGHT
        pygame.draw.line(screen, (int(20 + 30 * k), int(25 + 40 * k), int(60 + 80 * k)),
                         (0, y), (SCREEN_WIDTH, y))
    for i in range(80):
        sx = (i * 173) % SCREEN_WIDTH
        sy = (i * 71) % (SCREEN_HEIGHT // 2)
        a = max(0, min(255, 100 + int(100 * math.sin(t * 2 + i))))
        pygame.draw.circle(screen, (a, a, a), (sx, sy), 1)
    pygame.draw.circle(screen, (240, 240, 220), (SCREEN_WIDTH - 150, 100), 40)
    pygame.draw.circle(screen, (30, 35, 70), (SCREEN_WIDTH - 140, 90), 36)
    bx = 0
    while bx < SCREEN_WIDTH:
        bw = 60 + (bx * 17) % 50
        bh = 160 + (bx * 31) % 240
        by = SCREEN_HEIGHT - bh
        pygame.draw.rect(screen, (25, 30, 50), (bx, by, bw, bh))
        for wy in range(int(by) + 20, SCREEN_HEIGHT - 20, 24):
            for wx in range(bx + 10, bx + bw - 10, 18):
                lit = ((wx * 7 + wy * 13) % 10) < 6
                pygame.draw.rect(screen, (250, 220, 130) if lit else (40, 45, 70),
                                 (wx, wy, 8, 12))
        bx += bw + 6


def _draw_bg_beach(screen, t):
    for y in range(SCREEN_HEIGHT):
        k = y / SCREEN_HEIGHT
        pygame.draw.line(screen, (int(120 + 100 * k), int(190 + 40 * k), 230),
                         (0, y), (SCREEN_WIDTH, y))
    pygame.draw.circle(screen, (255, 250, 200), (SCREEN_WIDTH - 200, 110), 46)
    pygame.draw.circle(screen, (255, 240, 160), (SCREEN_WIDTH - 200, 110), 36)
    st = SCREEN_HEIGHT - 260
    pygame.draw.rect(screen, (60, 140, 200), (0, st, SCREEN_WIDTH, 160))
    for i in range(8):
        wy = st + i * 18
        for wx in range(0, SCREEN_WIDTH, 40):
            off = math.sin(t * 2 + wx * 0.02 + i) * 6
            pygame.draw.arc(screen, (120, 180, 230),
                            (wx, wy + off - 8, 40, 16), 3.14, 6.28, 2)
    pygame.draw.rect(screen, (240, 220, 160), (0, st + 160, SCREEN_WIDTH, 100))


BG_FUNCS = {"forest": _draw_bg_forest, "city": _draw_bg_city, "beach": _draw_bg_beach}
BG_ORDER = ["forest", "city", "beach"]
BG_NAMES = {"forest": "Лес", "city": "Город", "beach": "Пляж"}


def _blit_overlay(a, b):
    if a is None: return b
    if b is None: return a
    res = a.copy()
    res.blit(b, (0, 0))
    return res


class Game:
    MENU = "menu"
    SETTINGS = "settings"
    CONTROLS = "controls"
    LOAD_MENU = "load_menu"
    CUSTOMIZE = "customize"
    PROLOGUE = "prologue"
    PLAY = "play"
    PAUSE = "pause"
    INVENTORY = "inventory"
    CRAFT = "craft"
    GAME_OVER = "game_over"

    def __init__(self, screen):
        self.screen = screen
        self.state = Game.MENU
        self.running = True
        self.time = 0.0
        self.font_title = get_font(72, bold=True)
        self.font_big = get_font(40, bold=True)
        self.font = get_font(26)
        self.font_small = get_font(20)
        self.font_tiny = get_font(16)
        self.font_prologue = get_font(24)
        self.font_prologue_title = get_font(48, bold=True)

        self.settings = self._load_settings()
        self._apply_fullscreen()
        self.hero_look = heroine.normalize_look(self.settings.get("hero_look"))
        self.menu_bg = self.settings.get("menu_bg", "forest")
        self.world_size = self.settings.get("world_size", "medium")
        self.graphics = self.settings.get("graphics", "medium")

        self.audio = AudioManager()
        self.audio.set_music_volume(self.settings.get("music_volume", DEFAULT_MUSIC_VOLUME))
        self.audio.set_sfx_volume(self.settings.get("sfx_volume", DEFAULT_SFX_VOLUME))
        self.audio.play_music("menu")

        self.particles = ParticleSystem()

        cx = SCREEN_WIDTH // 2
        self.menu_buttons = [
            Button((cx - 150, 340, 300, 52), "Новая игра", self.start_new_game),
            Button((cx - 150, 402, 300, 52), "Загрузить", self.open_load_menu),
            Button((cx - 150, 464, 300, 52), "Кастомизация", self.open_customize),
            Button((cx - 150, 526, 300, 52), "Настройки", self.open_settings),
            Button((cx - 150, 588, 300, 52), "Выход", self.quit_game),
        ]
        self.bg_buttons = []
        bw, bh, gap = 90, 40, 14
        sx2 = SCREEN_WIDTH - (len(BG_ORDER) * (bw + gap)) - 30
        for i, bg in enumerate(BG_ORDER):
            self.bg_buttons.append((bg, pygame.Rect(sx2 + i * (bw + gap), 30, bw, bh)))

        self.music_slider = Slider((cx - 200, 170, 400, 16),
                                   value=self.settings.get("music_volume", DEFAULT_MUSIC_VOLUME),
                                   label="Музыка", on_change=self._on_music_volume)
        self.sfx_slider = Slider((cx - 200, 230, 400, 16),
                                 value=self.settings.get("sfx_volume", DEFAULT_SFX_VOLUME),
                                 label="Звуки", on_change=self._on_sfx_volume)
        self.size_btn = None
        self.graphics_btn = None
        self.fullscreen_btn = Button((cx - 200, 420, 400, 46), "Полный экран: ВЫКЛ",
                                     self.toggle_fullscreen)
        self.difficulty_btn = Button((cx - 200, 470, 400, 46),
                                     f"Сложность: {DIFFICULTY_NAMES[self.settings['difficulty']]}",
                                     self.cycle_difficulty)
        self.controls_btn = Button((cx - 200, 520, 400, 46), "Управление", self.open_controls)
        self.back_btn = Button((cx - 100, 590, 200, 50), "Назад", self.back_to_menu)
        self.gameover_btn = Button((cx - 100, 460, 200, 50), "В меню", self._gameover_to_menu)
        self._update_settings_buttons()

        self.customize_selected = 0
        self.customize_rects = []

        # Пролог
        self.prologue_page = 0

        self.player = None
        self.world = None
        self.camera = None
        self.daynight = None
        self.build_manager = None
        self.craft_selected = 0
        self.craft_rects = []
        self.inv_origin = (0, 0)
        self.save_list = []
        self.show_big_map = False
        self._autosave_last_day = 0
        self._last_splash = 0.0
        self._last_fire = 0.0

        self.worlds = {}
        self.player_positions = {}
        self.current_location = "village"
        self.travel_map_open = False
        self.near_border = None
        self.border_target = None
        self.travel_click_pending = False

        self.overworld = None
        self.overworld_location = None
        self.overworld_position = None
        self.tent_world = None
        self.mine_world = None

    def _on_music_volume(self, v):
        self.settings["music_volume"] = v
        self.audio.set_music_volume(v)
        self._save_settings()

    def _on_sfx_volume(self, v):
        self.settings["sfx_volume"] = v
        self.audio.set_sfx_volume(v)
        self._save_settings()
        self.audio.play_sfx("pickup")

    def _load_settings(self):
        default = {"volume": 0.5, "music_volume": DEFAULT_MUSIC_VOLUME,
                   "sfx_volume": DEFAULT_SFX_VOLUME,
                   "fullscreen": False, "difficulty": DIFFICULTY_NORMAL,
                   "controls": dict(DEFAULT_CONTROLS),
                   "hero_look": dict(heroine.DEFAULT_LOOK), "menu_bg": "forest",
                   "world_size": "medium", "graphics": "medium"}
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    default.update(json.load(f))
            except Exception:
                pass
        return default

    def _save_settings(self):
        try:
            with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _apply_fullscreen(self):
        flags = pygame.FULLSCREEN if self.settings["fullscreen"] else 0
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), flags)

    def _update_settings_buttons(self):
        self.fullscreen_btn.text = "Полный экран: " + ("ВКЛ" if self.settings["fullscreen"] else "ВЫКЛ")
        self.difficulty_btn.text = f"Сложность: {DIFFICULTY_NAMES[self.settings['difficulty']]}"

    # ---------- Пролог ----------
    def start_new_game(self):
        self.prologue_page = 0
        self.state = Game.PROLOGUE

    def _advance_prologue(self):
        self.prologue_page += 1
        if self.prologue_page >= len(story.PROLOGUE_PAGES):
            self.new_game()

    # ---------- Новая игра (после пролога) ----------
    def new_game(self):
        from world import (World, LOCATION_VILLAGE, LOCATION_CITY,
                           LOCATION_MOUNTAINS, LOCATION_SEA)
        from player import Player
        from camera import Camera
        from daynight import DayNightCycle
        from inventory import Inventory
        from building import BuildManager

        base_seed = random.randint(0, 10**9)
        size_key = self.world_size

        self.worlds = {
            LOCATION_VILLAGE: World(seed=base_seed + 1, location=LOCATION_VILLAGE, size_key=size_key),
            LOCATION_CITY: World(seed=base_seed + 2, location=LOCATION_CITY, size_key=size_key),
            LOCATION_MOUNTAINS: World(seed=base_seed + 3, location=LOCATION_MOUNTAINS, size_key=size_key),
            LOCATION_SEA: World(seed=base_seed + 4, location=LOCATION_SEA, size_key=size_key),
        }
        self.current_location = LOCATION_VILLAGE
        self.world = self.worlds[LOCATION_VILLAGE]
        spawn = self.world.find_spawn()

        self.player = Player(spawn[0], spawn[1], look=self.hero_look)
        self.player.audio = self.audio
        self.player.inventory = Inventory(INV_COLS, INV_ROWS)
        # Стартовый набор (после кораблекрушения)
        for item, cnt in [("wood", 3), ("stone", 2),
                          ("berry", 3), ("water_flask", 1),
                          ("wheat_seeds", 2)]:
            self.player.inventory.add_item(item, cnt)

        self.player_positions = {self.current_location: (self.player.x, self.player.y)}

        self.camera = Camera()
        self.camera.set_world_size(self.world.map_w, self.world.map_h)
        self.camera.follow(self.player.x, self.player.y)
        self.camera.x = self.camera.target_x
        self.camera.y = self.camera.target_y

        self.daynight = DayNightCycle(DAY_LENGTH_SECONDS)
        self.build_manager = BuildManager()
        self.craft_selected = 0
        self._autosave_last_day = self.daynight.day_count
        self.tent_world = None
        self.mine_world = None
        self.overworld = None
        self.state = Game.PLAY
        self.audio.play_music("game")

    def open_load_menu(self):
        from save_system import list_saves
        self.save_list = list_saves()
        self.state = Game.LOAD_MENU

    def open_customize(self):
        self.customize_selected = 0
        self.state = Game.CUSTOMIZE

    def open_settings(self): self.state = Game.SETTINGS
    def open_controls(self): self.state = Game.CONTROLS

    def back_to_menu(self):
        self.settings["hero_look"] = dict(self.hero_look)
        self.settings["menu_bg"] = self.menu_bg
        self.settings["world_size"] = self.world_size
        self.settings["graphics"] = self.graphics
        self._save_settings()
        self.state = Game.MENU
        self.audio.play_music("menu")

    def toggle_fullscreen(self):
        self.settings["fullscreen"] = not self.settings["fullscreen"]
        self._apply_fullscreen()
        self._update_settings_buttons()

    def cycle_difficulty(self):
        self.settings["difficulty"] = (self.settings["difficulty"] + 1) % 3
        self._update_settings_buttons()

    def quit_game(self):
        self._save_settings()
        self.audio.stop_music()
        self.running = False
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _gameover_to_menu(self):
        self.state = Game.MENU
        self.audio.play_music("menu")

    def load_game(self, filename):
        from save_system import load_game as _load
        from world import World, LOCATION_VILLAGE
        from player import Player
        from camera import Camera
        from daynight import DayNightCycle
        from building import BuildManager
        try:
            data = _load(filename)
            self.worlds = {}
            for loc_name, wdata in data.get("locations", {}).items():
                size_key = wdata.get("size_key", self.world_size)
                is_tent = wdata.get("is_tent", False)
                is_mine = wdata.get("is_mine", False)
                w = World(seed=wdata.get("seed", 0), location=loc_name,
                          size_key=size_key, is_tent=is_tent, is_mine=is_mine)
                w.load_state(wdata)
                self.worlds[loc_name] = w

            self.current_location = data.get("current_location", LOCATION_VILLAGE)
            self.world = self.worlds.get(self.current_location)
            if self.world is None:
                self.world = World(location=LOCATION_VILLAGE, size_key=self.world_size)
                self.worlds[self.current_location] = self.world

            pdata = data["player"]
            self.player = Player(pdata["x"], pdata["y"],
                                 look=pdata.get("look", self.hero_look))
            self.player.audio = self.audio
            self.player.load_state(pdata)

            self.player_positions = {}
            for k, v in data.get("player_positions", {}).items():
                self.player_positions[k] = tuple(v)
            self.player_positions[self.current_location] = (self.player.x, self.player.y)

            self.daynight = DayNightCycle(DAY_LENGTH_SECONDS)
            self.daynight.load_state(data["time"])

            self.camera = Camera()
            self.camera.set_world_size(self.world.map_w, self.world.map_h)
            self.camera.follow(self.player.x, self.player.y)
            self.camera.x = self.camera.target_x
            self.camera.y = self.camera.target_y

            self.build_manager = BuildManager()
            self._autosave_last_day = self.daynight.day_count
            self.tent_world = None
            self.mine_world = None
            self.overworld = None
            self.state = Game.PLAY
            self.audio.play_music("game")
        except Exception as e:
            print("Ошибка загрузки:", e)

    def travel_to(self, new_location):
        from world import LOCATION_NAMES
        if new_location == self.current_location: return
        if new_location not in self.worlds: return
        self.player_positions[self.current_location] = (self.player.x, self.player.y)
        self.current_location = new_location
        self.world = self.worlds[new_location]
        self.camera.set_world_size(self.world.map_w, self.world.map_h)
        if new_location in self.player_positions:
            self.player.x, self.player.y = self.player_positions[new_location]
        else:
            spawn = self.world.find_spawn()
            self.player.x, self.player.y = spawn
        self.camera.follow(self.player.x, self.player.y)
        self.camera.x = self.camera.target_x
        self.camera.y = self.camera.target_y
        self.world.mobs = []
        self.show_big_map = False
        self.travel_map_open = False
        self.audio.play_sfx("splash")
        self.particles.emit("splash", self.player.x, self.player.y, count=20)
        music = {"village": "game", "city": "city",
                 "mountains": "mountains", "sea": "sea"}.get(new_location, "game")
        self.audio.play_music(music)
        print(f"Путешествие → {LOCATION_NAMES.get(new_location, new_location)}")

    def _check_border(self):
        if self.world.is_tent or self.world.is_mine:
            self.near_border = None
            self.border_target = None
            return
        self.near_border = self.world.border_at(self.player.x, self.player.y)
        if self.near_border:
            self.border_target = self.world.get_border_target(self.near_border)
        else:
            self.border_target = None

    def enter_tent(self):
        from world import World, LOCATION_VILLAGE
        self.overworld = self.world
        self.overworld_location = self.current_location
        self.overworld_position = (self.player.x, self.player.y)
        if self.tent_world is None:
            self.tent_world = World(seed=self.world.seed + 999,
                                    location=LOCATION_VILLAGE, is_tent=True)
        self.world = self.tent_world
        self.current_location = "tent"
        self.camera.set_world_size(self.world.map_w, self.world.map_h)
        spawn = self.world.find_spawn()
        self.player.x, self.player.y = spawn
        self.camera.follow(self.player.x, self.player.y)
        self.camera.x = self.camera.target_x
        self.camera.y = self.camera.target_y
        self.audio.play_sfx("door")

    def exit_tent(self):
        if self.overworld is None: return
        self.world = self.overworld
        self.current_location = self.overworld_location
        self.camera.set_world_size(self.world.map_w, self.world.map_h)
        if self.overworld_position:
            self.player.x, self.player.y = self.overworld_position
        self.camera.follow(self.player.x, self.player.y)
        self.camera.x = self.camera.target_x
        self.camera.y = self.camera.target_y
        self.overworld = None
        self.overworld_position = None
        self.audio.play_sfx("door")

    def enter_mine(self):
        from world import World, LOCATION_VILLAGE
        self.overworld = self.world
        self.overworld_location = self.current_location
        self.overworld_position = (self.player.x, self.player.y)
        if self.mine_world is None:
            self.mine_world = World(seed=self.world.seed + 777,
                                    location=LOCATION_VILLAGE, is_mine=True)
        self.world = self.mine_world
        self.current_location = "mine"
        self.camera.set_world_size(self.world.map_w, self.world.map_h)
        spawn = self.world.find_spawn()
        self.player.x, self.player.y = spawn
        self.camera.follow(self.player.x, self.player.y)
        self.camera.x = self.camera.target_x
        self.camera.y = self.camera.target_y
        self.audio.play_sfx("door")

    def exit_mine(self):
        if self.overworld is None: return
        self.world = self.overworld
        self.current_location = self.overworld_location
        self.camera.set_world_size(self.world.map_w, self.world.map_h)
        if self.overworld_position:
            self.player.x, self.player.y = self.overworld_position
        self.camera.follow(self.player.x, self.player.y)
        self.camera.x = self.camera.target_x
        self.camera.y = self.camera.target_y
        self.overworld = None
        self.overworld_position = None
        self.audio.play_sfx("door")

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._save_settings()
                self.audio.stop_music()
                self.running = False
                return False
            if self.state == Game.MENU: self._handle_menu(event)
            elif self.state == Game.PROLOGUE: self._handle_prologue(event)
            elif self.state == Game.CUSTOMIZE: self._handle_customize(event)
            elif self.state == Game.SETTINGS: self._handle_settings(event)
            elif self.state == Game.CONTROLS: self.back_btn.handle(event)
            elif self.state == Game.LOAD_MENU: self._handle_load_menu(event)
            elif self.state == Game.PLAY: self._handle_play(event)
            elif self.state == Game.PAUSE: self._handle_pause(event)
            elif self.state == Game.INVENTORY: self._handle_inventory(event)
            elif self.state == Game.CRAFT: self._handle_craft(event)
            elif self.state == Game.GAME_OVER: self.gameover_btn.handle(event)
        return self.running

    def _handle_prologue(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.state = Game.MENU
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._advance_prologue()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._advance_prologue()

    def _handle_menu(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for bg, rect in self.bg_buttons:
                if rect.collidepoint(event.pos):
                    self.menu_bg = bg
                    self.settings["menu_bg"] = bg
                    self._save_settings()
                    return
        for b in self.menu_buttons:
            b.handle(event)
            if not self.running:
                return

    def _handle_settings(self, event):
        self.music_slider.handle(event)
        self.sfx_slider.handle(event)
        self.fullscreen_btn.handle(event)
        self.difficulty_btn.handle(event)
        self.controls_btn.handle(event)
        self.back_btn.handle(event)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.size_btn and self.size_btn.collidepoint(event.pos):
                idx = WORLD_SIZE_ORDER.index(self.world_size)
                self.world_size = WORLD_SIZE_ORDER[(idx + 1) % len(WORLD_SIZE_ORDER)]
                self.settings["world_size"] = self.world_size
                self._save_settings()
            elif self.graphics_btn and self.graphics_btn.collidepoint(event.pos):
                idx = GFX_ORDER.index(self.graphics)
                self.graphics = GFX_ORDER[(idx + 1) % len(GFX_ORDER)]
                self.settings["graphics"] = self.graphics
                self._save_settings()

    def _handle_customize(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.back_to_menu(); return
            if event.key == pygame.K_DOWN:
                self.customize_selected = (self.customize_selected + 1) % len(heroine.SLOT_ORDER)
                return
            if event.key == pygame.K_UP:
                self.customize_selected = (self.customize_selected - 1) % len(heroine.SLOT_ORDER)
                return
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self._change_slot(self.customize_selected,
                                  1 if event.key == pygame.K_RIGHT else -1)
                return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for action, rect in self.customize_rects:
                if rect.collidepoint(event.pos):
                    self._do_customize_action(action); return
        self.back_btn.handle(event)

    def _do_customize_action(self, action):
        kind, payload = action
        if kind == "select": self.customize_selected = payload
        elif kind == "prev": self._change_slot(payload, -1)
        elif kind == "next": self._change_slot(payload, 1)
        elif kind == "random": self.hero_look = heroine.random_look()
        elif kind == "save":
            self.settings["hero_look"] = dict(self.hero_look)
            self._save_settings()
            self.back_to_menu()

    def _change_slot(self, idx, delta):
        slot = heroine.SLOT_ORDER[idx]
        opts = heroine.SLOT_OPTIONS[slot]
        try: i = opts.index(self.hero_look[slot])
        except ValueError: i = 0
        self.hero_look[slot] = opts[(i + delta) % len(opts)]

    def _handle_load_menu(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = Game.MENU; return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, s in enumerate(self.save_list):
                rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 200 + i * 60, 500, 50)
                if rect.collidepoint(event.pos):
                    self.load_game(s["file"]); return

    def _handle_play(self, event):
        if self.build_manager and self.build_manager.active:
            if self.build_manager.handle_event(event, self.player, self.world, self.camera):
                return
        if self.travel_map_open:
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_t, pygame.K_ESCAPE):
                self.travel_map_open = False
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.travel_click_pending = True
                return
            return
        if self.world.is_tent or self.world.is_mine:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: self.state = Game.PAUSE
                elif event.key == pygame.K_e: self.player.interact(self.world, self)
                elif event.key == pygame.K_i: self.state = Game.INVENTORY
                elif event.key == pygame.K_c: self.state = Game.CRAFT
                elif event.key == pygame.K_f: self.player.use_item(self.world, self)
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.state = Game.PAUSE
            elif event.key == pygame.K_i: self.state = Game.INVENTORY
            elif event.key == pygame.K_c: self.state = Game.CRAFT
            elif event.key == pygame.K_b: self.build_manager.toggle()
            elif event.key == pygame.K_e:
                old_wood = self.player.inventory.count_item("wood")
                old_stone = self.player.inventory.count_item("stone")
                self.player.interact(self.world, self)
                if self.player.inventory.count_item("wood") > old_wood:
                    self.particles.emit("dust",
                                        self.player.x + self.player.facing * 30,
                                        self.player.y - 20, count=8,
                                        color=(180, 140, 80))
                elif self.player.inventory.count_item("stone") > old_stone:
                    self.particles.emit("dust",
                                        self.player.x + self.player.facing * 30,
                                        self.player.y - 20, count=8,
                                        color=(150, 150, 150))
            elif event.key == pygame.K_f: self.player.use_item(self.world, self)
            elif event.key == pygame.K_m:
                self.show_big_map = not self.show_big_map
                self.travel_map_open = False
            elif event.key == pygame.K_t:
                self.travel_map_open = not self.travel_map_open
                self.show_big_map = False
            elif event.key == pygame.K_SPACE:
                obj = self.world.find_interactable(*self.player.center, 56)
                if obj and obj.get("kind") == "bed":
                    self.player._sleep(self)
            elif pygame.K_1 <= event.key <= pygame.K_5:
                self.player.hotbar_selected = event.key - pygame.K_1
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.show_big_map:
                self.player.use_item(self.world, self)

    def _handle_pause(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.state = Game.PLAY
            elif event.key == pygame.K_q:
                self.state = Game.MENU
                self.audio.play_music("menu")
            elif event.key == pygame.K_s:
                if self.world.is_tent or self.world.is_mine:
                    print("Нельзя сохраняться в палатке/шахте — выйдите сначала")
                    return
                from save_system import save_game
                print("Сохранено:", save_game(self))

    def _handle_inventory(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_i, pygame.K_ESCAPE):
                if self.player.inventory.dragging is not None:
                    self.player.inventory.end_drag(-1)
                self.state = Game.PLAY; return
            if event.key == pygame.K_c: self.state = Game.CRAFT; return
        self.player.inventory.handle_event(event, self.inv_origin)

    def _handle_craft(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_c, pygame.K_ESCAPE):
                self.state = Game.PLAY; return
            if event.key == pygame.K_i: self.state = Game.INVENTORY; return
            if event.key == pygame.K_RETURN:
                self._do_craft(); return
            if event.key == pygame.K_DOWN:
                self.craft_selected = (self.craft_selected + 1) % len(RECIPES); return
            if event.key == pygame.K_UP:
                self.craft_selected = (self.craft_selected - 1) % len(RECIPES); return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self.craft_rects):
                if r.collidepoint(event.pos):
                    self.craft_selected = i
                    self._do_craft(); return

    def _do_craft(self):
        from inventory import Crafting
        if Crafting.craft(self.player.inventory, RECIPES[self.craft_selected]):
            self.audio.play_sfx("craft")

    def update(self, dt):
        self.time += dt
        if self.state == Game.PLAY and self.player:
            if not self.travel_map_open and not self.show_big_map:
                self.player.update(dt, self.world, self.daynight, self)
                self.world.update(dt, self.player, self.daynight)
                self.daynight.update(dt, self.world)
            self.camera.follow(self.player.x, self.player.y)
            self.camera.update()

            self._check_border()
            if self.border_target:
                edge_x = 6
                if (self.player.x < edge_x or
                        self.player.x > self.world.map_w * TILE_SIZE - edge_x or
                        self.player.y < edge_x or
                        self.player.y > self.world.map_h * TILE_SIZE - edge_x):
                    self.travel_to(self.border_target)

            if self.player.in_water:
                now = pygame.time.get_ticks() / 1000.0
                if now - self._last_splash > 0.8:
                    self._last_splash = now
                    self.audio.play_sfx("splash")
                    if self.graphics != "low":
                        self.particles.emit("splash", self.player.x, self.player.y, count=10)

            if self.player.near_campfire:
                now = pygame.time.get_ticks() / 1000.0
                if now - self._last_fire > 1.2:
                    self._last_fire = now
                    self.audio.play_sfx("campfire")

            if AUTOSAVE_ENABLED and self.daynight.day_count > self._autosave_last_day:
                self._autosave_last_day = self.daynight.day_count
                try:
                    from save_system import save_game
                    save_game(self, name=AUTOSAVE_NAME)
                except Exception:
                    pass

            if self.graphics != "low":
                self.particles.update(dt)
                self._spawn_ambient_particles(dt)

            if self.player.hp <= 0:
                self.state = Game.GAME_OVER

    def _spawn_ambient_particles(self, dt):
        if self.graphics == "low": return
        from world import SEASON_AUTUMN, SEASON_WINTER
        if len(self.particles.particles) > 300: return
        season = self.daynight.season
        is_night = self.daynight.is_night
        is_day = self.daynight.is_day
        cam_x, cam_y = self.camera.offset

        if is_day and random.random() < 0.02 * dt * 60:
            px = random.uniform(0, SCREEN_WIDTH) + cam_x
            py = random.uniform(SCREEN_HEIGHT * 0.4, SCREEN_HEIGHT) + cam_y
            self.particles.emit("butterfly", px, py, 1)
        if is_night and random.random() < 0.03 * dt * 60:
            px = random.uniform(0, SCREEN_WIDTH) + cam_x
            py = random.uniform(SCREEN_HEIGHT * 0.4, SCREEN_HEIGHT) + cam_y
            self.particles.emit("firefly", px, py, 1)
        if season == SEASON_AUTUMN and random.random() < 0.04 * dt * 60:
            px = random.uniform(0, SCREEN_WIDTH) + cam_x
            py = cam_y + random.uniform(-30, 0)
            self.particles.emit("leaf", px, py, 1)
        if season == SEASON_WINTER and random.random() < 0.05 * dt * 60:
            px = random.uniform(0, SCREEN_WIDTH) + cam_x
            py = cam_y + random.uniform(-30, 0)
            self.particles.emit("snow", px, py, 1)

    def draw(self):
        self.screen.fill(BLACK)
        if self.state == Game.MENU: self._draw_menu()
        elif self.state == Game.PROLOGUE: self._draw_prologue()
        elif self.state == Game.CUSTOMIZE: self._draw_customize()
        elif self.state == Game.SETTINGS: self._draw_settings()
        elif self.state == Game.CONTROLS: self._draw_controls()
        elif self.state == Game.LOAD_MENU: self._draw_load_menu()
        elif self.state == Game.PLAY:
            self._draw_play()
            if self.show_big_map: self._draw_big_map()
            if self.travel_map_open: self._draw_travel_map()
        elif self.state == Game.PAUSE: self._draw_play(); self._draw_pause()
        elif self.state == Game.INVENTORY: self._draw_play(); self._draw_inventory_overlay()
        elif self.state == Game.CRAFT: self._draw_play(); self._draw_craft_overlay()
        elif self.state == Game.GAME_OVER: self._draw_play(); self._draw_game_over()

    def _draw_prologue(self):
        """Экран пролога — тёмный фон, текст, анимация появления."""
        self.screen.fill((10, 10, 18))
        # Звёзды
        for i in range(80):
            sx = (i * 137) % SCREEN_WIDTH
            sy = (i * 89) % SCREEN_HEIGHT
            a = 100 + int(100 * math.sin(self.time * 2 + i))
            a = max(0, min(255, a))
            pygame.draw.circle(self.screen, (a, a, a), (sx, sy), 1)

        if self.prologue_page >= len(story.PROLOGUE_PAGES):
            return
        page = story.PROLOGUE_PAGES[self.prologue_page]

        # Заголовок
        title = self.font_prologue_title.render(page["title"], True, (220, 220, 240))
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 100)))

        # Текст
        y = 200
        for line in page["text"]:
            if line == "":
                y += 16
                continue
            surf = self.font_prologue.render(line, True, (200, 200, 220))
            self.screen.blit(surf, (SCREEN_WIDTH // 2 - surf.get_width() // 2, y))
            y += 38

        # Страница и подсказка
        page_info = self.font_tiny.render(
            f"{self.prologue_page + 1} / {len(story.PROLOGUE_PAGES)}",
            True, GRAY)
        self.screen.blit(page_info, page_info.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)))

        blink = abs(math.sin(self.time * 2))
        hint_color = (int(200 * blink), int(200 * blink), int(200 * blink))
        hint = self.font_small.render("ЛКМ / Enter — далее · Esc — пропустить",
                                      True, hint_color)
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

    def _draw_menu(self):
        BG_FUNCS[self.menu_bg](self.screen, self.time)
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 70))
        self.screen.blit(ov, (0, 0))
        for dx, dy in ((-2, -2), (2, -2), (-2, 2), (2, 2)):
            sh = self.font_title.render("SURVIVAL 2D", True, BLACK)
            self.screen.blit(sh, sh.get_rect(center=(SCREEN_WIDTH // 2 + dx, 80 + dy)))
        title = self.font_title.render("SURVIVAL 2D", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 80)))
        sub = self.font.render("Выживи в диком мире", True, (240, 240, 250))
        self.screen.blit(sub, sub.get_rect(center=(SCREEN_WIDTH // 2, 140)))
        heroine.draw_heroine(self.screen, SCREEN_WIDTH // 2 + 300, 460,
                             look=self.hero_look, phase=self.time * 3,
                             moving=True, facing=-1,
                             blink=(int(self.time * 2) % 5 == 0),
                             eye_dir=(-1, 0), scale=1.0)
        mouse = pygame.mouse.get_pos()
        for b in self.menu_buttons: b.draw(self.screen, mouse)
        for bg, rect in self.bg_buttons:
            sel = (bg == self.menu_bg)
            hov = rect.collidepoint(mouse)
            color = (100, 140, 90) if sel else ((80, 80, 100) if hov else DARK_GRAY)
            pygame.draw.rect(self.screen, color, rect, border_radius=6)
            pygame.draw.rect(self.screen, WHITE if sel else GRAY, rect, 2, border_radius=6)
            txt = self.font_small.render(BG_NAMES[bg], True, WHITE)
            self.screen.blit(txt, txt.get_rect(center=rect.center))
        hint = self.font_small.render(
            "WASD · E · I · C · F · B · M — карта · T — путешествия · Esc — пауза",
            True, (230, 230, 240))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

    def _draw_customize(self):
        BG_FUNCS[self.menu_bg](self.screen, self.time)
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 160))
        self.screen.blit(ov, (0, 0))
        t = self.font_big.render("Кастомизация персонажа", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 40)))
        heroine.draw_heroine(self.screen, SCREEN_WIDTH // 2, 500,
                             look=self.hero_look, phase=self.time * 3,
                             moving=True, facing=1,
                             blink=(int(self.time * 2) % 5 == 0),
                             eye_dir=(1, 0), scale=1.0)
        self.customize_rects = []
        mouse = pygame.mouse.get_pos()
        slot_w, slot_h, slot_x, slot_y, gap = 340, 40, 40, 100, 6
        for i, slot in enumerate(heroine.SLOT_ORDER):
            y = slot_y + i * (slot_h + gap)
            sel = (i == self.customize_selected)
            hov = (slot_x <= mouse[0] <= slot_x + slot_w and y <= mouse[1] <= y + slot_h)
            bg = (90, 120, 70) if sel else ((80, 80, 100) if hov else (50, 50, 60))
            rect = pygame.Rect(slot_x, y, slot_w, slot_h)
            pygame.draw.rect(self.screen, bg, rect, border_radius=6)
            pygame.draw.rect(self.screen, WHITE if sel else GRAY, rect, 2, border_radius=6)
            lab = self.font_small.render(heroine.SLOT_NAMES[slot], True, (200, 200, 220))
            self.screen.blit(lab, (slot_x + 10, y + 10))
            cur = self.hero_look[slot]
            name = heroine.SLOT_DISPLAY_NAMES[slot].get(cur, cur)
            ns = self.font.render(name, True, WHITE)
            self.screen.blit(ns, (slot_x + 130, y + 6))
            left_r = pygame.Rect(slot_x + slot_w - 80, y + 6, 32, 28)
            right_r = pygame.Rect(slot_x + slot_w - 40, y + 6, 32, 28)
            for r in (left_r, right_r):
                pygame.draw.rect(self.screen, DARK_GRAY, r, border_radius=4)
                pygame.draw.rect(self.screen, GRAY, r, 1, border_radius=4)
            pygame.draw.polygon(self.screen, WHITE,
                                [(left_r.x + 20, left_r.y + 8), (left_r.x + 10, left_r.y + 14),
                                 (left_r.x + 20, left_r.y + 20)])
            pygame.draw.polygon(self.screen, WHITE,
                                [(right_r.x + 12, right_r.y + 8), (right_r.x + 22, right_r.y + 14),
                                 (right_r.x + 12, right_r.y + 20)])
            self.customize_rects.append((("select", i), rect))
            self.customize_rects.append((("prev", i), left_r))
            self.customize_rects.append((("next", i), right_r))
        rand_r = pygame.Rect(SCREEN_WIDTH - 340, SCREEN_HEIGHT - 80, 150, 50)
        save_r = pygame.Rect(SCREEN_WIDTH - 180, SCREEN_HEIGHT - 80, 150, 50)
        for rect, text, color in ((rand_r, "Случайно", (90, 90, 130)),
                                  (save_r, "Готово", GREEN)):
            hov = rect.collidepoint(mouse)
            c = tuple(min(255, v + 20) for v in color) if hov else color
            pygame.draw.rect(self.screen, c, rect, border_radius=8)
            pygame.draw.rect(self.screen, WHITE, rect, 2, border_radius=8)
            s = self.font.render(text, True, WHITE)
            self.screen.blit(s, s.get_rect(center=rect.center))
        self.customize_rects.append((("random", None), rand_r))
        self.customize_rects.append((("save", None), save_r))
        hint = self.font_small.render("↑↓ — слот · ←→ — вариант · Esc — назад",
                                      True, (230, 230, 240))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30)))

    def _draw_settings(self):
        self.screen.fill((25, 30, 45))
        t = self.font_big.render("Настройки", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        self.music_slider.draw(self.screen)
        self.sfx_slider.draw(self.screen)
        cx = SCREEN_WIDTH // 2
        mouse = pygame.mouse.get_pos()
        size_rect = pygame.Rect(cx - 200, 300, 400, 46)
        size_name = WORLD_SIZE_NAMES.get(self.world_size, self.world_size)
        hovered = size_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, (80, 80, 100) if hovered else DARK_GRAY,
                         size_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, size_rect, 2, border_radius=8)
        txt = self.font.render(f"Размер мира: {size_name}", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=size_rect.center))
        self.size_btn = size_rect

        gfx_rect = pygame.Rect(cx - 200, 360, 400, 46)
        gfx_name = GFX_NAMES.get(self.graphics, self.graphics)
        hovered = gfx_rect.collidepoint(mouse)
        pygame.draw.rect(self.screen, (80, 80, 100) if hovered else DARK_GRAY,
                         gfx_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, gfx_rect, 2, border_radius=8)
        txt = self.font.render(f"Качество графики: {gfx_name}", True, WHITE)
        self.screen.blit(txt, txt.get_rect(center=gfx_rect.center))
        self.graphics_btn = gfx_rect

        self.fullscreen_btn.draw(self.screen, mouse)
        self.difficulty_btn.draw(self.screen, mouse)
        self.controls_btn.draw(self.screen, mouse)
        self.back_btn.draw(self.screen, mouse)

    def _draw_controls(self):
        self.screen.fill((25, 30, 45))
        t = self.font_big.render("Управление", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 100)))
        lines = ["WASD — движение", "E — взаимодействие / вход в палатку/шахту/грядку",
                 "I — инвентарь", "C — крафт", "B — строительство",
                 "F / ЛКМ — атака / использовать предмет", "M — карта локации",
                 "T — карта путешествий", "1..5 — слот быстрого доступа",
                 "Пробел — спать у кровати", "Esc — пауза/меню"]
        y = 160
        for line in lines:
            s = self.font.render(line, True, (220, 220, 230))
            self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += 36
        self.back_btn.draw(self.screen, pygame.mouse.get_pos())

    def _draw_load_menu(self):
        self.screen.fill((25, 30, 45))
        t = self.font_big.render("Загрузить игру", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 130)))
        if not self.save_list:
            s = self.font.render("Нет сохранений", True, GRAY)
            self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, 300)))
        else:
            for i, s in enumerate(self.save_list):
                rect = pygame.Rect(SCREEN_WIDTH // 2 - 250, 200 + i * 60, 500, 50)
                hov = rect.collidepoint(pygame.mouse.get_pos())
                pygame.draw.rect(self.screen, (80, 80, 100) if hov else DARK_GRAY,
                                 rect, border_radius=6)
                pygame.draw.rect(self.screen, WHITE, rect, 1, border_radius=6)
                txt = self.font.render(s["name"], True, WHITE)
                self.screen.blit(txt, txt.get_rect(center=rect.center))
        hint = self.font_small.render("Esc — назад", True, GRAY)
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))

    def _draw_play(self):
        if not self.world: return
        self.world.draw(self.screen, self.camera, self.daynight)
        for m in self.world.mobs:
            m.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)
        if self.graphics != "low":
            self.particles.draw(self.screen, self.camera)
        if self.graphics != "low" or self.world.is_mine:
            lights = []
            cam_x, cam_y = self.camera.offset
            px = self.player.x - cam_x
            py = self.player.y - self.player.h * 0.5 - cam_y
            r, g, b, a = self.daynight.get_darkness()
            if self.world.is_mine:
                a = 180
                r, g, b = 5, 5, 15
            base_radius = 120 + a * 0.7
            lights.append((px, py, base_radius, 1.0))
            for bld in self.world.buildings:
                if bld["kind"] == "campfire":
                    bx = bld["gx"] * TILE_SIZE + TILE_SIZE // 2 - cam_x
                    by = bld["gy"] * TILE_SIZE + TILE_SIZE // 2 - cam_y
                    pulse = 1.0 + 0.1 * math.sin(self.time * 6 + bx)
                    lights.append((bx, by, int(90 * pulse), 0.9))
            import light as _light
            mask = _light.make_light_mask(SCREEN_WIDTH, SCREEN_HEIGHT, (r, g, b), int(a), lights)
            self.screen.blit(mask, (0, 0))
        if self.graphics != "low" and not self.world.is_mine:
            self.daynight.draw_weather(self.screen)
        if self.player.hp < 30:
            pulse = abs(math.sin(self.time * 4))
            if pulse > 0.7:
                flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                flash.fill((150, 0, 0, int(40 * pulse)))
                self.screen.blit(flash, (0, 0))
        self._draw_status_vignette()
        if self.build_manager and not self.world.is_tent and not self.world.is_mine:
            self.build_manager.draw(self.screen, self.player, self.world, self.camera)
        self._draw_hud()
        if self.player.attacking_timer > 0:
            cx, cy = self.camera.apply((self.player.x, self.player.y - self.player.h // 2))
            arc_size = 60
            alpha = int(200 * self.player.attacking_timer / 0.25)
            arc = pygame.Surface((arc_size * 2, arc_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(arc, (250, 250, 100, alpha),
                               (arc_size, arc_size), arc_size, 3)
            self.screen.blit(arc, (cx - arc_size, cy - arc_size))
        from world import LOCATION_NAMES
        if self.world.is_tent: loc_name = "Палатка"
        elif self.world.is_mine: loc_name = "Шахта"
        else: loc_name = LOCATION_NAMES.get(self.current_location, self.current_location)
        ns = self.font.render(loc_name, True, WHITE)
        bg = pygame.Surface((ns.get_width() + 20, ns.get_height() + 8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        self.screen.blit(bg, (20, 120))
        self.screen.blit(ns, (30, 124))
        if self.border_target and not (self.world.is_tent or self.world.is_mine):
            target_name = LOCATION_NAMES.get(self.border_target, self.border_target)
            hint = f"→ {target_name} (идите к краю, чтобы перейти)"
            hs = self.font_small.render(hint, True, YELLOW)
            hb = pygame.Surface((hs.get_width() + 20, hs.get_height() + 10), pygame.SRCALPHA)
            hb.fill((0, 0, 0, 180))
            self.screen.blit(hb, (SCREEN_WIDTH // 2 - hs.get_width() // 2 - 10,
                                  SCREEN_HEIGHT - 130))
            self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2,
                                  SCREEN_HEIGHT - 125))

    def _draw_status_vignette(self):
        p = self.player
        def _make(color, strength):
            s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            band = int(120 * strength)
            col = (*color, int(140 * strength))
            s.fill((0, 0, 0, 0))
            pygame.draw.rect(s, col, (0, 0, SCREEN_WIDTH, band))
            pygame.draw.rect(s, col, (0, SCREEN_HEIGHT - band, SCREEN_WIDTH, band))
            pygame.draw.rect(s, col, (0, 0, band, SCREEN_HEIGHT))
            pygame.draw.rect(s, col, (SCREEN_WIDTH - band, 0, band, SCREEN_HEIGHT))
            return s
        overlay = None
        if p.hunger < 30:
            overlay = _blit_overlay(overlay, _make((200, 40, 40), (30 - p.hunger) / 30.0))
        if p.thirst < 30:
            overlay = _blit_overlay(overlay, _make((40, 80, 200), (30 - p.thirst) / 30.0))
        if p.temp < 20:
            overlay = _blit_overlay(overlay, _make((60, 120, 220), (20 - p.temp) / 20.0))
        if p.temp > 85:
            overlay = _blit_overlay(overlay, _make((230, 140, 60), (p.temp - 85) / 15.0))
        if overlay:
            self.screen.blit(overlay, (0, 0))

    def _draw_hud(self):
        p = self.player
        bx, by, bw, bh, gap = 20, 20, 220, 18, 6
        stats = [
            ("HP", p.vis_hp, p.max_hp, RED),
            ("Голод", p.vis_hunger, p.max_hunger, (200, 140, 40)),
            ("Жажда", p.vis_thirst, p.max_thirst, BLUE),
            ("Темп.", p.vis_temp, p.max_temp, (100, 200, 220)),
        ]
        for i, (label, val, mx, color) in enumerate(stats):
            y = by + i * (bh + gap)
            pygame.draw.rect(self.screen, (40, 40, 50), (bx, y, bw, bh), border_radius=4)
            w = int(bw * max(0, val) / mx)
            pulse = 0
            if label != "Темп." and val < mx * 0.25:
                pulse = int(abs(math.sin(self.time * 6)) * 4)
            pygame.draw.rect(self.screen, color, (bx, y, max(0, w - pulse), bh), border_radius=4)
            if pulse > 0:
                pygame.draw.rect(self.screen, WHITE, (bx + w - pulse, y, pulse, bh), border_radius=2)
            pygame.draw.rect(self.screen, WHITE, (bx, y, bw, bh), 1, border_radius=4)
            txt = self.font_tiny.render(f"{label}: {int(val)}/{int(mx)}", True, WHITE)
            self.screen.blit(txt, (bx + 4, y + 2))
        if p.equipped_armor:
            from settings import ARMOR
            bonus = ARMOR[p.equipped_armor]["hp_bonus"]
            armor_txt = f"🛡 {p.equipped_armor} (+{bonus})"
            s = self.font_tiny.render(armor_txt, True, (200, 220, 255))
            self.screen.blit(s, (bx, by + 4 * (bh + gap) + 4))
        info = (f"День {self.daynight.day_count} · {self.daynight.time_str} · "
                f"{self.daynight.season_name} "
                f"{ {'clear': '☀', 'rain': '☂', 'snow': '❄'}.get(self.daynight.weather, '') }")
        s = self.font.render(info, True, WHITE)
        bg = pygame.Surface((s.get_width() + 20, s.get_height() + 8), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 120))
        self.screen.blit(bg, (SCREEN_WIDTH - s.get_width() - 30, 20))
        self.screen.blit(s, (SCREEN_WIDTH - s.get_width() - 20, 24))
        self._draw_hotbar()
        if not (self.world.is_tent or self.world.is_mine):
            self._draw_minimap()
        hint = "WASD · E · F · I · C · B · M · T"
        hs = self.font_tiny.render(hint, True, (220, 220, 230))
        self.screen.blit(hs, (SCREEN_WIDTH // 2 - hs.get_width() // 2, SCREEN_HEIGHT - 27))

    def _draw_hotbar(self):
        n = len(self.player.hotbar)
        total = n * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD
        sx = (SCREEN_WIDTH - total) // 2
        y = SCREEN_HEIGHT - SLOT_SIZE - 50
        for i in range(n):
            idx = self.player.hotbar[i]
            rect = pygame.Rect(sx + i * (SLOT_SIZE + SLOT_PAD), y, SLOT_SIZE, SLOT_SIZE)
            sel = (i == self.player.hotbar_selected)
            pygame.draw.rect(self.screen, (60, 60, 70) if not sel else (100, 120, 80),
                             rect, border_radius=6)
            pygame.draw.rect(self.screen, WHITE if sel else GRAY, rect, 2, border_radius=6)
            slot = self.player.inventory.slots[idx] if idx < len(self.player.inventory.slots) else None
            if slot:
                icons.draw_item_icon(self.screen, slot.item_id, rect.inflate(-14, -14))
                if slot.count > 1:
                    t = self.font_tiny.render(str(slot.count), True, WHITE)
                    self.screen.blit(t, (rect.right - t.get_width() - 4, rect.bottom - 18))
            num = self.font_tiny.render(str(i + 1), True, (200, 200, 200))
            self.screen.blit(num, (rect.x + 3, rect.y + 2))

    def _draw_minimap(self):
        from settings import BIOME_COLORS
        size, margin = 160, 20
        x0 = SCREEN_WIDTH - size - margin
        y0 = SCREEN_HEIGHT - size - margin - 60
        pygame.draw.rect(self.screen, (20, 20, 30), (x0, y0, size, size), border_radius=6)
        pygame.draw.rect(self.screen, WHITE, (x0, y0, size, size), 1, border_radius=6)
        stx = max(1, self.world.map_w // size)
        sty = max(1, self.world.map_h // size)
        for py in range(size):
            gy = int(py * sty)
            if gy >= self.world.map_h: break
            for px in range(size):
                gx = int(px * stx)
                if gx >= self.world.map_w: break
                self.screen.set_at((x0 + px, y0 + py), BIOME_COLORS[self.world.tiles[gy][gx]])
        for b in self.world.buildings:
            bx = x0 + int(b["gx"] / self.world.map_w * size)
            by = y0 + int(b["gy"] / self.world.map_h * size)
            pygame.draw.rect(self.screen, (140, 90, 50), (bx, by, 2, 2))
        for m in self.world.mobs:
            mx_ = x0 + int(m.x / (self.world.map_w * TILE_SIZE) * size)
            my_ = y0 + int(m.y / (self.world.map_h * TILE_SIZE) * size)
            from entities import Monster
            color = (220, 60, 60) if isinstance(m, Monster) else (230, 220, 90)
            pygame.draw.circle(self.screen, color, (mx_, my_), 2)
        px = x0 + int(self.player.x / (self.world.map_w * TILE_SIZE) * size)
        py = y0 + int(self.player.y / (self.world.map_h * TILE_SIZE) * size)
        pygame.draw.circle(self.screen, RED, (px, py), 3)
        pygame.draw.circle(self.screen, WHITE, (px, py), 4, 1)
        lbl = self.font_tiny.render("M · T", True, WHITE)
        self.screen.blit(lbl, (x0 + 4, y0 + 2))

    def _draw_big_map(self):
        from settings import BIOME_COLORS
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        self.screen.blit(ov, (0, 0))
        t = self.font_big.render("Карта локации", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 40)))
        size = min(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 160)
        x0 = (SCREEN_WIDTH - size) // 2
        y0 = 100
        pygame.draw.rect(self.screen, (20, 20, 30), (x0, y0, size, size), border_radius=6)
        pygame.draw.rect(self.screen, WHITE, (x0, y0, size, size), 2, border_radius=6)
        stx = max(1, self.world.map_w // size)
        sty = max(1, self.world.map_h // size)
        for py in range(size):
            gy = int(py * sty)
            if gy >= self.world.map_h: break
            for px in range(size):
                gx = int(px * stx)
                if gx >= self.world.map_w: break
                self.screen.set_at((x0 + px, y0 + py), BIOME_COLORS[self.world.tiles[gy][gx]])
        for b in self.world.buildings:
            bx = x0 + int(b["gx"] / self.world.map_w * size)
            by = y0 + int(b["gy"] / self.world.map_h * size)
            pygame.draw.rect(self.screen, (140, 90, 50), (bx - 1, by - 1, 3, 3))
        px = x0 + int(self.player.x / (self.world.map_w * TILE_SIZE) * size)
        py = y0 + int(self.player.y / (self.world.map_h * TILE_SIZE) * size)
        pygame.draw.circle(self.screen, RED, (px, py), 4)
        pygame.draw.circle(self.screen, WHITE, (px, py), 6, 1)
        hint = self.font_small.render("M / Esc — закрыть карту", True, (220, 220, 230))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))

    def _draw_travel_map(self):
        from world import LOCATION_NAMES, LOCATION_NEIGHBORS
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 210))
        self.screen.blit(ov, (0, 0))
        title = self.font_big.render("Карта путешествий", True, WHITE)
        self.screen.blit(title, title.get_rect(center=(SCREEN_WIDTH // 2, 50)))
        layout = {
            "mountains": (SCREEN_WIDTH // 2, 200),
            "sea":       (SCREEN_WIDTH // 2 - 350, 400),
            "village":   (SCREEN_WIDTH // 2, 400),
            "city":      (SCREEN_WIDTH // 2 + 350, 400),
        }
        colors = {"village": (100, 160, 90), "city": (110, 110, 140),
                  "mountains": (150, 150, 150), "sea": (70, 140, 200)}
        for loc, neighbors in LOCATION_NEIGHBORS.items():
            if loc not in layout: continue
            x1, y1 = layout[loc]
            for n in neighbors:
                if n not in layout: continue
                x2, y2 = layout[n]
                if loc < n:
                    pygame.draw.line(self.screen, (200, 200, 200), (x1, y1), (x2, y2), 3)
        mouse = pygame.mouse.get_pos()
        for loc, (x, y) in layout.items():
            rect = pygame.Rect(x - 90, y - 50, 180, 100)
            selected = (loc == self.current_location)
            hovered = rect.collidepoint(mouse)
            color = colors.get(loc, GRAY)
            if selected:
                color = tuple(min(255, c + 60) for c in color)
            elif hovered:
                color = tuple(min(255, c + 30) for c in color)
            pygame.draw.rect(self.screen, color, rect, border_radius=12)
            pygame.draw.rect(self.screen, WHITE if selected else GRAY,
                             rect, 3 if selected else 2, border_radius=12)
            name = LOCATION_NAMES.get(loc, loc)
            txt = self.font_big.render(name, True, WHITE)
            self.screen.blit(txt, txt.get_rect(center=(x, y - 10)))
            if selected:
                sub = self.font_small.render("(вы здесь)", True, YELLOW)
                self.screen.blit(sub, sub.get_rect(center=(x, y + 25)))
            elif loc in LOCATION_NEIGHBORS.get(self.current_location, []):
                sub = self.font_small.render("→ доступно", True, (200, 220, 255))
                self.screen.blit(sub, sub.get_rect(center=(x, y + 25)))
            else:
                sub = self.font_small.render("(недоступно)", True, GRAY)
                self.screen.blit(sub, sub.get_rect(center=(x, y + 25)))
        hint = self.font_small.render(
            "T / Esc — закрыть · клик по доступной локации — переход",
            True, (220, 220, 230))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))
        if self.travel_click_pending:
            self.travel_click_pending = False
            for loc, (x, y) in layout.items():
                rect = pygame.Rect(x - 90, y - 50, 180, 100)
                if rect.collidepoint(mouse) and loc != self.current_location:
                    if loc in LOCATION_NEIGHBORS.get(self.current_location, []):
                        self.travel_to(loc)
                        return

    def _draw_pause(self):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        self.screen.blit(ov, (0, 0))
        t = self.font_big.render("Пауза", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 220)))
        y = 320
        for line in ["Esc — продолжить", "S — сохранить игру", "Q — выйти в меню"]:
            s = self.font.render(line, True, (220, 220, 230))
            self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, y)))
            y += 50

    def _draw_inventory_overlay(self):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        self.screen.blit(ov, (0, 0))
        t = self.font_big.render("Инвентарь", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 50)))
        inv = self.player.inventory
        w, h = inv.grid_size()
        origin = ((SCREEN_WIDTH - w) // 2, 120)
        self.inv_origin = origin
        inv.draw(self.screen, origin)
        hint = self.font_small.render(
            "ЛКМ — взять · ПКМ — выбросить половину · I/Esc — закрыть",
            True, (200, 200, 220))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, origin[1] + h + 30)))

    def _draw_craft_overlay(self):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 170))
        self.screen.blit(ov, (0, 0))
        t = self.font_big.render("Крафт", True, WHITE)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 50)))
        from inventory import Crafting
        origin = (SCREEN_WIDTH // 2 - 320, 120)
        self.craft_rects = Crafting.draw(self.screen, self.player.inventory, origin,
                                         self.craft_selected)
        rec = RECIPES[self.craft_selected]
        px, py = SCREEN_WIDTH // 2 + 140, 120
        pygame.draw.rect(self.screen, (30, 40, 30), (px, py, 300, 400), border_radius=8)
        pygame.draw.rect(self.screen, WHITE, (px, py, 300, 400), 2, border_radius=8)
        self.screen.blit(self.font.render(rec["name"], True, WHITE), (px + 15, py + 15))
        y = py + 70
        self.screen.blit(self.font_small.render("Требуется:", True, YELLOW), (px + 15, y))
        y += 30
        ok_all = True
        for k, v in rec["requires"].items():
            have = self.player.inventory.count_item(k)
            ok = have >= v
            if not ok: ok_all = False
            self.screen.blit(self.font_small.render(f"{ITEMS[k][0]}: {have}/{v}",
                                                    True, GREEN if ok else RED),
                             (px + 25, y))
            y += 26
        y += 20
        self.screen.blit(self.font_small.render(
            f"Результат: {ITEMS[rec['result']][0]} ×{rec['count']}", True, WHITE),
            (px + 15, y))
        y += 60
        btn_text = "Создать (Enter)" if ok_all else "Не хватает ресурсов"
        btn_color = GREEN if ok_all else (100, 60, 60)
        btn_rect = pygame.Rect(px + 40, y, 220, 50)
        pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, btn_rect, 2, border_radius=8)
        btxt = self.font_small.render(btn_text, True, WHITE)
        self.screen.blit(btxt, btxt.get_rect(center=btn_rect.center))
        hint = self.font_small.render(
            "↑↓ или клик — выбрать · Enter — создать · C/Esc — закрыть",
            True, (200, 200, 220))
        self.screen.blit(hint, hint.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 40)))

    def _draw_game_over(self):
        ov = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        ov.fill((0, 0, 0, 200))
        self.screen.blit(ov, (0, 0))
        t = self.font_title.render("ВЫ ПОГИБЛИ", True, RED)
        self.screen.blit(t, t.get_rect(center=(SCREEN_WIDTH // 2, 260)))
        s = self.font.render(f"Продержались дней: {self.daynight.day_count}", True, WHITE)
        self.screen.blit(s, s.get_rect(center=(SCREEN_WIDTH // 2, 340)))
        self.gameover_btn.draw(self.screen, pygame.mouse.get_pos())