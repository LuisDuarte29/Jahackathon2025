# powerup.py
import pygame as pg
import settings as cfg
from sprites import load_image, Animation

class PowerUp(pg.sprite.Sprite):
    """Power-ups que el jugador puede recoger en habitaciones especiales"""
    def __init__(self, pos, effect="increase_damage"):
        super().__init__()
        self.effect = effect
        # Sprite simple, se puede reemplazar con imagen real
        self.image = pg.Surface((24, 24), pg.SRCALPHA)
        if effect == "increase_damage":
            self.image.fill((255, 215, 0))  # dorado
        elif effect == "heal":
            self.image.fill((0, 255, 0))  # verde
        else:
            self.image.fill((0, 150, 255))  # azul
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(pos)

    def apply(self, player):
        """Aplica el efecto del power-up al jugador"""
        if self.effect == "increase_damage":
            player.damage += 5
        elif self.effect == "heal":
            player.hp = min(player.max_hp, player.hp + 30)
        elif self.effect == "increase_speed":
            player.speed += 50
        self.kill()
