import pygame as pg
import settings as cfg
import random

class Tile(pg.sprite.Sprite):
    def __init__(self, x, y, width, height, tile_type='wall'):
        super().__init__()
        self.tile_type = tile_type
        self.image = pg.Surface((width, height))
        if self.tile_type == 'wall':
            # Puedes reemplazar esto con una imagen de muro más adelante
            self.image.fill(cfg.GRAY)
        else:
            self.image.fill(cfg.BG_COLOR)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Map:
    def __init__(self):
        # 1. Calcular cuántas baldosas caben en la pantalla
        self.tiles_x = cfg.ANCHO // cfg.TILESIZE
        self.tiles_y = cfg.ALTO // cfg.TILESIZE

        self.width = self.tiles_x * cfg.TILESIZE
        self.height = self.tiles_y * cfg.TILESIZE

        # 2. Generar el mapa dinámicamente
        self.data = []
        for r in range(self.tiles_y):
            row = []
            for c in range(self.tiles_x):
                # 3. Poner muros ('1') en los bordes y suelo ('0') en el centro
                if r == 0 or r == self.tiles_y - 1 or c == 0 or c == self.tiles_x - 1:
                    row.append('1')
                else:
                    # Opcional: Para que no sea un cuarto vacío, podemos añadir
                    # algunos muros internos de forma aleatoria.
                    if random.random() < 0.04: # 4% de probabilidad de que sea un muro
                         row.append('1')
                    else:
                         row.append('0')
            self.data.append("".join(row))

    def render(self, surface):
        for row, tiles in enumerate(self.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    pg.draw.rect(surface, cfg.GRAY, (col * cfg.TILESIZE, row * cfg.TILESIZE, cfg.TILESIZE, cfg.TILESIZE))

    def make_map(self):
        self.walls = pg.sprite.Group()
        for row, tiles in enumerate(self.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    self.walls.add(Tile(col * cfg.TILESIZE, row * cfg.TILESIZE, cfg.TILESIZE, cfg.TILESIZE))
        return self.walls