import pygame as pg
import random
import settings as cfg
from sprites import load_image, slice_spritesheet, Animation
from bullet import EnemyBullet


class Enemy(pg.sprite.Sprite):
    DIRECTIONS = ["norte", "sur", "este", "oeste"]

    def __init__(self, pos, enemy_type="basic"):
        super().__init__()
        self.enemy_type = enemy_type
        self.pos = pg.math.Vector2(pos)

        # --- Stats según tipo ---
        if enemy_type == "basic":
            self.speed = cfg.ENEMY_SPEED + random.randint(-20, 20)
            self.max_hp = cfg.ENEMY_MAX_HP
            self.damage = 10
            self.can_shoot = True
            self.fire_cooldown = 1.5
        elif enemy_type == "fast":
            self.speed = cfg.ENEMY_SPEED * 1.5
            self.max_hp = int(cfg.ENEMY_MAX_HP * 0.6)
            self.damage = 8
            self.can_shoot = False
            self.fire_cooldown = 0
        elif enemy_type == "tank":
            self.speed = cfg.ENEMY_SPEED * 0.6
            self.max_hp = int(cfg.ENEMY_MAX_HP * 2)
            self.damage = 20
            self.can_shoot = True
            self.fire_cooldown = 2.5
        else:
            self.speed = cfg.ENEMY_SPEED
            self.max_hp = cfg.ENEMY_MAX_HP
            self.damage = 10
            self.can_shoot = False
            self.fire_cooldown = 0

        self.hp = self.max_hp
        self._flash_timer = 0.0
        self.fire_timer = self.fire_cooldown

        # --- Animaciones por dirección ---
        self.animations = {}
        for dir_name in self.DIRECTIONS:
            try:
                sheet = load_image(f"assets/enemy_{enemy_type}_{dir_name}.png")
                cols = 2 if sheet.get_width() > sheet.get_height() else 1
                rows = 1
                frame_w = sheet.get_width() // cols
                frame_h = sheet.get_height() // rows
                target_size = (frame_w * 2, frame_h * 2)
                frames = slice_spritesheet(sheet, frame_w, frame_h, cols, rows)
                self.animations[dir_name] = Animation(
                    frames, sec_per_frame=0.12, loop=True, scale=target_size
                )
            except Exception as e:
                print(f"[WARN] No se pudo cargar '{enemy_type}' '{dir_name}': {e}")

        # Fallback: si faltan animaciones, llenamos con un sprite rojo
        for dir_name in self.DIRECTIONS:
            if dir_name not in self.animations:
                surf = pg.Surface((32, 32))
                surf.fill((200, 50, 50))
                self.animations[dir_name] = Animation([surf], sec_per_frame=1, loop=True)

        # Estado inicial
        self.facing = "sur"
        self.anim = self.animations[self.facing]
        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)
        self.vel = pg.math.Vector2(0, 0)

        print(
            f"[DEBUG] Enemy '{enemy_type}' creado en {pos} | HP: {self.hp} | Vel: {self.speed} | Daño: {self.damage}"
        )

    def update(self, dt, player_pos, bullets_group=None, walls_group=None):
        dir_vec = pg.math.Vector2(player_pos) - self.pos
        if dir_vec.length_squared() > 0:
            dir_vec = dir_vec.normalize()
            # Cambiar animación según dirección
            if abs(dir_vec.y) > abs(dir_vec.x):
                self.facing = "norte" if dir_vec.y < 0 else "sur"
            else:
                self.facing = "oeste" if dir_vec.x < 0 else "este"

        # Siempre asegurarse de tener animación válida
        self.anim = self.animations.get(self.facing, self.animations["sur"])

        # Movimiento
        new_pos = self.pos + dir_vec * self.speed * dt
        new_rect = self.rect.copy()
        new_rect.center = new_pos
        can_move = True
        if walls_group:
            for wall in walls_group:
                if new_rect.colliderect(wall.rect):
                    can_move = False
                    break
        if can_move:
            self.pos = new_pos
        else:
            # Intentar solo X
            test_pos_x = pg.math.Vector2(new_pos.x, self.pos.y)
            test_rect_x = self.rect.copy()
            test_rect_x.center = test_pos_x
            if not any(test_rect_x.colliderect(wall.rect) for wall in walls_group):
                self.pos.x = test_pos_x.x
            else:
                # Intentar solo Y
                test_pos_y = pg.math.Vector2(self.pos.x, new_pos.y)
                test_rect_y = self.rect.copy()
                test_rect_y.center = test_pos_y
                if not any(test_rect_y.colliderect(wall.rect) for wall in walls_group):
                    self.pos.y = test_pos_y.y
        self.rect.center = (int(self.pos.x), int(self.pos.y))

        # Animación y flash
        self.anim.update(dt)
        self.image = self.anim.frame()
        if self._flash_timer > 0:
            self._flash_timer -= dt

        # Disparo
        if self.can_shoot and bullets_group is not None:
            self.fire_timer -= dt
            if self.fire_timer <= 0:
                bullet = EnemyBullet(self.rect.center, player_pos, damage=self.damage)
                bullets_group.add(bullet)
                self.fire_timer = self.fire_cooldown
                print(f"[DEBUG] Enemy '{self.enemy_type}' disparó una bala")

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - int(dmg))
        self._flash_timer = 0.12
        print(
            f"[DEBUG] Enemy '{self.enemy_type}' recibió {dmg} de daño | HP restante: {self.hp}"
        )

    def is_dead(self):
        dead = self.hp <= 0
        if dead:
            print(f"[DEBUG] Enemy '{self.enemy_type}' ha muerto")
        return dead

    def draw_hp(self, surface):
        w, h = self.rect.width, 4
        x = self.rect.centerx - w // 2
        y = self.rect.top - (h + 4)
        ratio = self.hp / self.max_hp if self.max_hp else 0
        pg.draw.rect(surface, (60, 60, 60), (x, y, w, h), border_radius=2)
        pg.draw.rect(
            surface,
            (0, 220, 0) if ratio > 0.35 else (220, 50, 50),
            (x, y, int(w * ratio), h),
            border_radius=2,
        )


class Boss(Enemy):
    def __init__(self, pos):
        super().__init__(pos, enemy_type="boss")
        # Stats del boss
        self.speed = cfg.ENEMY_SPEED * 0.8
        self.max_hp = cfg.ENEMY_MAX_HP * 3
        self.hp = self.max_hp
        self.damage = 40
        self.can_shoot = True
        self.fire_cooldown = 1.0
        self.fire_timer = self.fire_cooldown

        # Escalar todas las animaciones del boss a 96x96
        for dir_name in self.DIRECTIONS:
            anim = self.animations[dir_name]
            anim.frames = [pg.transform.smoothscale(f, (96, 96)) for f in anim.frames]

        # Estado inicial
        self.anim = self.animations.get(self.facing, self.animations["sur"])
        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)

        print(
            f"[DEBUG] Boss creado en {pos} | HP: {self.hp} | Vel: {self.speed} | Daño: {self.damage}"
        )
