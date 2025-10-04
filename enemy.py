# enemy.py
import pygame as pg
import settings as cfg
from sprites import load_image, slice_spritesheet, Animation
import random

class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, enemy_type="basic"):
        super().__init__()
        # --- Animación ---
        sheet = load_image("enemy_sheet.png")  # 4 cols x 1 fila, 64x64
        frames = slice_spritesheet(sheet, 64, 64, cols=4, rows=1)
        self.anim = Animation(frames, sec_per_frame=0.12, loop=True, scale=(32, 32))

        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(self.rect.center)

        # --- Stats según tipo ---
        if enemy_type == "basic":
            self.speed = cfg.ENEMY_SPEED + random.randint(-20, 20)
            self.max_hp = cfg.ENEMY_MAX_HP
            self.damage = 10
        elif enemy_type == "fast":
            self.speed = cfg.ENEMY_SPEED * 1.5
            self.max_hp = int(cfg.ENEMY_MAX_HP * 0.6)
            self.damage = 8
        elif enemy_type == "tank":
            self.speed = cfg.ENEMY_SPEED * 0.6
            self.max_hp = int(cfg.ENEMY_MAX_HP * 2)
            self.damage = 20
        else:
            self.speed = cfg.ENEMY_SPEED
            self.max_hp = cfg.ENEMY_MAX_HP
            self.damage = 10

        self.hp = self.max_hp
        self._flash_timer = 0.0
        self.enemy_type = enemy_type

# enemy.py (dentro de la clase Enemy)

    def update(self, dt, player_pos):
        """Actualiza la posición del enemigo para que siga al jugador."""
        # Vector hacia la posición del jugador
        dir_vec = pg.math.Vector2(player_pos) - self.pos
        if dir_vec.length_squared() > 0:
            dir_vec = dir_vec.normalize()
        self.pos += dir_vec * self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Actualizar animación
        self.anim.update(dt)
        self.image = self.anim.frame()

        # Efecto de flash al recibir daño
        if self._flash_timer > 0:
            self._flash_timer -= dt
    def take_damage(self, dmg):
        self.hp = max(0, self.hp - int(dmg))
        self._flash_timer = 0.12  # flash al recibir daño

    def is_dead(self):
        return self.hp <= 0

    def draw_hp(self, surface):
        """Dibuja barra de vida del enemigo"""
        w, h = self.rect.width, 4
        x = self.rect.centerx - w // 2
        y = self.rect.top - (h + 4)
        ratio = self.hp / self.max_hp if self.max_hp else 0
        pg.draw.rect(surface, (60, 60, 60), (x, y, w, h), border_radius=2)
        pg.draw.rect(surface, (0, 220, 0) if ratio > 0.35 else (220, 50, 50),
                     (x, y, int(w * ratio), h), border_radius=2)

    def draw(self, surface):
        """Dibuja efecto flash si recibió daño"""
        if self._flash_timer > 0:
            temp = pg.Surface(self.rect.size, pg.SRCALPHA)
            temp.fill((255, 255, 255, 120))
            surface.blit(temp, self.rect.topleft, special_flags=pg.BLEND_ADD)
