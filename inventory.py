# inventory.py
import pygame as pg
import settings as cfg


class InventoryHUD:
    def __init__(self, player):
        self.player = player
        self.items = {"coin": 0}  # puedes agregar otros tipos si los tienes
        self.font = pg.font.SysFont("Arial", 24)

    def add(self, item_type):
        """Aumenta la cantidad de un tipo de consumible."""
        if item_type in self.items:
            self.items[item_type] += 1
        else:
            self.items[item_type] = 1

    def draw(self, screen):
        """Dibuja la HUD de inventario en pantalla."""
        x, y = 20, 20
        for item, count in self.items.items():
            text = self.font.render(f"{item.capitalize()}: {count}", True, cfg.WHITE)
            screen.blit(text, (x, y))
            y += 30
