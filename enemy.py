import pygame as pg
import settings as cfg
from sprites import load_image, slice_spritesheet, Animation
import random
from bullet import EnemyBullet

class Enemy(pg.sprite.Sprite):
    def __init__(self, pos, enemy_type="basic"):
        super().__init__()
        # --- Animación ---
        sheet = load_image("enemy_sheet.png")
        frames = slice_spritesheet(sheet, 64, 64, cols=4, rows=1)
        self.anim = Animation(frames, sec_per_frame=0.12, loop=True, scale=(32, 32))

        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)
        self.pos = pg.math.Vector2(self.rect.center)

        # --- Disparo enemigo ---
        self.can_shoot = enemy_type in ["basic", "tank"]
        self.fire_cooldown = 2.0
        self.fire_timer = self.fire_cooldown

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

    def update(self, dt, player_pos, bullets_group=None, walls_group=None):
        """Actualiza posición y comportamiento del enemigo."""
        # Movimiento hacia el jugador
        dir_vec = pg.math.Vector2(player_pos) - self.pos
        if dir_vec.length_squared() > 0:
            dir_vec = dir_vec.normalize()
        
        # Calcular nueva posición
        new_pos = self.pos + dir_vec * self.speed * dt
        new_rect = self.rect.copy()
        new_rect.center = new_pos
        
        # Verificar colisión con paredes antes de mover
        can_move = True
        if walls_group:
            for wall in walls_group:
                if new_rect.colliderect(wall.rect):
                    can_move = False
                    break
        
        # Solo mover si no hay colisión
        if can_move:
            self.pos = new_pos
            self.rect.center = (int(self.pos.x), int(self.pos.y))
        else:
            # Si no puede moverse, intentar moverse solo en X o solo en Y
            # Intentar solo X
            test_pos_x = pg.math.Vector2(new_pos.x, self.pos.y)
            test_rect_x = self.rect.copy()
            test_rect_x.center = test_pos_x
            
            can_move_x = True
            for wall in walls_group:
                if test_rect_x.colliderect(wall.rect):
                    can_move_x = False
                    break
            
            if can_move_x:
                self.pos.x = test_pos_x.x
                self.rect.centerx = int(self.pos.x)
            else:
                # Intentar solo Y
                test_pos_y = pg.math.Vector2(self.pos.x, new_pos.y)
                test_rect_y = self.rect.copy()
                test_rect_y.center = test_pos_y
                
                can_move_y = True
                for wall in walls_group:
                    if test_rect_y.colliderect(wall.rect):
                        can_move_y = False
                        break
                
                if can_move_y:
                    self.pos.y = test_pos_y.y
                    self.rect.centery = int(self.pos.y)

        # Animación y flash
        self.anim.update(dt)
        self.image = self.anim.frame()
        if self._flash_timer > 0:
            self._flash_timer -= dt

        # Disparo enemigo
        if self.can_shoot and bullets_group is not None:
            self.fire_timer -= dt
            if self.fire_timer <= 0:
                bullet = EnemyBullet(self.rect.center, player_pos, damage=self.damage)
                bullets_group.add(bullet)
                self.fire_timer = self.fire_cooldown

    def take_damage(self, dmg):
        self.hp = max(0, self.hp - int(dmg))
        self._flash_timer = 0.12

    def is_dead(self):
        return self.hp <= 0

    def draw_hp(self, surface):
        """Dibuja barra de vida del enemigo"""
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
    """Una clase para el jefe final, más grande y más fuerte."""
    def __init__(self, pos, enemy_type="boss"):
        super().__init__(pos, enemy_type)
        
        # Sobrescribir las estadísticas para el jefe
        self.speed = cfg.ENEMY_SPEED * 0.8
        self.max_hp = cfg.ENEMY_MAX_HP * 3
        self.damage = 40
        self.hp = self.max_hp
        
        # Hacer el sprite del jefe más grande
        self.anim = Animation(self.anim.frames, sec_per_frame=0.12, loop=True, scale=(96, 96))
        self.image = self.anim.frame()
        self.rect = self.image.get_rect(center=pos)

    def draw_hp(self, surface):
        """Barra de vida más grande y prominente para el jefe."""
        w, h = self.rect.width * 1.5, 12
        x = self.rect.centerx - w // 2
        y = self.rect.top - (h + 10)
        ratio = self.hp / self.max_hp if self.max_hp else 0
        
        pg.draw.rect(surface, (60, 60, 60), (x, y, w, h), border_radius=4)
        pg.draw.rect(surface, (220, 0, 0), (x, y, int(w * ratio), h), border_radius=4)