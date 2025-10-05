import pygame as pg
import settings as cfg


class Bullet(pg.sprite.Sprite):
    def __init__(self, start_pos, target_pos, damage=None, player_class="Warrior"):
        super().__init__()
        # Elegir color según la clase del jugador
        bullet_color = cfg.BULLET_COLORS.get(player_class, cfg.YELLOW)

        # Imagen de la bala
        self.image = pg.Surface(cfg.BULLET_SIZE, pg.SRCALPHA)
        self.image.fill(bullet_color)
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
        self.rect.x += int(self.vel.x * dt)
        self.rect.y += int(self.vel.y * dt)

        # Reducir vida
        self.life -= dt
        if self.life <= 0:
            self.kill()

        # Destruir si sale de la pantalla
        if (
            self.rect.right < 0
            or self.rect.left > cfg.ANCHO
            or self.rect.bottom < 0
            or self.rect.top > cfg.ALTO
        ):
            self.kill()


class EnemyBullet(pg.sprite.Sprite):
    def __init__(self, pos, target_pos, damage=10, speed=300):
        super().__init__()
        self.image = pg.Surface((8, 8))
        self.image.fill((200, 50, 50))
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(pos)
        self.target = pg.math.Vector2(target_pos)
        self.speed = speed
        self.damage = damage
        dir_vec = self.target - self.pos
        self.velocity = (
            dir_vec.normalize() * self.speed
            if dir_vec.length_squared() > 0
            else pg.math.Vector2(0, 0)
        )

    def update(self, dt):
        self.pos += self.velocity * dt
        self.rect.center = self.pos
