# player.py
import pygame as pg
import settings as cfg
from sprites import load_image, slice_spritesheet, Animation

# (Temporal) confirmación de qué archivo se está cargando
print("PLAYER LOADED FROM:", __file__)

class Player(pg.sprite.Sprite):
    def __init__(self, pos):
        super().__init__()
        # IMPORTANTE: solo el nombre del archivo (sprites.py ya apunta a /assets)
        sheet = load_image("player_sheet.png")   # 4 cols x 2 filas, 64x64
        frames = slice_spritesheet(sheet, 64, 64, cols=4, rows=2)
        right_frames = frames[0:4]
        left_frames  = frames[4:8]

        target = (32, 32)
        self.anim_right = Animation(right_frames, sec_per_frame=0.12, loop=True, scale=target)
        self.anim_left  = Animation(left_frames,  sec_per_frame=0.12, loop=True, scale=target)
        self.facing = "right"
        self.anim = self.anim_right

        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(self.rect.center)

        self.speed = cfg.PLAYER_SPEED
        self.hp = cfg.PLAYER_MAX_HP
        self.max_hp = cfg.PLAYER_MAX_HP
        self._hit_timer = 0.0

    def update(self, dt, keys):
        direction = pg.math.Vector2(
            (keys[pg.K_d] or keys[pg.K_RIGHT]) - (keys[pg.K_a] or keys[pg.K_LEFT]),
            (keys[pg.K_s] or keys[pg.K_DOWN]) - (keys[pg.K_w] or keys[pg.K_UP])
        )
        if direction.length_squared() > 0:
            direction = direction.normalize()
            if direction.x < 0:
                self.facing = "left";  self.anim = self.anim_left
            elif direction.x > 0:
                self.facing = "right"; self.anim = self.anim_right

        self.pos += direction * self.speed * dt
        half_w, half_h = self.rect.width // 2, self.rect.height // 2
        self.pos.x = max(half_w, min(cfg.WIDTH - half_w, self.pos.x))
        self.pos.y = max(half_h, min(cfg.HEIGHT - half_h, self.pos.y))
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        moving = direction.length_squared() > 0
        self.anim.update(dt if moving else dt * 0.4)
        self.image = self.anim.frame()

    def apply_damage(self, dmg):
        self.hp = max(0, self.hp - int(dmg))

    def can_take_hit(self):
        return self._hit_timer <= 0

    def tick_hit_cooldown(self, dt, cooldown_s):
        self._hit_timer = max(0.0, self._hit_timer - dt)

    def trigger_hit_cooldown(self, cooldown_s):
        self._hit_timer = cooldown_s

    def draw_health_bar(self, surface):
        w, h = self.rect.width, 6
        x = self.rect.centerx - w // 2
        y = self.rect.top - (h + 8)
        pg.draw.rect(surface, cfg.GRAY, (x, y, w, h), border_radius=3)
        ratio = self.hp / self.max_hp if self.max_hp else 0
        pg.draw.rect(surface, cfg.RED if ratio < 0.35 else cfg.WHITE,
                     (x, y, int(w * ratio), h), border_radius=3)
