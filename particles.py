"""particles.py — система частиц: пыль, искры, листья, снег, бабочки, светлячки."""
import math
import random
import pygame


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life",
                 "color", "size", "gravity", "fade", "kind")

    def __init__(self, x, y, vx, vy, life, color, size, gravity=0.0, fade=True, kind="dot"):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size
        self.gravity = gravity
        self.fade = fade
        self.kind = kind


class ParticleSystem:
    def __init__(self):
        self.particles = []

    def emit(self, kind, x, y, count=8, **kwargs):
        for _ in range(count):
            if kind == "dust":
                self.particles.append(Particle(
                    x + random.uniform(-6, 6), y + random.uniform(-4, 4),
                    random.uniform(-2, 2), random.uniform(-3, -0.5),
                    random.uniform(0.3, 0.7), kwargs.get("color", (180, 170, 150)),
                    random.randint(2, 4), gravity=0.15, kind="dot"))
            elif kind == "spark":
                self.particles.append(Particle(
                    x + random.uniform(-4, 4), y + random.uniform(-4, 4),
                    random.uniform(-3, 3), random.uniform(-4, 0),
                    random.uniform(0.3, 0.8), kwargs.get("color", (250, 200, 80)),
                    random.randint(1, 3), gravity=0.2, kind="dot"))
            elif kind == "leaf":
                self.particles.append(Particle(
                    x + random.uniform(-20, 20), y + random.uniform(-10, 10),
                    random.uniform(-1, 1), random.uniform(0.5, 1.5),
                    random.uniform(2.0, 4.0), kwargs.get("color", (200, 120, 40)),
                    random.randint(2, 3), gravity=0.02, kind="leaf"))
            elif kind == "snow":
                self.particles.append(Particle(
                    x + random.uniform(-20, 20), y + random.uniform(-10, 10),
                    random.uniform(-0.5, 0.5), random.uniform(0.4, 1.0),
                    random.uniform(3.0, 6.0), (240, 240, 250),
                    random.randint(1, 3), gravity=0.01, kind="dot"))
            elif kind == "splash":
                self.particles.append(Particle(
                    x + random.uniform(-6, 6), y + random.uniform(-4, 4),
                    random.uniform(-3, 3), random.uniform(-6, -1),
                    random.uniform(0.4, 0.9), (100, 180, 240),
                    random.randint(2, 4), gravity=0.3, kind="dot"))
            elif kind == "hit":
                self.particles.append(Particle(
                    x + random.uniform(-4, 4), y + random.uniform(-4, 4),
                    random.uniform(-4, 4), random.uniform(-4, 4),
                    random.uniform(0.2, 0.4), kwargs.get("color", (240, 80, 80)),
                    random.randint(2, 4), gravity=0.0, kind="dot"))
            elif kind == "firefly":
                self.particles.append(Particle(
                    x + random.uniform(-20, 20), y + random.uniform(-20, 20),
                    random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3),
                    random.uniform(3.0, 6.0), (250, 240, 120),
                    random.randint(1, 2), gravity=0.0, kind="firefly"))
            elif kind == "butterfly":
                self.particles.append(Particle(
                    x, y, random.uniform(-0.6, 0.6), random.uniform(-0.6, 0.6),
                    random.uniform(3.0, 6.0),
                    random.choice([(250, 180, 220), (250, 230, 120), (180, 220, 250)]),
                    random.randint(3, 5), gravity=0.0, kind="butterfly"))

    def update(self, dt):
        for p in list(self.particles):
            p.life -= dt
            if p.life <= 0:
                self.particles.remove(p)
                continue
            p.x += p.vx
            p.y += p.vy
            p.vy += p.gravity
            if p.kind == "leaf":
                p.x += math.sin(p.life * 6) * 0.5
            elif p.kind == "butterfly":
                p.x += math.sin(p.life * 8) * 0.8
                p.y += math.cos(p.life * 6) * 0.4
            elif p.kind == "firefly":
                p.x += math.sin(p.life * 3) * 0.3
                p.y += math.cos(p.life * 2) * 0.3

    def draw(self, screen, camera):
        cam_x, cam_y = camera.offset
        for p in self.particles:
            sx = int(p.x - cam_x)
            sy = int(p.y - cam_y)
            if sx < -20 or sx > screen.get_width() + 20 or sy < -20 or sy > screen.get_height() + 20:
                continue
            alpha = 255
            if p.fade and p.max_life > 0:
                alpha = int(255 * (p.life / p.max_life))
            alpha = max(0, min(255, alpha))
            if p.kind == "dot":
                s = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p.color, alpha), (p.size, p.size), p.size)
                screen.blit(s, (sx - p.size, sy - p.size))
            elif p.kind == "leaf":
                s = pygame.Surface((p.size * 2 + 2, p.size + 2), pygame.SRCALPHA)
                pygame.draw.ellipse(s, (*p.color, alpha), (0, 0, p.size * 2, p.size))
                screen.blit(s, (sx - p.size, sy - p.size // 2))
            elif p.kind == "butterfly":
                s = pygame.Surface((p.size * 2, p.size * 2), pygame.SRCALPHA)
                flap = abs(math.sin(p.life * 10))
                w = max(1, int(p.size * flap))
                pygame.draw.ellipse(s, (*p.color, alpha), (p.size - w, 0, w, p.size * 2))
                pygame.draw.ellipse(s, (*p.color, alpha), (p.size, 0, w, p.size * 2))
                screen.blit(s, (sx - p.size, sy - p.size))
            elif p.kind == "firefly":
                glow = abs(math.sin(p.life * 4))
                a = int(alpha * glow)
                s = pygame.Surface((8, 8), pygame.SRCALPHA)
                pygame.draw.circle(s, (*p.color, a // 3), (4, 4), 4)
                pygame.draw.circle(s, (*p.color, a), (4, 4), 2)
                screen.blit(s, (sx - 4, sy - 4))