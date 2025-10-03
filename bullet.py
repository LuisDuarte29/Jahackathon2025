# bullet.py
import pygame as pg
from settings import BULLET_SPEED, BULLET_SIZE, BULLET_DAMAGE, BULLET_LIFETIME, YELLOW, WIDTH, HEIGHT

class Bullet(pg.sprite.Sprite):
    def __init__(self, start_pos, target_pos):
        super().__init__()
        self.image = pg.Surface(BULLET_SIZE, pg.SRCALPHA)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=start_pos)

        # Vector hacia el objetivo (click del mouse)
        dir_vec = pg.math.Vector2(target_pos) - pg.math.Vector2(start_pos)
        if dir_vec.length_squared() == 0:
            dir_vec = pg.math.Vector2(0, -1)  # por si se hace click exactamente encima
        self.vel = dir_vec.normalize() * BULLET_SPEED

        self.life = BULLET_LIFETIME
        self.damage = BULLET_DAMAGE

    def update(self, dt):
        # Mover
        self.rect.x += int(self.vel.x * dt)
        self.rect.y += int(self.vel.y * dt)

        # Vida/expiración
        self.life -= dt
        if self.life <= 0:
            self.kill()

        # Matar si sale de pantalla
        if (self.rect.right < 0 or self.rect.left > WIDTH or
            self.rect.bottom < 0 or self.rect.top > HEIGHT):
            self.kill()
