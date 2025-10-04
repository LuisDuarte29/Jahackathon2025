# bullet.py
import pygame as pg
import settings as cfg


class Bullet(pg.sprite.Sprite):
    def __init__(self, start_pos, target_pos, damage=None):
        super().__init__()
        # Imagen de la bala
        self.image = pg.Surface(cfg.BULLET_SIZE, pg.SRCALPHA)
        self.image.fill(cfg.YELLOW)
        self.rect = self.image.get_rect(center=start_pos)

        # Vector hacia el objetivo (click del mouse)
        dir_vec = pg.math.Vector2(target_pos) - pg.math.Vector2(start_pos)
        if dir_vec.length_squared() == 0:
            dir_vec = pg.math.Vector2(0, -1)  # evita división por cero
        self.vel = dir_vec.normalize() * cfg.BULLET_SPEED

        # Tiempo de vida
        self.life = cfg.BULLET_LIFETIME

        # Daño dinámico (por clase del jugador)
        self.damage = damage if damage is not None else cfg.BULLET_DAMAGE

    def update(self, dt):
        """Actualiza posición y vida de la bala"""
        # Movimiento proporcional al tiempo delta
        self.rect.x += int(self.vel.x * dt)
        self.rect.y += int(self.vel.y * dt)

        # Reducir vida
        self.life -= dt
        if self.life <= 0:
            self.kill()

        # Destruir si sale de la pantalla
        if (self.rect.right < 0 or self.rect.left > cfg.WIDTH or
            self.rect.bottom < 0 or self.rect.top > cfg.HEIGHT):
            self.kill()
