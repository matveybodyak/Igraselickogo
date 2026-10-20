"""player.py — игрок: idle-анимации, фермерство, броня, шахта."""
import math
import random
import pygame
from settings import (
    PLAYER_SPEED, PLAYER_MAX_HP, PLAYER_MAX_HUNGER, PLAYER_MAX_THIRST,
    PLAYER_TEMP_DEFAULT, HUNGER_RATE, THIRST_RATE, TEMP_COLD_RATE, TEMP_HOT_RATE,
    BIOME_WATER, RED, YELLOW, WEAPONS, ARMOR, CROPS, CROP_RESULT, FOOD_VALUES,
)
from inventory import Inventory
import heroine

HERO_SCALE = 0.75


class Player:
    def __init__(self, x, y, look=None):
        self.x, self.y = float(x), float(y)
        self.w, self.h = 22, 36
        self.speed = PLAYER_SPEED
        self.direction = (0, 1)
        self.facing = 1
        self.look = heroine.normalize_look(look or heroine.DEFAULT_LOOK)

        self.base_max_hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self.hp = PLAYER_MAX_HP
        self.hunger = self.max_hunger = PLAYER_MAX_HUNGER
        self.thirst = self.max_thirst = PLAYER_MAX_THIRST
        self.temp = PLAYER_TEMP_DEFAULT
        self.max_temp = 100

        self.equipped_armor = None
        self.armor_bonus = 0
        self.weapon_damage = 25

        self.inventory = Inventory()
        self.hotbar = [0, 1, 2, 3, 4]
        self.hotbar_selected = 0

        self.attacking_timer = 0.0
        self.attack_cooldown = 0.0
        self.hurt_anim_timer = 0.0
        self.hurt_anim_duration = 0.3
        self.shiver = 0.0

        self.in_water = False
        self.near_campfire = False
        self.inside_house = False

        self._tick_hunger = 0.0
        self._tick_thirst = 0.0
        self._tick_temp = 0.0

        # Анимации
        self.anim_phase = 0.0
        self.anim_phase_blend = 0.0  # 0 = покой, 1 = ходьба
        self.moving = False
        self.idle_time = 0.0  # сколько секунд без движения
        self.blink_timer = random.uniform(2.0, 5.0)
        self.blinking = False
        self.blink_duration = 0.12
        self.eye_dir = (0, 0)

        self.audio = None
        self._last_step = 0.0

        self.vis_hp = float(self.hp)
        self.vis_hunger = float(self.hunger)
        self.vis_thirst = float(self.thirst)
        self.vis_temp = float(self.temp)

    @property
    def rect(self):
        return pygame.Rect(int(self.x - self.w // 2), int(self.y - self.h),
                           self.w, self.h)

    @property
    def center(self):
        return self.x, self.y - self.h // 2

    def _play_sfx(self, name):
        if self.audio:
            self.audio.play_sfx(name)

    def _maybe_step_sfx(self):
        if not self.moving:
            return
        now = pygame.time.get_ticks() / 1000.0
        if now - self._last_step > 0.35:
            self._last_step = now
            self._play_sfx("step")

    def equip_armor(self, armor_id):
        if armor_id not in ARMOR: return
        if self.equipped_armor == armor_id: return
        self.equipped_armor = armor_id
        self.armor_bonus = ARMOR[armor_id]["hp_bonus"]
        self.max_hp = self.base_max_hp + self.armor_bonus
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def set_weapon(self, item_id):
        if item_id in WEAPONS:
            self.weapon_damage = WEAPONS[item_id]["damage"]
        else:
            self.weapon_damage = 25

    def update(self, dt, world, daynight, game):
        self._handle_input(dt, world)
        self._update_stats(dt, world, daynight)
        self._update_cooldowns(dt)
        self._update_biome(world)
        self._update_eyes(dt)
        self._maybe_step_sfx()
        self._update_animation_state(dt)

        def smooth(cur, target, speed):
            if abs(cur - target) < 0.5:
                return float(target)
            return cur + (target - cur) * min(1.0, dt * speed)

        self.vis_hp = smooth(self.vis_hp, self.hp, 6.0)
        self.vis_hunger = smooth(self.vis_hunger, self.hunger, 4.0)
        self.vis_thirst = smooth(self.vis_thirst, self.thirst, 4.0)
        self.vis_temp = smooth(self.vis_temp, self.temp, 3.0)

        if self.temp < 30:
            self.shiver = min(1.0, (30 - self.temp) / 30.0)
        else:
            self.shiver = 0.0

    def _update_animation_state(self, dt):
        """Плавно переключаем между ходьбой и покоем."""
        if self.moving:
            self.idle_time = 0.0
            self.anim_phase += dt * 10
            # Плавно наращиваем blend до 1
            self.anim_phase_blend = min(1.0, self.anim_phase_blend + dt * 8.0)
        else:
            self.idle_time += dt
            # Плавно снижаем blend до 0
            self.anim_phase_blend = max(0.0, self.anim_phase_blend - dt * 6.0)
            # Если blend уже маленький — сбрасываем фазу, чтобы не застывать в «полушаге»
            if self.anim_phase_blend < 0.05:
                self.anim_phase = 0.0

    def _handle_input(self, dt, world):
        keys = pygame.key.get_pressed()
        dx, dy = 0.0, 0.0
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if dx or dy:
            L = math.hypot(dx, dy)
            dx, dy = dx / L, dy / L
            self.direction = (dx, dy)
            if abs(dx) > 0.1:
                self.facing = 1 if dx > 0 else -1
        speed = self.speed * (0.55 if self.in_water else 1.0)
        moved = False
        if world.can_walk(self.x + dx * speed, self.y, self.w, self.h):
            self.x += dx * speed
            moved = True
        if world.can_walk(self.x, self.y + dy * speed, self.w, self.h):
            self.y += dy * speed
            moved = True
        # Сбрасываем moving, если не сдвинулись
        self.moving = moved

    def _update_eyes(self, dt):
        dx, dy = self.direction
        self.eye_dir = (dx, dy)
        self.blink_timer -= dt
        if self.blinking:
            self.blink_duration -= dt
            if self.blink_duration <= 0:
                self.blinking = False
                self.blink_timer = random.uniform(2.0, 6.0)
        else:
            if self.blink_timer <= 0:
                self.blinking = True
                self.blink_duration = 0.12

    def _update_stats(self, dt, world, daynight):
        self._tick_hunger += dt
        self._tick_thirst += dt
        if self._tick_hunger >= 1.0:
            self._tick_hunger = 0.0
            self.hunger -= HUNGER_RATE
        if self._tick_thirst >= 1.0:
            self._tick_thirst = 0.0
            self.thirst -= THIRST_RATE
        self.hunger = max(0.0, self.hunger)
        self.thirst = max(0.0, self.thirst)

        base_temp = daynight.get_temperature()
        if self.near_campfire: base_temp += 25
        if self.inside_house: base_temp += 10
        self._tick_temp += dt
        if self._tick_temp >= 0.5:
            self._tick_temp = 0.0
            if self.temp < base_temp:
                self.temp = min(base_temp, self.temp + TEMP_HOT_RATE)
            elif self.temp > base_temp:
                self.temp = max(base_temp, self.temp - TEMP_COLD_RATE)
        self.temp = max(0, min(100, self.temp))

        dmg = 0.0
        if self.hunger <= 0: dmg += 2.0 * dt
        if self.thirst <= 0: dmg += 3.0 * dt
        if self.temp < 20: dmg += (20 - self.temp) * 0.15 * dt
        elif self.temp > 85: dmg += (self.temp - 85) * 0.15 * dt
        if dmg > 0:
            self.hp -= dmg
        if self.hunger > 60 and self.thirst > 60 and self.hp < self.max_hp:
            self.hp = min(self.max_hp, self.hp + 1.0 * dt)

    def _update_cooldowns(self, dt):
        if self.attack_cooldown > 0: self.attack_cooldown -= dt
        if self.attacking_timer > 0: self.attacking_timer -= dt
        if self.hurt_anim_timer > 0: self.hurt_anim_timer -= dt

    def _update_biome(self, world):
        self.in_water = (world.tile_at_pixel(self.x, self.y) == BIOME_WATER)
        self.near_campfire = world.has_campfire_near(self.x, self.y, 96)
        self.inside_house = world.inside_house(self.x, self.y)

    def use_item(self, world, game):
        if self.attack_cooldown > 0: return
        self.attack_cooldown = 0.4
        self.attacking_timer = 0.25
        idx = self.hotbar[self.hotbar_selected]
        slot = self.inventory.slots[idx] if idx < len(self.inventory.slots) else None
        if slot:
            item = slot.item_id
            if item in ("cooked_meat", "raw_meat", "berry", "fish",
                        "wheat", "carrot", "pumpkin"):
                self._eat(item)
                slot.count -= 1
                if slot.count <= 0:
                    self.inventory.slots[idx] = None
                return
            if item == "water_flask":
                self.thirst = min(self.max_thirst, self.thirst + 40)
                self.inventory.slots[idx] = None
                return
            if item in ARMOR:
                self.equip_armor(item)
                return
            if item in WEAPONS:
                self.set_weapon(item)
                self._play_sfx("attack")
                world.damage_enemies_near(self.center[0], self.center[1], 64,
                                          self.weapon_damage)
                return
        self._play_sfx("attack")
        world.damage_enemies_near(self.center[0], self.center[1], 64, self.weapon_damage)

    def _eat(self, item):
        self._play_sfx("eat")
        if item == "cooked_meat":
            self.hunger = min(self.max_hunger, self.hunger + 45)
            self.hp = min(self.max_hp, self.hp + 10)
        elif item == "raw_meat":
            self.hunger = min(self.max_hunger, self.hunger + 25)
            if random.random() < 0.3: self.hp -= 8
        elif item == "berry":
            self.hunger = min(self.max_hunger, self.hunger + 12)
            self.thirst = min(self.max_thirst, self.thirst + 4)
        elif item == "fish":
            self.hunger = min(self.max_hunger, self.hunger + 18)
        elif item in FOOD_VALUES:
            v = FOOD_VALUES[item]
            self.hunger = min(self.max_hunger, self.hunger + v["hunger"])
            self.thirst = min(self.max_thirst, self.thirst + v.get("thirst", 0))

    def interact(self, world, game):
        obj = world.find_interactable(self.center[0], self.center[1], 56)
        if obj is None: return
        kind = obj["kind"]

        if game.world.is_tent and obj.get("is_tent_exit"):
            game.exit_tent(); return
        if kind == "tent":
            game.enter_tent(); return
        if game.world.is_mine and obj.get("is_mine_exit"):
            game.exit_mine(); return
        if kind == "mine_entrance":
            game.enter_mine(); return

        if kind == "pickup":
            self.inventory.add_item(obj["item_id"], obj["count"])
            world.remove_object(obj)
            self._play_sfx("pickup")
            return

        if kind == "farm_plot":
            self._handle_farm_plot(obj, world)
            return

        if kind == "tree":
            dmg = 50 if self.inventory.count_item("axe") > 0 else 25
            obj["hp"] = obj.get("hp", 100) - dmg
            self._play_sfx("chop")
            if obj["hp"] <= 0:
                self.inventory.add_item("wood", 3)
                world.start_fall_anim(obj, direction=self.facing)
        elif kind == "rock":
            pickaxe = self.inventory.count_item("pickaxe")
            iron_pick = self.inventory.count_item("iron_pickaxe")
            dmg = 50
            if iron_pick > 0: dmg = 120
            elif pickaxe > 0: dmg = 50
            else: dmg = 10
            obj["hp"] = obj.get("hp", 120) - dmg
            self._play_sfx("mine")
            if obj["hp"] <= 0:
                self.inventory.add_item("stone", 3)
                if random.random() < 0.3:
                    self.inventory.add_item("iron_ore", 1)
                world.remove_object(obj)
        elif kind == "coal_ore":
            if self.inventory.count_item("pickaxe") + self.inventory.count_item("iron_pickaxe") <= 0:
                return
            dmg = 80 if self.inventory.count_item("iron_pickaxe") > 0 else 50
            obj["hp"] = obj.get("hp", 150) - dmg
            self._play_sfx("mine")
            if obj["hp"] <= 0:
                self.inventory.add_item("coal", 3)
                world.start_fall_anim(obj, direction=self.facing)
        elif kind in ("iron_ore_rock", "gold_ore_rock", "diamond_ore_rock"):
            has_iron_pick = self.inventory.count_item("iron_pickaxe") > 0
            if not has_iron_pick and kind != "iron_ore_rock":
                return
            dmg = 100 if has_iron_pick else 50
            obj["hp"] = obj.get("hp", 200) - dmg
            self._play_sfx("mine")
            if obj["hp"] <= 0:
                if kind == "iron_ore_rock": self.inventory.add_item("iron_ore", 4)
                elif kind == "gold_ore_rock": self.inventory.add_item("gold_ore", 3)
                elif kind == "diamond_ore_rock": self.inventory.add_item("diamond", 2)
                world.start_fall_anim(obj, direction=self.facing)
        elif kind == "bush":
            if obj.get("has_berries", True):
                self.inventory.add_item("berry", 2)
                obj["has_berries"] = False
                obj["berry_timer"] = 0.0
                self._play_sfx("pickup")
            else:
                dmg = 25 if self.inventory.count_item("axe") > 0 else 10
                obj["hp"] = obj.get("hp", 40) - dmg
                self._play_sfx("chop")
                if obj["hp"] <= 0:
                    self.inventory.add_item("wood", 1)
                    world.start_fall_anim(obj, direction=self.facing)
        elif kind == "water":
            self.thirst = min(self.max_thirst,
                              self.thirst + 35 if self.inventory.count_item("water_flask") > 0 else 15)
        elif kind == "door":
            world.toggle_door(obj)
            self._play_sfx("door")
        elif kind == "bed":
            self._sleep(game)
        elif kind == "campfire":
            if self.inventory.count_item("raw_meat") > 0:
                self.inventory.remove_item("raw_meat", 1)
                self.inventory.add_item("cooked_meat", 1)
                self._play_sfx("craft")
            elif self.inventory.count_item("fish") > 0:
                self.inventory.remove_item("fish", 1)
                self.inventory.add_item("cooked_meat", 1)
                self._play_sfx("craft")
        elif kind == "chest":
            self._play_sfx("pickup")
            self.inventory.add_item("wood", 3)
            self.inventory.add_item("stone", 2)
            self.inventory.add_item("wheat_seeds", 2)
            world.remove_object(obj)

    def _handle_farm_plot(self, b, world):
        state = b.get("state", "empty")
        if state == "empty":
            seed_ids = ["wheat_seeds", "carrot_seeds", "pumpkin_seeds"]
            for s in seed_ids:
                if self.inventory.count_item(s) > 0:
                    self.inventory.remove_item(s, 1)
                    b["state"] = "growing"
                    b["crop"] = s
                    b["growth"] = 0.0
                    self._play_sfx("pickup")
                    return
        elif state == "ripe":
            crop = b.get("crop")
            result = CROP_RESULT.get(crop)
            if result:
                yield_count = CROPS.get(crop, {}).get("yield", 1)
                self.inventory.add_item(result, yield_count)
                b["state"] = "empty"
                b["crop"] = None
                b["growth"] = 0.0
                self._play_sfx("pickup")
                return

    def _sleep(self, game):
        game.daynight.skip_to_morning()
        self.hp = min(self.max_hp, self.hp + 40)
        self.hunger = max(0, self.hunger - 15)
        self.thirst = max(0, self.thirst - 20)

    def take_damage(self, amount):
        self.hp = max(0, self.hp - amount)
        self.hurt_anim_timer = self.hurt_anim_duration
        self._play_sfx("hurt")

    def draw(self, screen, camera):
        sx, sy = camera.apply((self.x, self.y))
        cx, cy = int(sx), int(sy)
        attack_anim = 0.0
        if self.attacking_timer > 0:
            attack_anim = 1.0 - (self.attacking_timer / 0.25)
            attack_anim = math.sin(attack_anim * math.pi)
        hurt_anim = 0.0
        if self.hurt_anim_timer > 0:
            hurt_anim = self.hurt_anim_timer / self.hurt_anim_duration

        heroine.draw_heroine(screen, cx, cy, look=self.look,
                             phase=self.anim_phase, moving=self.moving,
                             facing=self.facing, blink=self.blinking,
                             eye_dir=self.eye_dir, scale=HERO_SCALE,
                             attacking=attack_anim, hurt=hurt_anim,
                             shiver=self.shiver,
                             idle_time=self.idle_time,
                             anim_phase_blend=self.anim_phase_blend)
        bar_w = 32
        bar_x, bar_y = cx - bar_w // 2, cy - self.h - 8
        pygame.draw.rect(screen, (60, 20, 20), (bar_x, bar_y, bar_w, 4))
        pygame.draw.rect(screen, RED, (bar_x, bar_y,
                                       int(bar_w * self.hp / self.max_hp), 4))

    def to_dict(self):
        return {"x": self.x, "y": self.y, "hp": self.hp, "hunger": self.hunger,
                "thirst": self.thirst, "temp": self.temp, "look": dict(self.look),
                "inventory": self.inventory.to_dict(), "hotbar": self.hotbar,
                "equipped_armor": self.equipped_armor,
                "weapon_damage": self.weapon_damage}

    def load_state(self, data):
        self.x = data.get("x", self.x); self.y = data.get("y", self.y)
        self.hp = data.get("hp", self.hp); self.hunger = data.get("hunger", self.hunger)
        self.thirst = data.get("thirst", self.thirst); self.temp = data.get("temp", self.temp)
        if "look" in data:
            self.look = heroine.normalize_look(data["look"])
        if "inventory" in data:
            self.inventory.load_dict(data["inventory"])
        self.hotbar = data.get("hotbar", self.hotbar)
        armor = data.get("equipped_armor")
        if armor:
            self.equip_armor(armor)
        if "weapon_damage" in data:
            self.weapon_damage = data["weapon_damage"]
        self.vis_hp = float(self.hp)
        self.vis_hunger = float(self.hunger)
        self.vis_thirst = float(self.thirst)
        self.vis_temp = float(self.temp)