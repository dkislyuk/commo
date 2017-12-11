# For fun only. We claim no ownership of the sprites used or the Pokemon franchise
# Please don't sue us

# Dead pikachu credit to Sfrhk678 on deviant art

import pygame

from config import SPRITE_MIN_DIM


class Pikachu(object):
    def __init__(self, health_perc):
        assert health_perc <= 1.0 and health_perc >= 0.0
        if health_perc == 0.0:
            original_img = pygame.image.load("sprites/dead_pika.png")
        else:
            original_img = pygame.image.load("sprites/pika.png")

            dark = pygame.Surface(original_img.get_size()).convert_alpha()
            dark.fill((0, 0, 0, (1.0 - health_perc) * 255))
            original_img.blit(dark, (0, 0))

        (width, height) = original_img.get_size()
        aspect_ratio = float(height) / width

        self.image = pygame.transform.scale(original_img, (SPRITE_MIN_DIM, int(aspect_ratio * SPRITE_MIN_DIM)))

    def set_loc(self, pos):
        (width, height) = self.image.get_size()

        self.rect = pygame.Rect(pos[0] - width / 2, pos[1] - height / 2, width, height)


class Pokeball(object):
    def __init__(self, health_perc):
        assert health_perc <= 1.0 and health_perc >= 0.0
        original_img = pygame.image.load("sprites/pokeball.png")

        dark = pygame.Surface(original_img.get_size()).convert_alpha()
        dark.fill((0, 0, 0, (1.0 - health_perc) * 255))
        original_img.blit(dark, (0, 0))

        (width, height) = original_img.get_size()
        aspect_ratio = float(height) / width

        self.image = pygame.transform.scale(original_img, (SPRITE_MIN_DIM, int(aspect_ratio * SPRITE_MIN_DIM)))

    def set_loc(self, pos):
        (width, height) = self.image.get_size()

        self.rect = pygame.Rect(pos[0] - width / 2, pos[1] - height / 2, width, height)
