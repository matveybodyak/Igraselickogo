"""daynight.py — цикл дня/ночи, сезоны, освещение, температура, погода."""
import math
import random
import pygame
from settings import (
    DAY_LENGTH_SECONDS, SEASON_DAYS, SEASON_NAMES,
    SEASON_SPRING, SEASON_SUMMER, SEASON_AUTUMN, SEASON_WINTER,
    SCREEN_WIDTH, SCREEN_HEIGHT
)


class DayNightCycle:
    def __init__(self, day_length=DAY_LENGTH_SECONDS):
        self.day_length = day_length
        self.t = 0.0
        self.day_count = 1
        self.season = SEASON_SPRING
        self.season_day = 1
        self.weather = "clear"
        self.weather_timer = 0.0
        self.weather_check = 20.0

    @property
    def is_night(self): return self.t >= 0.8 or self.t < 0.05
    @property
    def is_day(self): return 0.25 <= self.t < 0.6
    @property
    def season_name(self): return SEASON_NAMES[self.season]
    @property
    def time_str(self):
        tm = self.t * 24 * 60
        return f"{int(tm // 60) % 24:02d}:{int(tm % 60):02d}"

    def update(self, dt, world=None):
        self.t += dt / self.day_length
        if self.t >= 1.0:
            self.t -= 1.0
            self.day_count += 1
            self.season_day += 1
            if self.season_day > SEASON_DAYS:
                self.season_day = 1
                self.season = (self.season + 1) % 4
                if world: world.apply_season(self.season)
        self.weather_timer += dt
        if self.weather_timer >= self.weather_check:
            self.weather_timer = 0.0
            self._roll_weather()

    def _roll_weather(self):
        r = random.random()
        if self.season == SEASON_WINTER:
            self.weather = "snow" if r < 0.45 else "clear"
        elif self.season in (SEASON_SPRING, SEASON_AUTUMN):
            self.weather = "rain" if r < 0.30 else "clear"
        else:
            self.weather = "rain" if r < 0.12 else "clear"

    def skip_to_morning(self):
        self.t = 0.25
        self.weather = "clear"

    def get_darkness(self):
        t = self.t
        if t < 0.05: a = 200
        elif t < 0.25: a = 200 - (t - 0.05) / 0.20 * 170
        elif t < 0.6: a = 20
        elif t < 0.8: a = 20 + (t - 0.6) / 0.2 * 150
        else: a = 200
        if 0.6 <= t < 0.8: return (60, 30, 10, int(a))
        if t >= 0.8 or t < 0.05: return (5, 10, 30, int(a))
        return (0, 0, 0, int(a))

    def draw_light_overlay(self, screen, camera=None, extra_lights=None):
        """
        Затемняет экран и вырезает круги света.
        extra_lights: список (world_x, world_y, radius, intensity)
        camera: нужен, чтобы перевести мировые координаты в экранные.
        """
        r, g, b, a = self.get_darkness()
        if a <= 0:
            return
        import light as _light
        sources = []
        if camera is not None and extra_lights:
            cam_x, cam_y = camera.offset
            for (wx, wy, rad, inten) in extra_lights:
                sources.append((wx - cam_x, wy - cam_y, rad, inten))
        sw, sh = screen.get_size()
        mask = _light.make_light_mask(sw, sh, (r, g, b), int(a), sources)
        screen.blit(mask, (0, 0))

    def get_temperature(self):
        base = {SEASON_SPRING: 55, SEASON_SUMMER: 70,
                SEASON_AUTUMN: 45, SEASON_WINTER: 25}[self.season]
        if self.is_night: base -= 20
        elif self.t < 0.15: base -= 10
        if self.weather == "rain": base -= 10
        elif self.weather == "snow": base -= 15
        return max(0, min(100, base))

    def draw_weather(self, screen):
        if self.weather == "clear": return
        t = pygame.time.get_ticks() / 1000.0
        if self.weather == "rain":
            color, count, length, speed = (150, 180, 220), 180, 12, 600
        else:
            color, count, length, speed = (240, 240, 250), 120, 3, 90
        for i in range(count):
            sx = (i * 97) % SCREEN_WIDTH
            sy = (i * 53) % SCREEN_HEIGHT
            if self.weather == "rain":
                y = (sy + t * speed) % (SCREEN_HEIGHT + 40)
                pygame.draw.line(screen, color, (sx, y), (sx - 3, y + length), 1)
            else:
                x = (sx + math.sin(t * 1.5 + i) * 20) % SCREEN_WIDTH
                y = (sy + t * speed) % (SCREEN_HEIGHT + 20)
                pygame.draw.circle(screen, color, (int(x), int(y)), length)

    def to_dict(self):
        return {"t": self.t, "day_count": self.day_count, "season": self.season,
                "season_day": self.season_day, "weather": self.weather}

    def load_state(self, data):
        self.t = data.get("t", 0.0)
        self.day_count = data.get("day_count", 1)
        self.season = data.get("season", SEASON_SPRING)
        self.season_day = data.get("season_day", 1)
        self.weather = data.get("weather", "clear")