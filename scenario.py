import pygame as pg
import settings as cfg


class Room:
    """Almacena la información de una sala: su mapa y los enemigos que contiene."""
    def __init__(self, map_file, enemies_to_spawn):
        self.map_file = map_file
        self.enemies_to_spawn = enemies_to_spawn

class Exit(pg.sprite.Sprite):
    """Representa la salida que aparece al limpiar un nivel."""
    def __init__(self, x, y):
        super().__init__()
        self.image = pg.Surface((cfg.TILESIZE, cfg.TILESIZE))
        self.image.fill((255, 215, 0)) # Color dorado para la salida
        self.rect = self.image.get_rect(topleft=(x, y))

    def lock(self):
        self.locked = True
        self.image.fill((100, 50, 50)) # Color rojo oscuro (cerrada)

    def unlock(self):
        self.locked = False
        self.image.fill((80, 180, 80)) # Color verde (abierta)