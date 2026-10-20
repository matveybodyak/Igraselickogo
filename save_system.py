"""save_system.py — сохранение/загрузка со всеми локациями."""
import json
import os
import datetime
from settings import SAVE_DIR


def _ensure():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def list_saves():
    _ensure()
    result = []
    for fname in sorted(os.listdir(SAVE_DIR)):
        if not fname.endswith(".json"):
            continue
        path = os.path.join(SAVE_DIR, fname)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            meta = data.get("meta", {})
            result.append({"file": path,
                           "name": f"{meta.get('name', fname)}  [{meta.get('date', '')}]"})
        except Exception:
            continue
    return result


def save_game(game, name=None):
    _ensure()
    if name is None:
        name = f"save_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
    filename = os.path.join(SAVE_DIR, f"{name}.json")

    # Данные всех локаций
    worlds_data = {}
    for loc_name, world in getattr(game, "worlds", {}).items():
        worlds_data[loc_name] = world.to_dict()

    data = {
        "meta": {"name": name,
                 "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                 "version": 4},
        "current_location": game.current_location,
        "locations": worlds_data,
        # позиция игрока в каждой локации
        "player_positions": {k: list(v) for k, v in getattr(game, "player_positions", {}).items()},
        "player": game.player.to_dict(),
        "time": game.daynight.to_dict(),
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return filename


def load_game(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)