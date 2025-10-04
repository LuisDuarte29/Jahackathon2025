# consumable.py
import pygame as pg
import settings as cfg
import random

CONSUMABLE_TYPES = ["coin", "key", "bomb"]

class Consumable(pg.sprite.Sprite):
    def __init__(self, pos, item_type=None):
        super().__init__()
        self.item_type = item_type if item_type else random.choice(CONSUMABLE_TYPES)

        # --- imágenes simples para testeo (círculos de colores) ---
        size = 20
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        color_map = {
            "coin": (255, 215, 0),   # dorado
            "key": (192, 192, 192),  # plateado
            "bomb": (0, 0, 0)        # negro
        }
        pg.draw.circle(self.image, color_map[self.item_type], (size//2, size//2), size//2)

        self.rect = self.image.get_rect(center=pos)

    def apply(self, player):
        """Efecto al recoger el consumible"""
        if self.item_type == "coin":
            player.coins = getattr(player, "coins", 0) + 1
        elif self.item_type == "key":
            player.keys = getattr(player, "keys", 0) + 1
        elif self.item_type == "bomb":
            player.bombs = getattr(player, "bombs", 0) + 1

        # Destruir consumible al recoger
        self.kill()
