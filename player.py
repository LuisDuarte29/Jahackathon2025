# player.py
import pygame as pg
import settings as cfg
from sprites import load_image, slice_spritesheet, Animation

# --- Definición de clases jugables ---
CLASSES = {
    "Warrior": {"hp": 120, "speed": 220, "damage": 28, "cooldown": 0.25},
    "Rogue":   {"hp": 80,  "speed": 300, "damage": 20, "cooldown": 0.15},
    "Mage":    {"hp": 100, "speed": 260, "damage": 34, "cooldown": 0.20},
}
# -------------------------------------

# Confirmación de carga (debug)
print("PLAYER LOADED FROM:", __file__)

class Player(pg.sprite.Sprite):
    def __init__(self, pos, class_name="Warrior"):
        super().__init__()
        # Animación
        sheet = load_image("player_sheet.png")
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
        self.vel = pg.math.Vector2(0, 0)

        # --- Sistema de clases ---
        self.class_name = class_name
        stats = CLASSES.get(class_name, CLASSES["Warrior"])

        self.speed = stats["speed"]
        self.hp = stats["hp"]
        self.max_hp = stats["hp"]
        self.damage = stats["damage"]
        self.fire_cooldown = stats["cooldown"]

        self._hit_timer = 0.0

    # --- MÉTODOS DE LA CLASE (AHORA INDENTADOS CORRECTAMENTE) ---
    def update(self, dt, keys):
        self.vel = pg.math.Vector2(0, 0)
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
        
        self.vel = direction * self.speed
        
        moving = self.vel.length_squared() > 0
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
        fg_color = cfg.RED if ratio < 0.35 else cfg.WHITE
        pg.draw.rect(surface, fg_color,
                     (x, y, int(w * ratio), h), border_radius=3)

    def apply_powerup(self, powerup_type, value):
        """Aplica un power-up al jugador."""
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