# player.py
import pygame as pg
from settings import GREEN, WHITE, PLAYER_SPEED, PLAYER_MAX_HP, RED, GRAY, WIDTH, HEIGHT

class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        self.image = pg.Surface((28, 28), pg.SRCALPHA)
        self.image.fill(GREEN)
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(self.rect.center)
        self.speed = PLAYER_SPEED
        self.hp = PLAYER_MAX_HP
        self.max_hp = PLAYER_MAX_HP
        self._hit_timer = 0.0  # cooldown para recibir daño

    def update(self, dt, keys):
        # Movimiento con WASD (flechas siguen habilitadas, si no querés, quitá RIGHT/LEFT/UP/DOWN)
        direction = pg.math.Vector2(
            (keys[pg.K_d] or keys[pg.K_RIGHT]) - (keys[pg.K_a] or keys[pg.K_LEFT]),
            (keys[pg.K_s] or keys[pg.K_DOWN]) - (keys[pg.K_w] or keys[pg.K_UP])
        )
        if direction.length_squared() > 0:
            direction = direction.normalize()
        self.pos += direction * self.speed * dt

        # ---- LIMITE DE MAPA (clamp dentro de la pantalla) ----
        half_w, half_h = self.rect.width // 2, self.rect.height // 2
        self.pos.x = max(half_w, min(WIDTH - half_w, self.pos.x))
        self.pos.y = max(half_h, min(HEIGHT - half_h, self.pos.y))
        # -------------------------------------------------------

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def apply_damage(self, dmg):
        self.hp = max(0, self.hp - int(dmg))

    def can_take_hit(self):
        return self._hit_timer <= 0

    def tick_hit_cooldown(self, dt, cooldown_s):
        if self._hit_timer > 0:
            self._hit_timer -= dt
        else:
            self._hit_timer = 0

    def trigger_hit_cooldown(self, cooldown_s):
        self._hit_timer = cooldown_s

    def draw_health_bar(self, surface):
        # Barra sobre el jugador
        w, h = self.rect.width, 6
        x = self.rect.centerx - w // 2
        y = self.rect.top - (h + 8)
        # fondo
        pg.draw.rect(surface, GRAY, (x, y, w, h), border_radius=3)
        # vida
        ratio = self.hp / self.max_hp if self.max_hp else 0
        pg.draw.rect(surface, RED if ratio < 0.35 else WHITE, (x, y, int(w * ratio), h), border_radius=3)
