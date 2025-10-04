# enemy.py
import pygame as pg
import settings as cfg
from sprites import load_image, slice_spritesheet, Animation

class Enemy(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # IMPORTANTE: solo el nombre del archivo
        sheet = load_image("enemy_sheet.png")  # 4 cols x 1 fila, 64x64
        frames = slice_spritesheet(sheet, 64, 64, cols=4, rows=1)
        self.anim = Animation(frames, sec_per_frame=0.12, loop=True, scale=(32, 32))

        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(self.rect.center)

        self.speed = cfg.ENEMY_SPEED
        self.max_hp = cfg.ENEMY_MAX_HP
        self.hp = cfg.ENEMY_MAX_HP
        self._flash_timer = 0.0

    def update(self, dt, player_pos):
        dir_vec = (pg.math.Vector2(player_pos) - self.pos)
        if dir_vec.length_squared() > 0:
            dir_vec = dir_vec.normalize()
        self.pos += dir_vec * self.speed * dt
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        self.anim.update(dt)
        self.image = self.anim.frame()

        if self._flash_timer > 0:
            self._flash_timer -= dt

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - int(dmg))
        self._flash_timer = 0.1

    def is_dead(self):
        return self.hp <= 0

    def draw_hp(self, surface):
        w, h = self.rect.width, 4
        x = self.rect.centerx - w // 2
        y = self.rect.top - (h + 4)
        ratio = self.hp / self.max_hp if self.max_hp else 0
        pg.draw.rect(surface, (60, 60, 60), (x, y, w, h), border_radius=2)
        pg.draw.rect(surface, (0, 220, 0), (x, y, int(w * ratio), h), border_radius=2)

    def draw(self, surface):
        if self._flash_timer > 0:
            temp = pg.Surface(self.rect.size, pg.SRCALPHA)
            temp.fill((255, 255, 255, 100))
            surface.blit(temp, self.rect.topleft, special_flags=pg.BLEND_ADD)
