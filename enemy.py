# enemy.py
import random
import pygame as pg
from settings import ENEMY_SPEED, ENEMY_SIZE, ENEMY_COLOR, ENEMY_MAX_HP, WHITE, RED

class Enemy(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface(ENEMY_SIZE, pg.SRCALPHA)
        self.image.fill(ENEMY_COLOR)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(self.rect.center)
        self.speed = ENEMY_SPEED
        self.max_hp = ENEMY_MAX_HP
        self.hp = ENEMY_MAX_HP
        self._flash_timer = 0.0

    def update(self, dt, player_pos):
        # perseguir al jugador
        dir_vec = (pg.math.Vector2(player_pos) - self.pos)
        if dir_vec.length_squared() > 0:
            dir_vec = dir_vec.normalize()
        self.pos += dir_vec * self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        if self._flash_timer > 0:
            self._flash_timer -= dt

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - int(dmg))
        self._flash_timer = 0.1  # pequeño flash al recibir daño

    def is_dead(self):
        return self.hp <= 0

    def draw_hp(self, surface):
        # barra de vida pequeña arriba del enemigo
        w, h = self.rect.width, 4
        x = self.rect.centerx - w // 2
        y = self.rect.top - (h + 4)
        ratio = self.hp / self.max_hp if self.max_hp else 0
        pg.draw.rect(surface, (60, 60, 60), (x, y, w, h), border_radius=2)
        pg.draw.rect(surface, (0, 220, 0), (x, y, int(w * ratio), h), border_radius=2)

    def draw(self, surface):
        # flash blanco corto cuando recibe daño
        if self._flash_timer > 0:
            temp = pg.Surface(self.rect.size, pg.SRCALPHA)
            temp.fill(WHITE)
            surface.blit(temp, self.rect.topleft, special_flags=pg.BLEND_ADD)
