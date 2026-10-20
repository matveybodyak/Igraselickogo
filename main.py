"""main.py — точка входа."""
import os
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, SAVE_DIR
from game import Game


def main():
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)

    try:
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
    except Exception:
        pass

    pygame.init()
    pygame.display.set_caption("Survival 2D — выживание")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()

    game = Game(screen)

    running = True
    while running and game.running:
        dt = clock.tick(FPS) / 1000.0
        if not game.handle_events():
            break
        game.update(dt)
        game.draw()
        pygame.display.flip()

    pygame.mixer.music.stop()
    pygame.quit()


if __name__ == "__main__":
    main()