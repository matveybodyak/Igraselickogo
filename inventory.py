"""inventory.py — инвентарь с drag&drop, стаки, крафт."""
import pygame
from settings import (
    ITEMS, STACK_MAX, INV_COLS, INV_ROWS, SLOT_SIZE, SLOT_PAD,
    RECIPES, get_font, WHITE, GRAY, DARK_GRAY, GREEN, RED, YELLOW
)
import icons


class ItemStack:
    __slots__ = ("item_id", "count")
    def __init__(self, item_id, count=1):
        self.item_id = item_id
        self.count = count
    @property
    def name(self): return ITEMS[self.item_id][0]
    @property
    def color(self): return ITEMS[self.item_id][1]
    @property
    def stackable(self): return ITEMS[self.item_id][2]
    def max_stack(self): return STACK_MAX if self.stackable else 1
    def copy(self): return ItemStack(self.item_id, self.count)


class Inventory:
    def __init__(self, cols=INV_COLS, rows=INV_ROWS):
        self.cols = cols
        self.rows = rows
        self.slots = [None] * (cols * rows)
        self.font = get_font(14, bold=True)
        self.dragging = None
        self.drag_from = None
        self.mouse_pos = (0, 0)

    def slot_rect(self, index, origin):
        r = index // self.cols
        c = index % self.cols
        x = origin[0] + c * (SLOT_SIZE + SLOT_PAD)
        y = origin[1] + r * (SLOT_SIZE + SLOT_PAD)
        return pygame.Rect(x, y, SLOT_SIZE, SLOT_SIZE)

    def grid_size(self):
        return (self.cols * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD,
                self.rows * (SLOT_SIZE + SLOT_PAD) - SLOT_PAD)

    def slot_at(self, pos, origin):
        for i in range(len(self.slots)):
            if self.slot_rect(i, origin).collidepoint(pos):
                return i
        return -1

    def add_item(self, item_id, count=1):
        stackable = ITEMS[item_id][2]
        max_stack = STACK_MAX if stackable else 1
        if stackable:
            for s in self.slots:
                if s and s.item_id == item_id and s.count < max_stack:
                    put = min(max_stack - s.count, count)
                    s.count += put
                    count -= put
                    if count == 0:
                        return 0
        for i, s in enumerate(self.slots):
            if s is None:
                put = min(max_stack, count)
                self.slots[i] = ItemStack(item_id, put)
                count -= put
                if count == 0:
                    return 0
        return count

    def count_item(self, item_id):
        return sum(s.count for s in self.slots if s and s.item_id == item_id)

    def remove_item(self, item_id, count=1):
        if self.count_item(item_id) < count:
            return False
        for i, s in enumerate(self.slots):
            if s and s.item_id == item_id:
                take = min(s.count, count)
                s.count -= take
                count -= take
                if s.count == 0:
                    self.slots[i] = None
                if count == 0:
                    return True
        return True

    def has_items(self, requires):
        return all(self.count_item(k) >= v for k, v in requires.items())

    def consume_items(self, requires):
        if not self.has_items(requires):
            return False
        for k, v in requires.items():
            self.remove_item(k, v)
        return True

    def start_drag(self, index):
        if 0 <= index < len(self.slots) and self.slots[index]:
            self.dragging = self.slots[index].copy()
            self.drag_from = index
            self.slots[index] = None

    def end_drag(self, target_index):
        if self.dragging is None:
            return
        if target_index < 0:
            if self.drag_from is not None and self.slots[self.drag_from] is None:
                self.slots[self.drag_from] = self.dragging
            else:
                self.add_item(self.dragging.item_id, self.dragging.count)
            self.dragging = None
            self.drag_from = None
            return
        target = self.slots[target_index]
        if target is None:
            self.slots[target_index] = self.dragging
        elif target.item_id == self.dragging.item_id and target.stackable:
            put = min(STACK_MAX - target.count, self.dragging.count)
            target.count += put
            self.dragging.count -= put
            if self.dragging.count > 0:
                if self.drag_from is not None and self.slots[self.drag_from] is None:
                    self.slots[self.drag_from] = self.dragging
                else:
                    self.add_item(self.dragging.item_id, self.dragging.count)
        else:
            self.slots[target_index] = self.dragging
            if self.drag_from is not None:
                self.slots[self.drag_from] = target
            else:
                self.add_item(target.item_id, target.count)
        self.dragging = None
        self.drag_from = None

    def handle_event(self, event, origin):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            idx = self.slot_at(event.pos, origin)
            if idx >= 0:
                if self.dragging is None:
                    self.start_drag(idx)
                else:
                    self.end_drag(idx)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            idx = self.slot_at(event.pos, origin)
            if idx >= 0 and self.slots[idx]:
                s = self.slots[idx]
                if s.count > 1:
                    s.count //= 2
                else:
                    self.slots[idx] = None
        elif event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos

    def _draw_count(self, screen, rect, count):
        if count > 1:
            txt = self.font.render(str(count), True, WHITE)
            bg = pygame.Surface((txt.get_width() + 4, txt.get_height()), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            screen.blit(bg, (rect.right - txt.get_width() - 6,
                             rect.bottom - txt.get_height() - 2))
            screen.blit(txt, (rect.right - txt.get_width() - 4,
                              rect.bottom - txt.get_height() - 2))

    def draw(self, screen, origin):
        for i in range(len(self.slots)):
            rect = self.slot_rect(i, origin)
            pygame.draw.rect(screen, (45, 45, 55), rect, border_radius=4)
            pygame.draw.rect(screen, (90, 90, 110), rect, 1, border_radius=4)
            s = self.slots[i]
            if s:
                inner = rect.inflate(-12, -12)
                icons.draw_item_icon(screen, s.item_id, inner)
                self._draw_count(screen, rect, s.count)

        if self.dragging is not None:
            mx, my = pygame.mouse.get_pos()
            rect = pygame.Rect(mx - SLOT_SIZE // 2, my - SLOT_SIZE // 2,
                               SLOT_SIZE, SLOT_SIZE)
            inner = rect.inflate(-12, -12)
            icons.draw_item_icon(screen, self.dragging.item_id, inner)
            self._draw_count(screen, rect, self.dragging.count)

    def to_dict(self):
        return {"cols": self.cols, "rows": self.rows,
                "slots": [{"id": s.item_id, "count": s.count} if s else None
                          for s in self.slots]}

    def load_dict(self, data):
        self.cols = data.get("cols", INV_COLS)
        self.rows = data.get("rows", INV_ROWS)
        self.slots = [None] * (self.cols * self.rows)
        for i, s in enumerate(data.get("slots", [])):
            if i >= len(self.slots):
                break
            if s:
                self.slots[i] = ItemStack(s["id"], s["count"])


class Crafting:
    @staticmethod
    def can_craft(inventory, recipe):
        return inventory.has_items(recipe["requires"])

    @staticmethod
    def craft(inventory, recipe):
        if not Crafting.can_craft(inventory, recipe):
            return False
        inventory.consume_items(recipe["requires"])
        inventory.add_item(recipe["result"], recipe["count"])
        return True

    @staticmethod
    def draw(screen, inventory, origin, selected):
        font = get_font(20)
        font_small = get_font(16)
        rects = []
        x, y = origin
        for i, rec in enumerate(RECIPES):
            rect = pygame.Rect(x, y + i * 44, 420, 40)
            ok = Crafting.can_craft(inventory, rec)
            bg = (90, 120, 70) if i == selected else ((50, 70, 50) if ok else (60, 45, 45))
            pygame.draw.rect(screen, bg, rect, border_radius=5)
            pygame.draw.rect(screen, WHITE if ok else GRAY, rect, 1, border_radius=5)
            name = font.render(rec["name"], True, WHITE if ok else GRAY)
            screen.blit(name, (rect.x + 10, rect.y + 8))
            req = ", ".join(f"{ITEMS[k][0]}×{v}" for k, v in rec["requires"].items())
            req_s = font_small.render(req, True, (200, 200, 220) if ok else (140, 140, 160))
            screen.blit(req_s, (rect.x + 160, rect.y + 12))
            rects.append(rect)
        return rects