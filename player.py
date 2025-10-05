import pygame as pg
import settings as cfg
from sprites import load_image, slice_spritesheet, Animation
from bullet import Bullet  # Sistema de balas

CLASSES = {
    "Juggernaut": {"hp": 120, "speed": 220, "damage": 28, "cooldown": 0.25},
    "Assault": {"hp": 80, "speed": 300, "damage": 20, "cooldown": 0.15},
    "Blaster": {"hp": 100, "speed": 260, "damage": 34, "cooldown": 0.20},
}

PLAYER_SCALE = (32, 32)

print("PLAYER LOADED FROM:", __file__)

class Player(pg.sprite.Sprite):
    def __init__(self, pos, class_name="Juggernaut"):
        super().__init__()
        self.class_name = class_name

        if class_name == "Juggernaut":
            frame_w, frame_h = 21, 11
            cols, rows = 4, 1
            base_path = "assets/juggernaut_"
            spf = 0.12
        elif class_name == "Assault":
            frame_w, frame_h = 48, 64
            cols, rows = 3, 1
            base_path = "assets/assault_"
            spf = 0.15
        elif class_name == "Blaster":
            frame_w, frame_h = 21, 11
            cols, rows = 4, 1
            base_path = "assets/blaster_"
            spf = 0.12
        else:
            raise ValueError(f"Clase desconocida: {class_name}")

        self.anim_up = Animation(
            slice_spritesheet(load_image(f"{base_path}norte.png"), frame_w, frame_h, cols, rows),
            sec_per_frame=spf,
            loop=True,
            scale=PLAYER_SCALE,
        )
        self.anim_down = Animation(
            slice_spritesheet(load_image(f"{base_path}sur.png"), frame_w, frame_h, cols, rows),
            sec_per_frame=spf,
            loop=True,
            scale=PLAYER_SCALE,
        )
        self.anim_right = Animation(
            slice_spritesheet(load_image(f"{base_path}este.png"), frame_w, frame_h, cols, rows),
            sec_per_frame=spf,
            loop=True,
            scale=PLAYER_SCALE,
        )
        self.anim_left = Animation(
            slice_spritesheet(load_image(f"{base_path}oeste.png"), frame_w, frame_h, cols, rows),
            sec_per_frame=spf,
            loop=True,
            scale=PLAYER_SCALE,
        )

        self.facing = "down"
        self.anim = self.anim_down
        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(self.rect.center)
        self.vel = pg.math.Vector2(0, 0)

        stats = CLASSES.get(class_name, CLASSES["Juggernaut"])
        self.speed = stats["speed"]
        self.hp = stats["hp"]
        self.max_hp = stats["hp"]
        self.damage = stats["damage"]
        self.fire_cooldown = stats["cooldown"]

        self._hit_timer = 0.0
        self._shoot_timer = 0.0

    # --- MOVIMIENTO Y ANIMACIÓN CON PAREDES ---
    def update(self, dt, keys, walls_group):
        self.vel = pg.math.Vector2(0, 0)
        direction = pg.math.Vector2(
            (keys[pg.K_d] or keys[pg.K_RIGHT]) - (keys[pg.K_a] or keys[pg.K_LEFT]),
            (keys[pg.K_s] or keys[pg.K_DOWN]) - (keys[pg.K_w] or keys[pg.K_UP]),
        )

        if direction.length_squared() > 0:
            direction = direction.normalize()
            if abs(direction.y) > abs(direction.x):
                self.facing = "up" if direction.y < 0 else "down"
            else:
                self.facing = "left" if direction.x < 0 else "right"

            self.anim = getattr(self, f"anim_{self.facing}")
            self.anim.update(dt)
            self.image = self.anim.frame()
        else:
            self.image = self.anim.frames[0]

        # Movimiento con colisiones
        # Eje X
        self.pos.x += direction.x * self.speed * dt
        self.rect.centerx = round(self.pos.x)
        collided_x = pg.sprite.spritecollide(self, walls_group, False)
        for wall in collided_x:
            if direction.x > 0:
                self.rect.right = wall.rect.left
            elif direction.x < 0:
                self.rect.left = wall.rect.right
            self.pos.x = self.rect.centerx

        # Eje Y
        self.pos.y += direction.y * self.speed * dt
        self.rect.centery = round(self.pos.y)
        collided_y = pg.sprite.spritecollide(self, walls_group, False)
        for wall in collided_y:
            if direction.y > 0:
                self.rect.bottom = wall.rect.top
            elif direction.y < 0:
                self.rect.top = wall.rect.bottom
            self.pos.y = self.rect.centery

        self.vel = direction * self.speed

        # Cooldown de disparos
        if self._shoot_timer > 0:
            self._shoot_timer -= dt

    # --- RESTO DE MÉTODOS (shoot, apply_damage, tick_hit_cooldown, draw_health_bar...) ---
    def shoot(self, target_pos, bullet_group):
        if self._shoot_timer <= 0:
            bullet = Bullet(
                start_pos=self.rect.center,
                target_pos=target_pos,
                damage=self.damage,
                player_class=self.class_name,
            )
            bullet_group.add(bullet)
            self._shoot_timer = self.fire_cooldown

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
        fg_color = cfg.RED if ratio < 0.35 else cfg.WHITE
        pg.draw.rect(surface, fg_color, (x, y, int(w * ratio), h), border_radius=3)

    def apply_powerup(self, powerup_type, value):
        if powerup_type == "hp":
            self.hp = min(self.max_hp, self.hp + value)
        elif powerup_type == "max_hp":
            self.max_hp += value
            self.hp = min(self.hp + value, self.max_hp)
        elif powerup_type == "speed":
            self.speed += value
        elif powerup_type == "damage":
            self.damage += value
        elif powerup_type == "cooldown":
            self.fire_cooldown = max(0.05, self.fire_cooldown - value)
        else:
            print(f"[WARN] Power-up desconocido: {powerup_type}")
