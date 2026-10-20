"""
launcher.py — красивый лаунчер для Survival 2D.
Запускается двойным кликом. Проверяет Python и pygame,
при необходимости устанавливает pygame-ce, запускает main.py.
"""
import os
import sys
import subprocess
import importlib.util
import threading
import tkinter as tk
from tkinter import messagebox


# Папка, где лежит лаунчер (или .exe, если собран)
if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

MAIN_FILE = os.path.join(APP_DIR, "main.py")
SETTINGS_FILE = os.path.join(APP_DIR, "settings.json")
SAVES_DIR = os.path.join(APP_DIR, "saves")
ASSETS_DIR = os.path.join(APP_DIR, "assets")


# ---------- Утилиты ----------
def check_pygame():
    return importlib.util.find_spec("pygame") is not None


def get_pygame_version():
    try:
        import pygame
        return pygame.version.ver
    except Exception:
        return None


def install_pygame(log_callback=None):
    """Устанавливает pygame-ce. Возвращает True/False."""
    try:
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade", "pygame-ce"]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, bufsize=1,
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)
        for line in proc.stdout:
            if log_callback:
                log_callback(line.rstrip())
        proc.wait()
        return proc.returncode == 0
    except Exception as e:
        if log_callback:
            log_callback(f"Ошибка: {e}")
        return False


def find_python():
    """Ищет python.exe в системе, если лаунчер собран как .exe."""
    if not getattr(sys, "frozen", False):
        return sys.executable
    import shutil
    for cmd in ("python", "python3", "py"):
        path = shutil.which(cmd)
        if path:
            return path
    if sys.platform == "win32":
        for base in (os.path.expandvars(r"%LOCALAPPDATA%\Programs\Python"),
                     r"C:\Python313", r"C:\Python312", r"C:\Python311"):
            if os.path.isdir(base):
                for name in os.listdir(base):
                    candidate = os.path.join(base, name, "python.exe")
                    if os.path.exists(candidate):
                        return candidate
    return None


def run_game():
    if not os.path.exists(MAIN_FILE):
        messagebox.showerror(
            "Файл не найден",
            f"Не найден main.py в папке:\n{APP_DIR}\n\n"
            "Положите launcher.py рядом с main.py и остальными файлами игры."
        )
        return False
    py = find_python()
    if not py:
        messagebox.showerror(
            "Python не найден",
            "Не удалось найти Python на компьютере.\n\n"
            "Установите Python 3.10+ с python.org\n"
            "и запустите лаунчер снова."
        )
        return False
    try:
        kwargs = {}
        if sys.platform == "win32":
            kwargs["creationflags"] = subprocess.CREATE_NEW_CONSOLE
        subprocess.Popen([py, MAIN_FILE], cwd=APP_DIR, **kwargs)
        return True
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось запустить игру:\n{e}")
        return False


def open_folder(path):
    if not os.path.exists(path):
        messagebox.showinfo("Папка не найдена",
                            f"Папка ещё не создана:\n{path}")
        return
    try:
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception as e:
        messagebox.showerror("Ошибка", str(e))


# ---------- Лаунчер ----------
class Launcher:
    BG = "#0f1420"
    BG2 = "#1a2236"
    ACCENT = "#5b8def"
    ACCENT_HOVER = "#7aa5ff"
    TEXT = "#e8edf5"
    TEXT_DIM = "#8a94a8"
    SUCCESS = "#7cd67c"
    WARNING = "#f0c060"
    ERROR = "#d67c7c"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Survival 2D — Лаунчер")
        self.root.geometry("560x520")
        self.root.resizable(False, False)
        self.root.configure(bg=self.BG)
        self._center_window(560, 520)

        icon_path = os.path.join(ASSETS_DIR, "icon.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.pygame_ok = check_pygame()
        self.pygame_version = get_pygame_version() if self.pygame_ok else None

        self._build_ui()
        self._update_status()

    def _center_window(self, w, h):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw - w) // 2
        y = (sh - h) // 2
        self.root.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        # Верхний баннер
        banner = tk.Frame(self.root, bg=self.BG2, height=110)
        banner.pack(fill="x")
        banner.pack_propagate(False)
        tk.Label(banner, text="SURVIVAL 2D", font=("Arial", 32, "bold"),
                 fg=self.TEXT, bg=self.BG2).pack(pady=(18, 0))
        tk.Label(banner, text="Выживи в диком мире",
                 font=("Arial", 12), fg=self.TEXT_DIM, bg=self.BG2).pack()

        # Центральный блок — статус
        status_frame = tk.Frame(self.root, bg=self.BG)
        status_frame.pack(fill="x", padx=30, pady=(20, 10))

        self.status_icon = tk.Label(status_frame, text="●", font=("Arial", 14),
                                    fg=self.TEXT_DIM, bg=self.BG)
        self.status_icon.pack(side="left", padx=(0, 8))

        self.status_label = tk.Label(status_frame, text="Проверка...",
                                     font=("Arial", 11), fg=self.TEXT_DIM,
                                     bg=self.BG, anchor="w")
        self.status_label.pack(side="left", fill="x", expand=True)

        # Кнопки
        btn_frame = tk.Frame(self.root, bg=self.BG)
        btn_frame.pack(fill="x", padx=40, pady=(10, 10))

        self.play_btn = self._make_button(btn_frame, "▶   Играть", self._on_play,
                                          primary=True)
        self.play_btn.pack(fill="x", pady=5)

        self.install_btn = self._make_button(btn_frame, "⬇   Установить pygame",
                                             self._on_install)
        self.install_btn.pack(fill="x", pady=5)

        row = tk.Frame(btn_frame, bg=self.BG)
        row.pack(fill="x", pady=5)
        self._make_button(row, "📁  Папка игры",
                          lambda: open_folder(APP_DIR)).pack(side="left", fill="x",
                                                            expand=True, padx=(0, 3))
        self._make_button(row, "💾  Сохранения",
                          lambda: open_folder(SAVES_DIR)).pack(side="left", fill="x",
                                                              expand=True, padx=(3, 0))

        self._make_button(btn_frame, "✕   Выход", self.root.destroy,
                          danger=True).pack(fill="x", pady=(5, 0))

        # Лог (скрыт, пока не нужен)
        self.log_text = tk.Text(self.root, height=6, bg="#0a0e15", fg=self.TEXT_DIM,
                                font=("Consolas", 9), bd=0, state="disabled",
                                wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=30, pady=(10, 15))

    def _make_button(self, parent, text, command, primary=False, danger=False):
        if primary:
            bg, fg, hover = self.ACCENT, "white", self.ACCENT_HOVER
        elif danger:
            bg, fg, hover = "#2a1a1a", self.ERROR, "#3a2020"
        else:
            bg, fg, hover = self.BG2, self.TEXT, "#25304a"

        btn = tk.Button(parent, text=text, command=command,
                        font=("Arial", 12, "bold"), bg=bg, fg=fg,
                        activebackground=hover, activeforeground=fg,
                        bd=0, pady=10, cursor="hand2", relief="flat")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def _log(self, text):
        self.log_text.config(state="normal")
        self.log_text.insert("end", text + "\n")
        self.log_text.see("end")
        self.log_text.config(state="disabled")

    def _update_status(self):
        self.pygame_ok = check_pygame()
        self.pygame_version = get_pygame_version() if self.pygame_ok else None

        if not os.path.exists(MAIN_FILE):
            self.status_icon.config(fg=self.ERROR)
            self.status_label.config(text="✗ main.py не найден в папке игры",
                                     fg=self.ERROR)
            self.play_btn.config(state="disabled")
            return

        if self.pygame_ok:
            self.status_icon.config(fg=self.SUCCESS)
            self.status_label.config(
                text=f"✓ pygame {self.pygame_version} — можно играть",
                fg=self.SUCCESS)
            self.play_btn.config(state="normal")
            self.install_btn.pack_forget()
        else:
            self.status_icon.config(fg=self.WARNING)
            self.status_label.config(
                text="⚠ pygame не установлен — нажмите «Установить»",
                fg=self.WARNING)
            self.play_btn.config(state="disabled")
            if not self.install_btn.winfo_ismapped():
                self.install_btn.pack(fill="x", pady=5, before=self.play_btn)

    def _on_play(self):
        if not self.pygame_ok:
            messagebox.showwarning(
                "Нужна установка",
                "pygame не установлен.\nНажмите «Установить pygame»."
            )
            return
        if run_game():
            self.root.after(500, self.root.destroy)

    def _on_install(self):
        self.install_btn.config(state="disabled", text="Установка...")
        self._log("Установка pygame-ce...")

        def worker():
            ok = install_pygame(log_callback=lambda s: self.root.after(0, self._log, s))
            def done():
                self.install_btn.config(state="normal", text="⬇   Установить pygame")
                self._update_status()
                if ok:
                    messagebox.showinfo("Готово", "pygame установлен!\nМожно играть.")
                else:
                    messagebox.showerror(
                        "Ошибка",
                        "Не удалось установить pygame-ce.\n\n"
                        "Попробуйте вручную в командной строке:\n"
                        "pip install pygame-ce"
                    )
            self.root.after(0, done)

        threading.Thread(target=worker, daemon=True).start()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    Launcher().run()