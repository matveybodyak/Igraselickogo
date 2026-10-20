"""
audio.py — менеджер звуков: музыка + SFX.
Все файлы ищутся в assets/music/ и assets/sfx/.
Отсутствующие файлы игнорируются (игра не падает).
"""
import os
import pygame


BASE = "assets"
MUSIC_DIR = os.path.join(BASE, "music")
SFX_DIR = os.path.join(BASE, "sfx")


class AudioManager:
    def __init__(self):
        self.ok = False
        self.music_volume = 0.5
        self.sfx_volume = 0.7
        self.current_music = None
        self.sfx_cache = {}
        self.sfx_enabled = True
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.ok = True
        except Exception as e:
            print("Аудио недоступно:", e)

    # ---------- Музыка ----------
    def _find_music(self, name):
        for ext in (".ogg", ".mp3", ".wav"):
            path = os.path.join(MUSIC_DIR, name + ext)
            if os.path.exists(path):
                return path
        return None

    def play_music(self, name, volume=None, loop=-1):
        if not self.ok:
            return
        path = self._find_music(name)
        if path is None:
            return
        if self.current_music == path:
            return
        try:
            pygame.mixer.music.load(path)
            v = self.music_volume if volume is None else volume
            pygame.mixer.music.set_volume(max(0.0, min(1.0, v)))
            pygame.mixer.music.play(loop)
            self.current_music = path
        except Exception as e:
            print("Не удалось запустить музыку:", e)

    def stop_music(self):
        if not self.ok:
            return
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.current_music = None

    def set_music_volume(self, v):
        self.music_volume = max(0.0, min(1.0, v))
        if self.ok:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except Exception:
                pass

    # ---------- SFX ----------
    def _find_sfx(self, name):
        for ext in (".ogg", ".wav", ".mp3"):
            path = os.path.join(SFX_DIR, name + ext)
            if os.path.exists(path):
                return path
        return None

    def _get_sound(self, name):
        if name in self.sfx_cache:
            return self.sfx_cache[name]
        path = self._find_sfx(name)
        if path is None:
            self.sfx_cache[name] = None
            return None
        try:
            snd = pygame.mixer.Sound(path)
            snd.set_volume(self.sfx_volume)
            self.sfx_cache[name] = snd
            return snd
        except Exception:
            self.sfx_cache[name] = None
            return None

    def play_sfx(self, name):
        if not self.ok or not self.sfx_enabled:
            return
        snd = self._get_sound(name)
        if snd:
            try:
                snd.play()
            except Exception:
                pass

    def set_sfx_volume(self, v):
        self.sfx_volume = max(0.0, min(1.0, v))
        for snd in self.sfx_cache.values():
            if snd:
                snd.set_volume(self.sfx_volume)