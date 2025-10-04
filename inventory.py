# inventory.py
import pygame as pg
import settings as cfg

class InventoryHUD:
    """HUD para mostrar consumibles del jugador: monedas, llaves y bombas"""
    def __init__(self, player):
        self.player = player
        # Conteo inicial
        self.coins = 0
        self.keys = 0
        self.bombs = 0
        # Cargar íconos (puedes reemplazar con tus sprites)
        self.icon_coin = pg.Surface((24, 24))
        self.icon_coin.fill((255, 215, 0))  # amarillo para moneda
        self.icon_key = pg.Surface((24, 24))
        self.icon_key.fill((0, 255, 0))     # verde para llave
        self.icon_bomb = pg.Surface((24, 24))
        self.icon_bomb.fill((255, 0, 0))    # rojo para bomba
        # Fuente para números
        self.font = pg.font.Font(None, 24)

    def add(self, item_type, amount=1):
        """Incrementa la cantidad de un tipo de consumible"""
        if item_type == "coin":
            self.coins += amount
        elif item_type == "key":
            self.keys += amount
        elif item_type == "bomb":
            self.bombs += amount

    def draw(self, surface):
        """Dibuja el HUD en la esquina superior izquierda"""
        x, y = 10, 10

        # Monedas
        surface.blit(self.icon_coin, (x, y))
        text = self.font.render(str(self.coins), True, cfg.WHITE)
        surface.blit(text, (x + 28, y + 2))

        # Llaves
        surface.blit(self.icon_key, (x, y + 32))
        text = self.font.render(str(self.keys), True, cfg.WHITE)
        surface.blit(text, (x + 28, y + 34))

        # Bombas
        surface.blit(self.icon_bomb, (x, y + 64))
        text = self.font.render(str(self.bombs), True, cfg.WHITE)
        surface.blit(text, (x + 28, y + 66))
