"""world.py — локации, шахты, грядки (фермерство)."""
import math
import random
import pygame
from settings import (
    TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT,
    BIOME_WATER, BIOME_BEACH, BIOME_GRASS, BIOME_FOREST, BIOME_MOUNTAIN, BIOME_SNOW,
    BIOME_COLORS, SEASON_SPRING, SEASON_AUTUMN, SEASON_WINTER,
    DARK_GREEN, GRAY, DARK_BROWN, RED, YELLOW, ORANGE, WHITE, BLACK, ITEMS, CROPS,
    WORLD_SIZES, TENT_INTERIOR_W, TENT_INTERIOR_H,
    MINE_INTERIOR_W, MINE_INTERIOR_H,
)

LOCATION_VILLAGE = "village"
LOCATION_CITY = "city"
LOCATION_MOUNTAINS = "mountains"
LOCATION_SEA = "sea"

LOCATION_NAMES = {
    LOCATION_VILLAGE: "Деревня",
    LOCATION_CITY: "Город",
    LOCATION_MOUNTAINS: "Горы",
    LOCATION_SEA: "Море",
}

LOCATION_NEIGHBORS = {
    LOCATION_VILLAGE: [LOCATION_CITY, LOCATION_MOUNTAINS, LOCATION_SEA],
    LOCATION_CITY: [LOCATION_VILLAGE, LOCATION_MOUNTAINS],
    LOCATION_MOUNTAINS: [LOCATION_VILLAGE, LOCATION_CITY],
    LOCATION_SEA: [LOCATION_VILLAGE],
}

BORDER_LEFT = "left"
BORDER_RIGHT = "right"
BORDER_TOP = "top"
BORDER_BOTTOM = "bottom"

BORDER_TO_LOCATION = {
    LOCATION_VILLAGE: {BORDER_LEFT: LOCATION_SEA, BORDER_RIGHT: LOCATION_CITY, BORDER_TOP: LOCATION_MOUNTAINS},
    LOCATION_CITY: {BORDER_LEFT: LOCATION_VILLAGE, BORDER_TOP: LOCATION_MOUNTAINS},
    LOCATION_MOUNTAINS: {BORDER_BOTTOM: LOCATION_VILLAGE, BORDER_RIGHT: LOCATION_CITY},
    LOCATION_SEA: {BORDER_RIGHT: LOCATION_VILLAGE},
}

BORDER_NAMES = {BORDER_LEFT: "влево", BORDER_RIGHT: "вправо", BORDER_TOP: "вверх", BORDER_BOTTOM: "вниз"}

BERRY_REGROW_TIME = 60.0
FALL_ANIM_TIME = 0.7


class PerlinNoise:
    def __init__(self, seed=None):
        rnd = random.Random(seed)
        self.perm = list(range(256))
        rnd.shuffle(self.perm)
        self.perm += self.perm

    @staticmethod
    def _fade(t): return t * t * t * (t * (t * 6 - 15) + 10)
    @staticmethod
    def _lerp(a, b, t): return a + t * (b - a)

    def _grad(self, h, x, y):
        v = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        gx, gy = v[h % 8]
        return gx * x + gy * y

    def noise2(self, x, y):
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf, yf = x - math.floor(x), y - math.floor(y)
        u, v = self._fade(xf), self._fade(yf)
        aa = self.perm[self.perm[xi] + yi]
        ab = self.perm[self.perm[xi] + yi + 1]
        ba = self.perm[self.perm[xi + 1] + yi]
        bb = self.perm[self.perm[xi + 1] + yi + 1]
        x1 = self._lerp(self._grad(aa, xf, yf), self._grad(ba, xf - 1, yf), u)
        x2 = self._lerp(self._grad(ab, xf, yf - 1), self._grad(bb, xf - 1, yf - 1), u)
        return self._lerp(x1, x2, v)

    def octaves(self, x, y, octaves=4, persistence=0.5):
        total = 0.0
        freq, amp, mx = 1.0, 1.0, 0.0
        for _ in range(octaves):
            total += self.noise2(x * freq, y * freq) * amp
            mx += amp
            amp *= persistence
            freq *= 2.0
        return total / mx if mx else 0.0


class World:
    def __init__(self, seed=None, location=LOCATION_VILLAGE,
                 size_key="medium", is_tent=False, is_mine=False):
        self.is_tent = is_tent
        self.is_mine = is_mine
        self.size_key = size_key
        if is_tent:
            self.map_w = TENT_INTERIOR_W
            self.map_h = TENT_INTERIOR_H
        elif is_mine:
            self.map_w = MINE_INTERIOR_W
            self.map_h = MINE_INTERIOR_H
        else:
            self.map_w, self.map_h = WORLD_SIZES.get(size_key, (200, 200))

        self.location = location
        self.seed = seed if seed is not None else random.randint(0, 10**9)
        self.rng = random.Random(self.seed)
        self.noise = PerlinNoise(self.seed)
        self.tiles = [[BIOME_GRASS for _ in range(self.map_w)] for _ in range(self.map_h)]
        self.objects = []
        self.buildings = []
        self.mobs = []
        self.season = SEASON_SPRING
        self.falling = []
        self.generate()

    def generate(self):
        if self.is_tent:
            self._generate_tent_interior()
            return
        if self.is_mine:
            self._generate_mine_interior()
            return
        for gy in range(self.map_h):
            for gx in range(self.map_w):
                if self.location == LOCATION_SEA:
                    tile = self._sea_tile(gx, gy)
                elif self.location == LOCATION_MOUNTAINS:
                    tile = self._mountain_tile(gx, gy)
                elif self.location == LOCATION_CITY:
                    tile = self._city_tile(gx, gy)
                else:
                    tile = self._village_tile(gx, gy)
                self.tiles[gy][gx] = tile
        self._smooth_tiles(1)
        self._spawn_resources()
        self._place_mine_entrances()

    def _place_mine_entrances(self):
        count = 0
        if self.location == LOCATION_MOUNTAINS:
            count = 4
        elif self.location == LOCATION_VILLAGE:
            count = 1
        elif self.location == LOCATION_SEA:
            count = 1
        for _ in range(count * 30):
            if count <= 0: break
            gx = self.rng.randint(5, self.map_w - 5)
            gy = self.rng.randint(5, self.map_h - 5)
            t = self.tiles[gy][gx]
            if t in (BIOME_MOUNTAIN, BIOME_BEACH):
                px = gx * TILE_SIZE + TILE_SIZE // 2
                py = gy * TILE_SIZE + TILE_SIZE // 2
                too_close = False
                for o in self.objects:
                    if o.get("kind") == "mine_entrance":
                        if (o["x"] - px) ** 2 + (o["y"] - py) ** 2 < 200 ** 2:
                            too_close = True
                            break
                if too_close: continue
                self.objects.append({"kind": "mine_entrance", "x": px, "y": py})
                count -= 1

    def _generate_tent_interior(self):
        for gy in range(self.map_h):
            for gx in range(self.map_w):
                if gx == 0 or gy == 0 or gx == self.map_w - 1 or gy == self.map_h - 1:
                    self.tiles[gy][gx] = BIOME_MOUNTAIN
                else:
                    self.tiles[gy][gx] = BIOME_GRASS
        mid_x = self.map_w // 2
        mid_y = self.map_h // 2
        self.buildings.append({"kind": "bed", "gx": mid_x, "gy": mid_y})
        self.buildings.append({"kind": "chest", "gx": mid_x + 2, "gy": mid_y})
        self.buildings.append({"kind": "campfire", "gx": mid_x - 2, "gy": mid_y})
        self.buildings.append({"kind": "door", "gx": mid_x, "gy": self.map_h - 1,
                               "opened": False, "is_tent_exit": True})

    def _generate_mine_interior(self):
        for gy in range(self.map_h):
            for gx in range(self.map_w):
                if gx == 0 or gy == 0 or gx == self.map_w - 1 or gy == self.map_h - 1:
                    self.tiles[gy][gx] = BIOME_MOUNTAIN
                else:
                    self.tiles[gy][gx] = BIOME_BEACH
        mid_x = self.map_w // 2
        self.buildings.append({"kind": "door", "gx": mid_x, "gy": self.map_h - 1,
                               "opened": False, "is_mine_exit": True})
        for gy in range(self.map_h):
            for gx in range(self.map_w):
                if self.tiles[gy][gx] == BIOME_MOUNTAIN: continue
                adjacent_wall = False
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        if dx == 0 and dy == 0: continue
                        nx, ny = gx + dx, gy + dy
                        if 0 <= nx < self.map_w and 0 <= ny < self.map_h:
                            if self.tiles[ny][nx] == BIOME_MOUNTAIN:
                                adjacent_wall = True; break
                    if adjacent_wall: break
                if not adjacent_wall: continue
                r = self.rng.random()
                px = gx * TILE_SIZE + TILE_SIZE // 2
                py = gy * TILE_SIZE + TILE_SIZE // 2
                if r < 0.20:
                    self.objects.append({"kind": "rock", "x": px, "y": py, "hp": 120})
                elif r < 0.30:
                    self.objects.append({"kind": "coal_ore", "x": px, "y": py, "hp": 150})
                elif r < 0.42:
                    self.objects.append({"kind": "iron_ore_rock", "x": px, "y": py, "hp": 180})
                elif r < 0.46:
                    self.objects.append({"kind": "gold_ore_rock", "x": px, "y": py, "hp": 220})
                elif r < 0.48:
                    self.objects.append({"kind": "diamond_ore_rock", "x": px, "y": py, "hp": 300})
        for _ in range(4):
            gx = self.rng.randint(2, self.map_w - 3)
            gy = self.rng.randint(2, self.map_h - 3)
            if self.tiles[gy][gx] == BIOME_BEACH:
                self.buildings.append({"kind": "campfire", "gx": gx, "gy": gy})

    def _village_tile(self, gx, gy):
        nx, ny = gx / 40.0, gy / 40.0
        e = (self.noise.octaves(nx, ny, 4, 0.55) + 1) / 2
        m = (self.noise.octaves(nx + 100, ny + 100, 3, 0.5) + 1) / 2
        if e < 0.30: return BIOME_WATER
        if e < 0.36: return BIOME_BEACH
        if e < 0.62: return BIOME_FOREST if m > 0.55 else BIOME_GRASS
        if e < 0.78: return BIOME_MOUNTAIN
        return BIOME_SNOW

    def _mountain_tile(self, gx, gy):
        nx, ny = gx / 30.0, gy / 30.0
        e = (self.noise.octaves(nx, ny, 5, 0.6) + 1) / 2
        if e < 0.35: return BIOME_GRASS
        if e < 0.55: return BIOME_MOUNTAIN
        if e < 0.78: return BIOME_MOUNTAIN
        return BIOME_SNOW

    def _sea_tile(self, gx, gy):
        nx, ny = gx / 25.0, gy / 25.0
        e = (self.noise.octaves(nx, ny, 4, 0.5) + 1) / 2
        if e < 0.55: return BIOME_WATER
        if e < 0.75: return BIOME_BEACH
        if e < 0.85: return BIOME_GRASS
        return BIOME_FOREST

    def _city_tile(self, gx, gy):
        if gx % 8 == 0 or gy % 8 == 0:
            return BIOME_BEACH
        n = self.noise.noise2(gx / 20.0, gy / 20.0)
        if n > 0.4: return BIOME_MOUNTAIN
        if n > 0.1: return BIOME_BEACH
        return BIOME_GRASS

    def _smooth_tiles(self, passes=1):
        for _ in range(passes):
            new = [row[:] for row in self.tiles]
            for gy in range(1, self.map_h - 1):
                for gx in range(1, self.map_w - 1):
                    counts = {}
                    for dy in (-1, 0, 1):
                        for dx in (-1, 0, 1):
                            t = self.tiles[gy + dy][gx + dx]
                            counts[t] = counts.get(t, 0) + 1
                    best = max(counts.items(), key=lambda kv: kv[1])[0]
                    if counts[best] >= 6:
                        new[gy][gx] = best
            self.tiles = new

    def _spawn_resources(self):
        loc = self.location
        for gy in range(self.map_h):
            for gx in range(self.map_w):
                tile = self.tiles[gy][gx]
                px = gx * TILE_SIZE + TILE_SIZE // 2
                py = gy * TILE_SIZE + TILE_SIZE // 2
                if loc == LOCATION_SEA:
                    if tile == BIOME_BEACH and self.rng.random() < 0.10:
                        self.objects.append({"kind": "bush", "x": px, "y": py,
                                             "has_berries": True, "berry_timer": 0.0, "hp": 40})
                    elif tile == BIOME_GRASS and self.rng.random() < 0.08:
                        self.objects.append({"kind": "tree", "x": px, "y": py, "hp": 100})
                    elif tile == BIOME_BEACH and self.rng.random() < 0.03:
                        self.objects.append({"kind": "rock", "x": px, "y": py, "hp": 120})
                elif loc == LOCATION_MOUNTAINS:
                    if tile == BIOME_MOUNTAIN and self.rng.random() < 0.35:
                        self.objects.append({"kind": "rock", "x": px, "y": py, "hp": 120})
                    elif tile == BIOME_GRASS and self.rng.random() < 0.10:
                        self.objects.append({"kind": "tree", "x": px, "y": py, "hp": 100})
                elif loc == LOCATION_CITY:
                    if tile == BIOME_GRASS and self.rng.random() < 0.05:
                        self.objects.append({"kind": "bush", "x": px, "y": py,
                                             "has_berries": True, "berry_timer": 0.0, "hp": 40})
                    elif tile == BIOME_MOUNTAIN and self.rng.random() < 0.15:
                        self.objects.append({"kind": "rock", "x": px, "y": py, "hp": 120})
                else:
                    if tile == BIOME_FOREST:
                        if self.rng.random() < 0.22:
                            self.objects.append({"kind": "tree", "x": px, "y": py, "hp": 100})
                        elif self.rng.random() < 0.05:
                            self.objects.append({"kind": "bush", "x": px, "y": py,
                                                 "has_berries": True, "berry_timer": 0.0, "hp": 40})
                    elif tile == BIOME_GRASS:
                        if self.rng.random() < 0.04:
                            self.objects.append({"kind": "tree", "x": px, "y": py, "hp": 100})
                        elif self.rng.random() < 0.06:
                            self.objects.append({"kind": "bush", "x": px, "y": py,
                                                 "has_berries": True, "berry_timer": 0.0, "hp": 40})
                    elif tile == BIOME_MOUNTAIN:
                        if self.rng.random() < 0.18:
                            self.objects.append({"kind": "rock", "x": px, "y": py, "hp": 120})
                    elif tile == BIOME_BEACH:
                        if self.rng.random() < 0.03:
                            self.objects.append({"kind": "rock", "x": px, "y": py, "hp": 120})

    def find_spawn(self):
        if self.is_tent or self.is_mine:
            return (self.map_w // 2 * TILE_SIZE, (self.map_h - 2) * TILE_SIZE)
        cx, cy = self.map_w // 2, self.map_h // 2
        for r in range(0, 100):
            for gy in range(cy - r, cy + r + 1):
                for gx in range(cx - r, cx + r + 1):
                    if 0 <= gx < self.map_w and 0 <= gy < self.map_h:
                        if self.tiles[gy][gx] in (BIOME_GRASS, BIOME_BEACH, BIOME_FOREST):
                            return gx * TILE_SIZE + TILE_SIZE // 2, gy * TILE_SIZE + TILE_SIZE // 2
        return cx * TILE_SIZE, cy * TILE_SIZE

    def tile_at(self, gx, gy):
        if 0 <= gx < self.map_w and 0 <= gy < self.map_h:
            return self.tiles[gy][gx]
        return BIOME_WATER

    def tile_at_pixel(self, px, py):
        return self.tile_at(int(px // TILE_SIZE), int(py // TILE_SIZE))

    def can_walk(self, x, y, w, h):
        rect = pygame.Rect(int(x - w // 2), int(y - h), w, h)
        gx1 = rect.left // TILE_SIZE
        gy1 = rect.top // TILE_SIZE
        gx2 = (rect.right - 1) // TILE_SIZE
        gy2 = (rect.bottom - 1) // TILE_SIZE
        for gy in range(gy1, gy2 + 1):
            for gx in range(gx1, gx2 + 1):
                if self.tile_at(gx, gy) in (BIOME_WATER, BIOME_SNOW):
                    return False
        for b in self.buildings:
            if b["kind"] == "wall":
                br = pygame.Rect(b["gx"] * TILE_SIZE, b["gy"] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(br): return False
            elif b["kind"] == "door" and not b.get("opened", False):
                br = pygame.Rect(b["gx"] * TILE_SIZE, b["gy"] * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                if rect.colliderect(br): return False
        for o in self.objects:
            if o["kind"] in ("tree", "rock", "bush", "coal_ore", "iron_ore_rock",
                             "gold_ore_rock", "diamond_ore_rock"):
                orect = pygame.Rect(o["x"] - 10, o["y"] - 20, 20, 20)
                if rect.colliderect(orect): return False
        return True

    def find_interactable(self, x, y, radius):
        best, best_d = None, radius * radius
        for o in self.objects:
            d = (o["x"] - x) ** 2 + (o["y"] - y) ** 2
            if d < best_d: best_d, best = d, o
        for b in self.buildings:
            bx = b["gx"] * TILE_SIZE + TILE_SIZE // 2
            by = b["gy"] * TILE_SIZE + TILE_SIZE // 2
            d = (bx - x) ** 2 + (by - y) ** 2
            if d < best_d: best_d, best = d, b
        if best is None:
            gx, gy = int(x // TILE_SIZE), int(y // TILE_SIZE)
            for dy in (-2, -1, 0, 1, 2):
                for dx in (-2, -1, 0, 1, 2):
                    if self.tile_at(gx + dx, gy + dy) == BIOME_WATER:
                        return {"kind": "water"}
        return best

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    def start_fall_anim(self, obj, direction=1):
        self.falling.append({
            "x": obj["x"], "y": obj["y"], "kind": obj["kind"],
            "timer": FALL_ANIM_TIME, "direction": direction,
        })
        self.remove_object(obj)

    def damage_enemies_near(self, x, y, radius, dmg):
        r2 = radius * radius
        for m in self.mobs:
            if getattr(m, "dead", False): continue
            if (m.x - x) ** 2 + (m.y - y) ** 2 < r2:
                m.take_damage(dmg)

    def has_campfire_near(self, x, y, radius):
        r2 = radius * radius
        for b in self.buildings:
            if b["kind"] == "campfire":
                bx = b["gx"] * TILE_SIZE + TILE_SIZE // 2
                by = b["gy"] * TILE_SIZE + TILE_SIZE // 2
                if (bx - x) ** 2 + (by - y) ** 2 < r2: return True
        return False

    def inside_house(self, x, y):
        gx, gy = int(x // TILE_SIZE), int(y // TILE_SIZE)
        walls = 0
        for dy in (-2, -1, 0, 1, 2):
            for dx in (-2, -1, 0, 1, 2):
                for b in self.buildings:
                    if b["kind"] == "wall" and b["gx"] == gx + dx and b["gy"] == gy + dy:
                        walls += 1
        return walls >= 6

    def toggle_door(self, door):
        door["opened"] = not door.get("opened", False)

    def can_place(self, gx, gy, kind):
        if self.tile_at(gx, gy) in (BIOME_WATER, BIOME_SNOW):
            return False
        for b in self.buildings:
            if b["gx"] == gx and b["gy"] == gy: return False
        return True

    def place_building(self, gx, gy, kind):
        if not self.can_place(gx, gy, kind): return False
        b = {"kind": kind, "gx": gx, "gy": gy}
        if kind == "door": b["opened"] = False
        if kind == "farm_plot":
            b["state"] = "empty"
            b["crop"] = None
            b["growth"] = 0.0
        self.buildings.append(b)
        return True

    def apply_season(self, season, initial=False):
        self.season = season

    def border_at(self, x, y):
        if self.is_tent or self.is_mine:
            return None
        if x < TILE_SIZE * 2: return BORDER_LEFT
        if x > (self.map_w - 2) * TILE_SIZE: return BORDER_RIGHT
        if y < TILE_SIZE * 2: return BORDER_TOP
        if y > (self.map_h - 2) * TILE_SIZE: return BORDER_BOTTOM
        return None

    def get_border_target(self, side):
        if self.is_tent or self.is_mine:
            return None
        return BORDER_TO_LOCATION.get(self.location, {}).get(side)

    def update(self, dt, player, daynight):
        if self.is_tent or self.is_mine:
            return

        # Рост урожая на грядках
        for b in self.buildings:
            if b["kind"] == "farm_plot" and b.get("state") == "growing":
                b["growth"] = b.get("growth", 0.0) + dt
                crop_info = CROPS.get(b.get("crop"))
                if crop_info and b["growth"] >= crop_info["grow_time"]:
                    b["state"] = "ripe"

        for o in self.objects:
            if o["kind"] == "bush" and not o.get("has_berries", True):
                o["berry_timer"] = o.get("berry_timer", 0.0) + dt
                if o["berry_timer"] >= BERRY_REGROW_TIME:
                    o["has_berries"] = True
                    o["berry_timer"] = 0.0

        for f in list(self.falling):
            f["timer"] -= dt
            if f["timer"] <= 0:
                self.falling.remove(f)

        if daynight.is_night and len(self.mobs) < 14:
            if self.rng.random() < 0.006:
                self._spawn_monster(player)
        elif daynight.is_day and len(self.mobs) < 18:
            if self.rng.random() < 0.020:
                self._spawn_animal(player)

        for m in list(self.mobs):
            m.update(dt, self, player, daynight)
            if getattr(m, "dead", False):
                drop = getattr(m, "drop", None)
                if drop:
                    item_id, count = drop if isinstance(drop, tuple) else (drop, 1)
                    self.objects.append({"kind": "pickup", "x": m.x, "y": m.y,
                                         "item_id": item_id, "count": count, "hp": 1})
                self.mobs.remove(m)

    def _spawn_monster(self, player):
        from entities import Monster
        for _ in range(20):
            ang = self.rng.uniform(0, math.tau)
            dist = self.rng.uniform(500, 900)
            x, y = player.x + math.cos(ang) * dist, player.y + math.sin(ang) * dist
            if self.tile_at_pixel(x, y) in (BIOME_GRASS, BIOME_FOREST, BIOME_BEACH):
                self.mobs.append(Monster(x, y, self.rng))
                return

    def _spawn_animal(self, player):
        from entities import Animal
        kind_pool = {
            LOCATION_VILLAGE: ["cow", "cow", "sheep", "sheep", "chicken", "chicken", "deer", "rabbit"],
            LOCATION_CITY: ["chicken", "chicken", "rabbit"],
            LOCATION_MOUNTAINS: ["deer", "deer", "rabbit", "rabbit"],
            LOCATION_SEA: ["chicken", "chicken", "cow"],
        }.get(self.location, ["rabbit"])
        for _ in range(20):
            ang = self.rng.uniform(0, math.tau)
            dist = self.rng.uniform(400, 800)
            x, y = player.x + math.cos(ang) * dist, player.y + math.sin(ang) * dist
            if self.tile_at_pixel(x, y) in (BIOME_GRASS, BIOME_FOREST, BIOME_BEACH):
                kind = self.rng.choice(kind_pool)
                self.mobs.append(Animal(x, y, self.rng, kind=kind))
                return

    # ---------- Отрисовка ----------
    def draw(self, screen, camera, daynight):
        cam_x, cam_y = camera.offset
        gx0 = max(0, int(cam_x // TILE_SIZE) - 1)
        gy0 = max(0, int(cam_y // TILE_SIZE) - 1)
        gx1 = min(self.map_w, int((cam_x + SCREEN_WIDTH) // TILE_SIZE) + 2)
        gy1 = min(self.map_h, int((cam_y + SCREEN_HEIGHT) // TILE_SIZE) + 2)

        t_now = pygame.time.get_ticks() / 1000.0

        for gy in range(gy0, gy1):
            for gx in range(gx0, gx1):
                color = self._tile_color(self.tiles[gy][gx], gx, gy)
                sx, sy = gx * TILE_SIZE - cam_x, gy * TILE_SIZE - cam_y
                pygame.draw.rect(screen, color, (sx, sy, TILE_SIZE + 1, TILE_SIZE + 1))

        for gy in range(gy0, gy1):
            for gx in range(gx0, gx1):
                t = self.tiles[gy][gx]
                sx, sy = gx * TILE_SIZE - cam_x, gy * TILE_SIZE - cam_y
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                    nt = self.tile_at(gx + dx, gy + dy)
                    if nt == t: continue
                    ncolor = self._tile_color(nt, gx + dx, gy + dy)
                    seed = ((gx * 73856093) ^ (gy * 19349663) ^ (dx * 83492791)) & 0xFFFF
                    rnd = (seed % 100) / 100.0
                    if dx == -1:
                        bx, by = sx + 2, sy + TILE_SIZE * rnd
                        pygame.draw.circle(screen, ncolor, (int(bx), int(by)), 8)
                        pygame.draw.circle(screen, ncolor, (int(bx - 3), int(by + 6)), 6)
                    elif dx == 1:
                        bx, by = sx + TILE_SIZE - 2, sy + TILE_SIZE * (1 - rnd)
                        pygame.draw.circle(screen, ncolor, (int(bx), int(by)), 8)
                        pygame.draw.circle(screen, ncolor, (int(bx + 3), int(by + 6)), 6)
                    elif dy == -1:
                        bx, by = sx + TILE_SIZE * rnd, sy + 2
                        pygame.draw.circle(screen, ncolor, (int(bx), int(by)), 8)
                        pygame.draw.circle(screen, ncolor, (int(bx + 6), int(by - 3)), 6)
                    elif dy == 1:
                        bx, by = sx + TILE_SIZE * (1 - rnd), sy + TILE_SIZE - 2
                        pygame.draw.circle(screen, ncolor, (int(bx), int(by)), 8)
                        pygame.draw.circle(screen, ncolor, (int(bx + 6), int(by + 3)), 6)

        for gy in range(gy0, gy1):
            for gx in range(gx0, gx1):
                if self.tiles[gy][gx] != BIOME_WATER: continue
                sx = gx * TILE_SIZE - cam_x
                sy = gy * TILE_SIZE - cam_y
                for i in range(2):
                    offset = math.sin(t_now * 1.5 + gx * 0.5 + gy * 0.3 + i) * 4
                    wy = sy + 8 + i * 14 + offset
                    pygame.draw.line(screen, (120, 180, 230),
                                     (sx + 4, wy), (sx + TILE_SIZE - 4, wy), 1)
                blink = abs(math.sin(t_now * 2 + gx + gy))
                if blink > 0.85:
                    bx = sx + (gx * 13 + gy * 7) % (TILE_SIZE - 6)
                    by = sy + (gx * 5 + gy * 11) % (TILE_SIZE - 6)
                    pygame.draw.circle(screen, (220, 240, 255), (bx, by), 2)

        for gy in range(gy0, gy1):
            for gx in range(gx0, gx1):
                t = self.tiles[gy][gx]
                if t not in (BIOME_GRASS, BIOME_FOREST): continue
                seed = ((gx * 1234567) ^ (gy * 7654321)) & 0xFFFFFF
                if seed % 100 < 25:
                    sx = gx * TILE_SIZE - cam_x
                    sy = gy * TILE_SIZE - cam_y
                    px = sx + (seed % TILE_SIZE)
                    py = sy + ((seed >> 8) % TILE_SIZE)
                    sway = math.sin(t_now * 2 + gx * 0.7 + gy * 0.5) * 1.5
                    darker = (20, 60, 20) if t == BIOME_FOREST else (40, 120, 40)
                    pygame.draw.line(screen, darker, (px, py), (px + sway, py - 4), 1)
                    pygame.draw.line(screen, darker, (px + 2, py), (px + 2 + sway, py - 3), 1)

        for o in self.objects:
            sx, sy = o["x"] - cam_x, o["y"] - cam_y
            if -100 < sx < SCREEN_WIDTH + 100 and -100 < sy < SCREEN_HEIGHT + 100:
                self._draw_object(screen, o, sx, sy)
        for b in self.buildings:
            sx = b["gx"] * TILE_SIZE - cam_x
            sy = b["gy"] * TILE_SIZE - cam_y
            self._draw_building(screen, b, sx, sy)

        for f in self.falling:
            self._draw_falling(screen, f, cam_x, cam_y)

    def _draw_falling(self, screen, f, cam_x, cam_y):
        sx = f["x"] - cam_x
        sy = f["y"] - cam_y
        progress = 1.0 - max(0.0, f["timer"] / FALL_ANIM_TIME)
        angle = progress * 80 * f["direction"]
        fade = int(255 * (1.0 - progress * progress))
        if f["kind"] in ("tree", "coal_ore", "iron_ore_rock", "gold_ore_rock", "diamond_ore_rock"):
            self._draw_tree_falling(screen, sx, sy, angle, fade)
        elif f["kind"] == "bush":
            self._draw_bush_falling(screen, sx, sy, angle, fade)

    def _draw_tree_falling(self, screen, sx, sy, angle, fade):
        surf = pygame.Surface((120, 140), pygame.SRCALPHA)
        base_x, base_y = 60, 130
        trunk_h = 48
        pygame.draw.polygon(surf, DARK_BROWN, [
            (base_x - 7, base_y), (base_x + 7, base_y),
            (base_x + 4, base_y - trunk_h), (base_x - 4, base_y - trunk_h)])
        if self.season == SEASON_AUTUMN:
            ld, lm, ll = (140, 70, 20), (200, 120, 40), (240, 170, 70)
        elif self.season == SEASON_WINTER:
            ld, lm, ll = (170, 180, 190), (210, 220, 230), (245, 245, 250)
        else:
            ld, lm, ll = (35, 85, 35), (60, 130, 60), (100, 175, 80)
        ccx, ccy = base_x, base_y - trunk_h - 18
        for dx, dy, r in [(-22, 4, 18), (0, 6, 20), (22, 4, 18), (-14, -6, 18), (14, -6, 18)]:
            pygame.draw.circle(surf, ld, (int(ccx + dx), int(ccy + dy)), r)
        for dx, dy, r in [(-18, 0, 16), (0, -2, 18), (18, 0, 16), (-8, -14, 15), (8, -14, 15)]:
            pygame.draw.circle(surf, lm, (int(ccx + dx), int(ccy + dy)), r)
        for dx, dy, r in [(-10, -8, 10), (0, -16, 12), (10, -8, 10)]:
            pygame.draw.circle(surf, ll, (int(ccx + dx), int(ccy + dy)), r)
        surf.set_alpha(fade)
        rotated = pygame.transform.rotate(surf, -angle)
        rect = rotated.get_rect()
        bx, by = 60, 130
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rot_bx = rect.centerx + (bx - rect.centerx) * cos_a - (by - rect.centery) * sin_a
        rot_by = rect.centery + (bx - rect.centerx) * sin_a + (by - rect.centery) * cos_a
        screen.blit(rotated, (sx - rot_bx, sy - rot_by))

    def _draw_bush_falling(self, screen, sx, sy, angle, fade):
        surf = pygame.Surface((60, 60), pygame.SRCALPHA)
        base_x, base_y = 30, 50
        for dx, dy, r in [(-12, -4, 10), (0, -6, 12), (12, -4, 10), (-6, -10, 9), (6, -10, 9)]:
            pygame.draw.circle(surf, (30, 80, 30), (base_x + dx, base_y + dy), r)
        for dx, dy, r in [(-10, -8, 9), (0, -12, 10), (10, -8, 9), (-4, -16, 8), (4, -16, 8)]:
            pygame.draw.circle(surf, (55, 120, 50), (base_x + dx, base_y + dy), r)
        surf.set_alpha(fade)
        rotated = pygame.transform.rotate(surf, -angle)
        rect = rotated.get_rect()
        bx, by = base_x, base_y
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rot_bx = rect.centerx + (bx - rect.centerx) * cos_a - (by - rect.centery) * sin_a
        rot_by = rect.centery + (bx - rect.centerx) * sin_a + (by - rect.centery) * cos_a
        screen.blit(rotated, (sx - rot_bx, sy - rot_by))

    def _tile_color(self, t, gx, gy):
        base = BIOME_COLORS[t]
        n = ((gx * 73856093) ^ (gy * 19349663)) & 0xFF
        delta = (n % 16) - 8
        if t == BIOME_GRASS and self.season == SEASON_AUTUMN:
            base = (150, 130, 60)
        elif t == BIOME_GRASS and self.season == SEASON_WINTER:
            base = (200, 210, 220)
        elif t == BIOME_FOREST and self.season == SEASON_AUTUMN:
            base = (130, 90, 40)
        elif t == BIOME_FOREST and self.season == SEASON_WINTER:
            base = (170, 180, 190)
        if self.is_mine:
            base = tuple(max(0, c - 40) for c in base)
        return (max(0, min(255, base[0] + delta)),
                max(0, min(255, base[1] + delta)),
                max(0, min(255, base[2] + delta)))

    def _draw_object(self, screen, o, sx, sy):
        kind = o["kind"]
        t = pygame.time.get_ticks() / 1000.0
        wind = math.sin(t * 1.5 + sx * 0.01) * 1.5
        if kind == "tree":
            self._draw_tree(screen, sx, sy, wind)
        elif kind == "rock":
            self._draw_rock(screen, sx, sy)
        elif kind == "bush":
            self._draw_bush(screen, sx, sy, wind, has_berries=o.get("has_berries", True))
        elif kind == "mine_entrance":
            self._draw_mine_entrance(screen, sx, sy, t)
        elif kind in ("coal_ore", "iron_ore_rock", "gold_ore_rock", "diamond_ore_rock"):
            self._draw_ore_rock(screen, sx, sy, kind)
        elif kind == "pickup":
            item_id = o.get("item_id", "wood")
            color = ITEMS[item_id][1] if item_id in ITEMS else (200, 200, 200)
            bob = math.sin(pygame.time.get_ticks() / 300 + sx) * 2
            pygame.draw.circle(screen, (0, 0, 0), (int(sx), int(sy)), 6, 1)
            pygame.draw.rect(screen, color,
                             (int(sx) - 5, int(sy - 14 + bob), 10, 10), border_radius=2)
            pygame.draw.rect(screen, (30, 30, 30),
                             (int(sx) - 5, int(sy - 14 + bob), 10, 10), 1, border_radius=2)

    def _draw_mine_entrance(self, screen, sx, sy, t):
        sh = pygame.Surface((70, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 90), (0, 0, 70, 20))
        screen.blit(sh, (sx - 35, sy - 8))
        pygame.draw.circle(screen, (90, 90, 95), (sx - 22, sy - 4), 10)
        pygame.draw.circle(screen, (100, 100, 105), (sx + 22, sy - 4), 10)
        pygame.draw.circle(screen, (110, 110, 115), (sx, sy - 26), 12)
        pygame.draw.ellipse(screen, (15, 15, 20), (sx - 20, sy - 24, 40, 24))
        pygame.draw.ellipse(screen, (0, 0, 0), (sx - 16, sy - 20, 32, 18))
        pygame.draw.rect(screen, DARK_BROWN, (sx - 22, sy - 4, 4, 10))
        pygame.draw.rect(screen, DARK_BROWN, (sx + 18, sy - 4, 4, 10))
        pygame.draw.rect(screen, DARK_BROWN, (sx - 22, sy - 26, 44, 4))
        blink = abs(math.sin(t * 3))
        if blink > 0.7:
            pygame.draw.circle(screen, (150, 120, 80), (int(sx), int(sy - 12)), 3)

    def _draw_ore_rock(self, screen, sx, sy, kind):
        pygame.draw.polygon(screen, (100, 100, 105),
                            [(sx - 20, sy), (sx - 16, sy - 14), (sx - 4, sy - 22),
                             (sx + 10, sy - 20), (sx + 20, sy - 10), (sx + 18, sy)])
        pygame.draw.polygon(screen, (70, 70, 75),
                            [(sx - 20, sy), (sx - 16, sy - 14), (sx - 4, sy - 22), (sx - 4, sy)])
        pygame.draw.polygon(screen, (130, 130, 135),
                            [(sx - 4, sy - 22), (sx + 10, sy - 20),
                             (sx + 14, sy - 12), (sx, sy - 12)])
        if kind == "coal_ore":
            for dx, dy in [(-8, -8), (2, -4), (8, -12), (-2, -14)]:
                pygame.draw.circle(screen, (30, 30, 35), (sx + dx, sy + dy), 2)
        elif kind == "iron_ore_rock":
            for dx, dy in [(-8, -8), (2, -4), (8, -12), (-2, -14), (5, -6)]:
                pygame.draw.circle(screen, (190, 190, 210), (sx + dx, sy + dy), 2)
                pygame.draw.circle(screen, (230, 230, 250), (sx + dx - 1, sy + dy - 1), 1)
        elif kind == "gold_ore_rock":
            for dx, dy in [(-8, -8), (2, -4), (8, -12), (-2, -14), (5, -6), (-5, -16)]:
                pygame.draw.circle(screen, (230, 200, 60), (sx + dx, sy + dy), 2)
                pygame.draw.circle(screen, (255, 240, 150), (sx + dx - 1, sy + dy - 1), 1)
        elif kind == "diamond_ore_rock":
            for dx, dy in [(-8, -8), (2, -4), (8, -12), (-2, -14), (5, -6), (-5, -16), (10, -8)]:
                pygame.draw.circle(screen, (170, 230, 250), (sx + dx, sy + dy), 2)
                pygame.draw.circle(screen, (240, 255, 255), (sx + dx - 1, sy + dy - 1), 1)

    def _draw_tree(self, screen, sx, sy, wind):
        shadow = pygame.Surface((70, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 70, 20))
        screen.blit(shadow, (sx - 35, sy - 6))
        trunk_h = 48
        pygame.draw.polygon(screen, DARK_BROWN,
                            [(sx - 7, sy), (sx + 7, sy),
                             (sx + 4, sy - trunk_h), (sx - 4, sy - trunk_h)])
        for i in range(3):
            bx = sx - 4 + i * 4
            pygame.draw.line(screen, (50, 30, 15), (bx, sy - 4), (bx, sy - trunk_h + 4), 1)
        pygame.draw.line(screen, (170, 110, 60), (sx - 5, sy - 6), (sx - 3, sy - trunk_h + 4), 2)
        pygame.draw.arc(screen, DARK_BROWN, (sx - 14, sy - 6, 14, 10), 0, 3.14, 3)
        pygame.draw.arc(screen, DARK_BROWN, (sx, sy - 6, 14, 10), 0, 3.14, 3)
        branch_y = sy - trunk_h + 10
        pygame.draw.line(screen, DARK_BROWN, (sx - 3, branch_y), (sx - 16, branch_y - 12), 3)
        pygame.draw.line(screen, DARK_BROWN, (sx + 3, branch_y - 4), (sx + 18, branch_y - 16), 3)
        if self.season == SEASON_AUTUMN:
            leaf_dark, leaf_mid, leaf_light = (140, 70, 20), (200, 120, 40), (240, 170, 70)
        elif self.season == SEASON_WINTER:
            leaf_dark, leaf_mid, leaf_light = (170, 180, 190), (210, 220, 230), (245, 245, 250)
        else:
            leaf_dark, leaf_mid, leaf_light = (35, 85, 35), (60, 130, 60), (100, 175, 80)
        ccx, ccy = sx + wind, sy - trunk_h - 18
        for dx, dy, r in [(-22, 4, 18), (0, 6, 20), (22, 4, 18), (-14, -6, 18), (14, -6, 18)]:
            pygame.draw.circle(screen, leaf_dark, (int(ccx + dx), int(ccy + dy)), r)
        for dx, dy, r in [(-18, 0, 16), (0, -2, 18), (18, 0, 16), (-8, -14, 15), (8, -14, 15)]:
            pygame.draw.circle(screen, leaf_mid, (int(ccx + dx), int(ccy + dy)), r)
        for dx, dy, r in [(-10, -8, 10), (0, -16, 12), (10, -8, 10)]:
            pygame.draw.circle(screen, leaf_light, (int(ccx + dx), int(ccy + dy)), r)

    def _draw_rock(self, screen, sx, sy):
        shadow = pygame.Surface((46, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 46, 14))
        screen.blit(shadow, (sx - 23, sy - 4))
        pygame.draw.polygon(screen, (110, 110, 115),
                            [(sx - 20, sy), (sx - 16, sy - 14), (sx - 4, sy - 22),
                             (sx + 10, sy - 20), (sx + 20, sy - 10), (sx + 18, sy)])
        pygame.draw.polygon(screen, (80, 80, 85),
                            [(sx - 20, sy), (sx - 16, sy - 14), (sx - 4, sy - 22), (sx - 4, sy)])
        pygame.draw.polygon(screen, (150, 150, 155),
                            [(sx - 4, sy - 22), (sx + 10, sy - 20),
                             (sx + 14, sy - 12), (sx, sy - 12)])
        pygame.draw.circle(screen, (200, 200, 210), (sx + 2, sy - 16), 2)
        pygame.draw.circle(screen, (70, 120, 60), (sx - 14, sy - 4), 3)

    def _draw_bush(self, screen, sx, sy, wind, has_berries=True):
        shadow = pygame.Surface((38, 12), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 70), (0, 0, 38, 12))
        screen.blit(shadow, (sx - 19, sy - 4))
        cx = sx + wind * 0.5
        for dx, dy, r in [(-12, -4, 10), (0, -6, 12), (12, -4, 10), (-6, -10, 9), (6, -10, 9)]:
            pygame.draw.circle(screen, (30, 80, 30), (int(cx + dx), sy + dy), r)
        for dx, dy, r in [(-10, -8, 9), (0, -12, 10), (10, -8, 9), (-4, -16, 8), (4, -16, 8)]:
            pygame.draw.circle(screen, (55, 120, 50), (int(cx + dx), sy + dy), r)
        for dx, dy, r in [(-6, -18, 5), (2, -20, 6), (8, -16, 5)]:
            pygame.draw.circle(screen, (90, 160, 70), (int(cx + dx), sy + dy), r)
        if has_berries:
            rnd = random.Random(int(sx * 11 + sy * 5) & 0xFFFF)
            for _ in range(5):
                bx = rnd.randint(-14, 14)
                by = rnd.randint(-20, -4)
                pygame.draw.circle(screen, (200, 50, 80), (int(cx + bx), int(sy + by)), 2)

    def _draw_building(self, screen, b, sx, sy):
        kind = b["kind"]
        if kind == "wall":
            pygame.draw.rect(screen, (140, 100, 60), (sx, sy, TILE_SIZE, TILE_SIZE))
            pygame.draw.rect(screen, (90, 60, 30), (sx, sy, TILE_SIZE, TILE_SIZE), 2)
        elif kind == "door":
            color = (110, 70, 40) if b.get("opened") else (170, 110, 60)
            pygame.draw.rect(screen, color, (sx + 4, sy + 4, TILE_SIZE - 8, TILE_SIZE - 8))
            pygame.draw.circle(screen, YELLOW, (sx + TILE_SIZE - 8, sy + TILE_SIZE // 2), 2)
        elif kind == "roof":
            pygame.draw.rect(screen, (100, 70, 40), (sx, sy, TILE_SIZE, TILE_SIZE))
            pygame.draw.line(screen, (60, 40, 20), (sx, sy), (sx + TILE_SIZE, sy + TILE_SIZE), 2)
        elif kind == "bed":
            pygame.draw.rect(screen, (200, 80, 80),
                             (sx + 4, sy + 4, TILE_SIZE - 8, TILE_SIZE - 8), border_radius=4)
            pygame.draw.rect(screen, WHITE, (sx + 4, sy + 4, TILE_SIZE - 8, 8), border_radius=4)
        elif kind == "campfire":
            pygame.draw.circle(screen, (80, 60, 40),
                               (sx + TILE_SIZE // 2, sy + TILE_SIZE // 2), 10)
            t = pygame.time.get_ticks() / 100.0
            fx, fy = sx + TILE_SIZE // 2, sy + TILE_SIZE // 2 - 4
            pygame.draw.circle(screen, ORANGE, (int(fx), int(fy + math.sin(t) * 2)), 6)
            pygame.draw.circle(screen, YELLOW, (int(fx), int(fy + math.sin(t + 1) * 2)), 3)
        elif kind == "chest":
            pygame.draw.rect(screen, (150, 110, 60),
                             (sx + 4, sy + 8, TILE_SIZE - 8, TILE_SIZE - 12), border_radius=3)
            pygame.draw.rect(screen, (110, 80, 40),
                             (sx + 4, sy + 4, TILE_SIZE - 8, TILE_SIZE // 2), border_radius=3)
            pygame.draw.rect(screen, (240, 220, 100),
                             (sx + TILE_SIZE // 2 - 3, sy + TILE_SIZE // 2 - 2, 6, 4))
        elif kind == "tent":
            pygame.draw.polygon(screen, (180, 100, 60), [
                (sx + 4, sy + TILE_SIZE - 4),
                (sx + TILE_SIZE // 2, sy + 4),
                (sx + TILE_SIZE - 4, sy + TILE_SIZE - 4)])
            pygame.draw.polygon(screen, (120, 70, 40), [
                (sx + 4, sy + TILE_SIZE - 4),
                (sx + TILE_SIZE // 2, sy + 4),
                (sx + TILE_SIZE - 4, sy + TILE_SIZE - 4)], 2)
            pygame.draw.rect(screen, (60, 35, 20),
                             (sx + TILE_SIZE // 2 - 4, sy + TILE_SIZE - 12, 8, 10))
        elif kind == "farm_plot":
            self._draw_farm_plot(screen, b, sx, sy)

    def _draw_farm_plot(self, screen, b, sx, sy):
        # Земля
        pygame.draw.rect(screen, (110, 80, 50), (sx + 2, sy + 2, TILE_SIZE - 4, TILE_SIZE - 4))
        # Бороздки
        for i in range(3):
            pygame.draw.line(screen, (80, 55, 30),
                             (sx + 4, sy + 8 + i * 8), (sx + TILE_SIZE - 4, sy + 8 + i * 8), 1)
        state = b.get("state", "empty")
        crop = b.get("crop")
        if state == "empty":
            return
        if crop and crop in CROPS:
            color = CROPS[crop]["color"]
            if state == "growing":
                growth = b.get("growth", 0)
                total = CROPS[crop]["grow_time"]
                frac = min(1.0, growth / total)
                # маленький росток
                h = int(4 + frac * 12)
                for i in range(3):
                    px = sx + 8 + i * 7
                    pygame.draw.line(screen, (60, 140, 50),
                                     (px, sy + TILE_SIZE - 4), (px, sy + TILE_SIZE - 4 - h), 2)
                    if frac > 0.5:
                        pygame.draw.circle(screen, color, (px, sy + TILE_SIZE - 4 - h), 2)
            elif state == "ripe":
                # спелый плод
                for i in range(3):
                    px = sx + 8 + i * 7
                    pygame.draw.line(screen, (60, 140, 50),
                                     (px, sy + TILE_SIZE - 4), (px, sy + TILE_SIZE - 16), 2)
                    pygame.draw.circle(screen, color, (px, sy + TILE_SIZE - 18), 4)
                    pygame.draw.circle(screen, tuple(min(255, c + 40) for c in color),
                                       (px - 1, sy + TILE_SIZE - 19), 2)

    def to_dict(self):
        return {
            "seed": self.seed, "location": self.location,
            "size_key": self.size_key, "is_tent": self.is_tent,
            "is_mine": self.is_mine,
            "map_w": self.map_w, "map_h": self.map_h,
            "objects": [dict(o) for o in self.objects],
            "buildings": [dict(b) for b in self.buildings],
            "mobs": [{"x": m.x, "y": m.y, "hp": m.hp, "kind": getattr(m, "kind", "zombie")}
                     for m in self.mobs],
        }

    def load_state(self, data):
        if "map_w" in data and "map_h" in data:
            self.map_w = data["map_w"]
            self.map_h = data["map_h"]
        if "objects" in data:
            self.objects = []
            for o in data["objects"]:
                obj = dict(o)
                if obj.get("kind") == "bush" and "has_berries" not in obj:
                    obj["has_berries"] = True
                    obj["berry_timer"] = 0.0
                self.objects.append(obj)
        if "buildings" in data:
            self.buildings = [dict(b) for b in data["buildings"]]
        if "mobs" in data:
            from entities import Animal, Monster
            self.mobs = []
            for m in data["mobs"]:
                kind = m.get("kind", "zombie")
                if kind in ("zombie", "skeleton"):
                    mob = Monster(m["x"], m["y"], self.rng)
                    mob.kind = kind
                else:
                    mob = Animal(m["x"], m["y"], self.rng, kind=kind)
                mob.hp = m.get("hp", mob.max_hp)
                self.mobs.append(mob)