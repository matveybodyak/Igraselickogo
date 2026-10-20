"""entities.py — мобы: Animal (5 видов), Monster, Fish. С анимацией вспышки урона."""
import math
import random
import pygame
from settings import RED
import sprites


class Mob:
    def __init__(self, x, y):
        self.x, self.y = float(x), float(y)
        self.w, self.h = 22, 26
        self.hp = self.max_hp = 30
        self.speed = 1.5
        self.dead = False
        self.direction = (0, 1)
        self.facing = 1
        self.state = "idle"
        self.state_timer = 0.0
        self.wander_dx = 0.0
        self.wander_dy = 0.0
        self.attack_cooldown = 0.0
        self.anim_phase = 0.0
        self.moving = False
        self.hit_flash = 0.0
        self.rng = random.Random()

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h), self.w, self.h)

    def distance_to(self, x, y):
        return math.hypot(self.x - x, self.y - y)

    def take_damage(self, amount):
        self.hp -= amount
        self.hit_flash = 0.2
        if self.hp <= 0:
            self.hp = 0
            self.dead = True
            self.on_death()

    def on_death(self):
        pass

    def _move(self, dx, dy, dt, world):
        if dx == 0 and dy == 0:
            self.moving = False
            return
        length = math.hypot(dx, dy)
        if length == 0:
            self.moving = False
            return
        dx, dy = dx / length, dy / length
        step = self.speed * dt * 60
        moved = False
        if world.can_walk(self.x + dx * step, self.y, self.w, self.h):
            self.x += dx * step
            moved = True
        if world.can_walk(self.x, self.y + dy * step, self.w, self.h):
            self.y += dy * step
            moved = True
        self.direction = (dx, dy)
        if abs(dx) > 0.1:
            self.facing = 1 if dx > 0 else -1
        self.moving = moved
        if moved:
            self.anim_phase += dt * 10

    def update(self, dt, world, player, daynight):
        self.state_timer -= dt
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.state_timer <= 0:
            self._pick_new_state(player, daynight)
        if self.state == "wander":
            self._move(self.wander_dx, self.wander_dy, dt, world)
        elif self.state == "flee" and player:
            self._move(self.x - player.x, self.y - player.y, dt, world)
        elif self.state == "chase" and player:
            self._move(player.x - self.x, player.y - self.y, dt, world)
            if self.distance_to(player.x, player.y) < 40:
                self._attack(player)
        else:
            self.moving = False
        if self.hit_flash > 0:
            self.hit_flash -= dt

    def _pick_new_state(self, player, daynight):
        self.state = "wander"
        ang = self.rng.uniform(0, math.tau)
        self.wander_dx = math.cos(ang)
        self.wander_dy = math.sin(ang)
        self.state_timer = self.rng.uniform(1.5, 4.0)

    def _attack(self, player):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 1.2
            player.take_damage(8)

    def draw(self, screen, camera):
        sx, sy = camera.apply((self.x, self.y))
        pygame.draw.rect(screen, RED, (sx - self.w // 2, sy - self.h, self.w, self.h),
                         border_radius=4)

    def _draw_hp_bar(self, screen, sx, sy):
        if self.hp < self.max_hp:
            bar_w = max(20, self.w)
            bx, by = sx - bar_w // 2, sy - self.h - 14
            pygame.draw.rect(screen, (60, 20, 20), (bx, by, bar_w, 3))
            pygame.draw.rect(screen, RED, (bx, by, int(bar_w * self.hp / self.max_hp), 3))


class Animal(Mob):
    TYPES = {
        "deer":    {"hp": 40, "speed": 2.2, "w": 26, "h": 30, "drop": ("raw_meat", 2)},
        "rabbit":  {"hp": 15, "speed": 2.8, "w": 16, "h": 16, "drop": ("raw_meat", 1)},
        "cow":     {"hp": 60, "speed": 1.2, "w": 44, "h": 28, "drop": ("raw_meat", 3)},
        "sheep":   {"hp": 40, "speed": 1.4, "w": 34, "h": 24, "drop": ("wool", 2)},
        "chicken": {"hp": 12, "speed": 2.0, "w": 22, "h": 18, "drop": ("feather", 2)},
    }

    def __init__(self, x, y, rng=None, kind=None):
        super().__init__(x, y)
        self.rng = rng or random.Random()
        self.kind = kind or self.rng.choice(list(self.TYPES.keys()))
        data = self.TYPES[self.kind]
        self.hp = self.max_hp = data["hp"]
        self.speed = data["speed"]
        self.w, self.h = data["w"], data["h"]
        self.drop = data["drop"]

    def _pick_new_state(self, player, daynight):
        flee_radius = {"deer": 180, "rabbit": 150, "cow": 100, "sheep": 110, "chicken": 130}[self.kind]
        if player and self.distance_to(player.x, player.y) < flee_radius:
            self.state = "flee"
            self.state_timer = 1.0
            return
        self.state = "wander" if self.rng.random() < 0.7 else "idle"
        ang = self.rng.uniform(0, math.tau)
        self.wander_dx = math.cos(ang)
        self.wander_dy = math.sin(ang)
        self.state_timer = self.rng.uniform(2.0, 5.0)

    def draw(self, screen, camera):
        sx, sy = camera.apply((self.x, self.y))
        fn = {"deer": sprites.draw_deer, "rabbit": sprites.draw_rabbit,
              "cow": sprites.draw_cow, "sheep": sprites.draw_sheep,
              "chicken": sprites.draw_chicken}[self.kind]
        fn(screen, int(sx), int(sy), self.anim_phase, self.moving, self.facing)
        if self.hit_flash > 0:
            s = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
            s.fill((255, 255, 255, int(120 * self.hit_flash / 0.2)))
            screen.blit(s, (int(sx) - (self.w + 20) // 2, int(sy) - self.h - 10))
        self._draw_hp_bar(screen, int(sx), int(sy))


class Monster(Mob):
    def __init__(self, x, y, rng=None):
        super().__init__(x, y)
        self.rng = rng or random.Random()
        self.kind = self.rng.choice(["zombie", "skeleton"])
        if self.kind == "zombie":
            self.hp = self.max_hp = 50
            self.speed = 1.6
            self.w, self.h = 22, 28
            self.damage = 10
            self.drop = "raw_meat"
        else:
            self.hp = self.max_hp = 35
            self.speed = 2.0
            self.w, self.h = 20, 28
            self.damage = 8
            self.drop = "stone"
        self.state = "chase"

    def _pick_new_state(self, player, daynight):
        if player and self.distance_to(player.x, player.y) < 500:
            self.state = "chase"
        else:
            self.state = "wander"
            ang = self.rng.uniform(0, math.tau)
            self.wander_dx = math.cos(ang)
            self.wander_dy = math.sin(ang)
            self.state_timer = self.rng.uniform(1.5, 3.0)

    def _attack(self, player):
        if self.attack_cooldown <= 0:
            self.attack_cooldown = 1.0
            player.take_damage(self.damage)

    def draw(self, screen, camera):
        sx, sy = camera.apply((self.x, self.y))
        cx, cy = int(sx), int(sy)
        bob = math.sin(self.anim_phase) * 2 if self.moving else 0
        sh = pygame.Surface((self.w + 6, 6), pygame.SRCALPHA)
        pygame.draw.ellipse(sh, (0, 0, 0, 70), (0, 0, self.w + 6, 6))
        screen.blit(sh, (cx - (self.w + 6) // 2, cy - 3))
        swing = math.sin(self.anim_phase) * 2 if self.moving else 0
        for i, dx in enumerate((-6, 6)):
            lx = cx + dx + (swing if i == 0 else -swing)
            leg_color = (40, 50, 40) if self.kind == "zombie" else (150, 150, 150)
            pygame.draw.rect(screen, leg_color, (lx - 2, cy - 8, 4, 8))
        body = pygame.Rect(cx - self.w // 2, int(cy - self.h + bob), self.w, self.h)
        color = (70, 120, 60) if self.kind == "zombie" else (215, 215, 215)
        edge = (30, 60, 30) if self.kind == "zombie" else (150, 150, 150)
        pygame.draw.rect(screen, color, body, border_radius=5)
        pygame.draw.rect(screen, edge, body, 2, border_radius=5)
        head_y = body.y + 4
        pygame.draw.circle(screen, color, (cx, head_y), 7)
        pygame.draw.circle(screen, edge, (cx, head_y), 7, 1)
        ex = cx + self.facing * 2
        pygame.draw.circle(screen, (200, 30, 30), (ex - 3, head_y - 1), 2)
        pygame.draw.circle(screen, (200, 30, 30), (ex + 3, head_y - 1), 2)
        if self.kind == "zombie":
            for i in range(2):
                yy = body.y + 10 + i * 6
                pygame.draw.line(screen, (40, 60, 40), (body.x + 3, yy), (body.right - 3, yy), 1)
        if self.hit_flash > 0:
            s = pygame.Surface((self.w + 20, self.h + 20), pygame.SRCALPHA)
            s.fill((255, 255, 255, int(120 * self.hit_flash / 0.2)))
            screen.blit(s, (cx - (self.w + 20) // 2, cy - self.h - 10))
        self._draw_hp_bar(screen, cx, cy)


class Fish:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.dead = False

    def update(self, dt, world, player, daynight):
        pass

    def draw(self, screen, camera):
        sx, sy = camera.apply((self.x, self.y))
        pygame.draw.ellipse(screen, (120, 180, 200), (sx - 6, sy - 3, 12, 6))