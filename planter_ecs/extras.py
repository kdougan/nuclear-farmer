import random

import pygame as pg
from glm import vec2

# ==============================
# EXTRAS


class GameResources:
    surfs = {}
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(GameResources, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not self.surfs:
            red_rect = pg.Surface(vec2(32).to_list())
            red_rect.fill((200, 0, 0))

            green_circle = pg.Surface(vec2(32).to_list(), pg.SRCALPHA)
            pg.draw.circle(green_circle, (0, 200, 0), (16, 16), 16)

            dirt = pg.image.load("resources/dirt-0x0-32x32.png").convert()
            cog = pg.image.load("resources/cog.png").convert_alpha()

            self.surfs["red_rect"] = red_rect
            self.surfs["green_circle"] = green_circle
            self.surfs["dirt"] = dirt
            self.surfs["cog"] = cog


class TileMap:
    tiles = []
    tile_size = 0

    def __init__(self, tile_surf, tile_size):
        self.tile_size = tile_size
        self.tiles = []
        for _ in range(100):
            row = []
            for _ in range(100):
                x = random.randint(0, 5) * tile_size
                row.append(tile_surf.subsurface((x, 0), (tile_size, tile_size)))
            self.tiles.append(row)
