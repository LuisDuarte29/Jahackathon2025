# game.py
import pygame as pg
import math
import random
import settings as cfg
from player import Player
from enemy import Enemy
from menus import main_menu, pause
from hud import draw_ui, HUD


CLASS_KEYS = {pg.K_1: "Warrior", pg.K_2: "Rogue", pg.K_3: "Mage"}


class Bullet(pg.sprite.Sprite):
    def __init__(self, start_pos, target_pos, damage=10, speed=400):
        super().__init__()
        # Crear superficie con transparencia
        self.image = pg.Surface((10, 10), pg.SRCALPHA)
        # Dibujar círculo amarillo
        pg.draw.circle(self.image, cfg.YELLOW, (5, 5), 5)
        self.rect = self.image.get_rect(center=start_pos)
        
        dx = target_pos[0] - start_pos[0]
        dy = target_pos[1] - start_pos[1]
        dist = math.hypot(dx, dy)
        
        if dist == 0:
            self.vel_x = 0
            self.vel_y = 0
        else:
            self.vel_x = (dx / dist) * speed
            self.vel_y = (dy / dist) * speed
        
        self.damage = damage
        self.lifetime = 3.0  # seconds
    
    def update(self, dt):
        self.rect.x += self.vel_x * dt
        self.rect.y += self.vel_y * dt
        self.lifetime -= dt
        
        # Remove if out of bounds or lifetime expired
        if (self.rect.right < 0 or self.rect.left > cfg.WIDTH or 
            self.rect.bottom < 0 or self.rect.top > cfg.HEIGHT or 
            self.lifetime <= 0):
            self.kill()


def spawn_enemy(offscreen=True):
    """Genera un enemigo en una posición aleatoria."""
    if offscreen:
        side = random.choice(["l", "r", "t", "b"])
        if side == "l":
            x, y = -20, random.randint(0, cfg.HEIGHT)
        elif side == "r":
            x, y = cfg.WIDTH + 20, random.randint(0, cfg.HEIGHT)
        elif side == "t":
            x, y = random.randint(0, cfg.WIDTH), -20
        else:
            x, y = random.randint(0, cfg.WIDTH), cfg.HEIGHT + 20
    else:
        x, y = random.randint(50, cfg.WIDTH - 50), random.randint(50, cfg.HEIGHT - 50)
    return Enemy((x, y))


def game_over_screen(screen, clock, score, time_alive):
    """Muestra la pantalla de Game Over."""
    big_font = pg.font.SysFont("consolas,roboto,arial", 48, bold=True)
    font = pg.font.SysFont("consolas,roboto,arial", 24)
    
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_RETURN or event.key == pg.K_SPACE:
                    main_menu.loop_menu(clock, loop_juego)
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    raise SystemExit
        
        screen.fill(cfg.BG_COLOR)
        
        # Textos
        title = big_font.render("GAME OVER", True, cfg.RED)
        score_text = font.render(f"Score: {score}", True, cfg.WHITE)
        time_text = font.render(f"Tiempo: {int(time_alive)}s", True, cfg.WHITE)
        hint = font.render("Presiona ENTER para volver al menu", True, cfg.GRAY)
        hint2 = font.render("ESC para salir", True, cfg.GRAY)
        
        # Posiciones centradas
        screen.blit(title, title.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2 - 60)))
        screen.blit(score_text, score_text.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2)))
        screen.blit(time_text, time_text.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2 + 40)))
        screen.blit(hint, hint.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2 + 100)))
        screen.blit(hint2, hint2.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2 + 130)))
        
        pg.display.flip()
        clock.tick(cfg.FPS)


def class_selection_screen(screen, clock):
    font = pg.font.Font(None, 48)
    small_font = pg.font.Font(None, 32)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key in CLASS_KEYS:
                    return CLASS_KEYS[event.key]

        screen.fill(cfg.BG_COLOR)
        title = font.render("Selecciona tu clase:", True, cfg.WHITE)
        option1 = small_font.render("1 - Warrior", True, cfg.GREEN)
        option2 = small_font.render("2 - Rogue", True, cfg.GREEN)
        option3 = small_font.render("3 - Mage", True, cfg.GREEN)
        screen.blit(title, (cfg.WIDTH//2 - title.get_width()//2, cfg.HEIGHT//3))
        screen.blit(option1, (cfg.WIDTH//2 - option1.get_width()//2, cfg.HEIGHT//2))
        screen.blit(option2, (cfg.WIDTH//2 - option2.get_width()//2, cfg.HEIGHT//2 + 40))
        screen.blit(option3, (cfg.WIDTH//2 - option3.get_width()//2, cfg.HEIGHT//2 + 80))
        pg.display.flip()
        clock.tick(cfg.FPS)


def loop_juego(screen, clock):
    class_name = class_selection_screen(screen, clock)
    player = Player((cfg.WIDTH // 2, cfg.HEIGHT // 2), class_name=class_name)
    
    # Grupos de sprites
    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()
    all_sprites.add(player)

    # Crear HUD
    hud = HUD()
    
    # Enemigo inicial
    enemy = spawn_enemy(offscreen=False)
    enemies.add(enemy)
    all_sprites.add(enemy)

    # Variables de juego
    time_to_fire = 0.0
    enemy_spawn_timer = 0.0
    enemy_spawn_interval = 2.0
    jugando = True

    while jugando:
        dt = clock.tick(cfg.FPS) / 1000.0
        keys = pg.key.get_pressed()
        time_to_fire = max(0.0, time_to_fire - dt)

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    res = pause.loop_pausa(clock)
                    if res == "menu":
                        return
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if time_to_fire <= 0.0:
                    mx, my = event.pos
                    b = Bullet(player.rect.center, (mx, my), damage=player.damage)
                    bullets.add(b)
                    all_sprites.add(b)
                    time_to_fire = player.fire_cooldown

        # Actualizar HUD
        hud.update(dt)
        
        # Actualizar cooldown de golpes del jugador
        player.tick_hit_cooldown(dt, 0.5)

        # Sistema de spawn de enemigos
        enemy_spawn_timer += dt
        enemy_spawn_interval = max(0.7, 2.0 - hud.time_alive * 0.05)
        if enemy_spawn_timer >= enemy_spawn_interval:
            enemy_spawn_timer = 0.0
            new_enemy = spawn_enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # Updates
        player.update(dt, keys)
        for e in enemies:
            e.update(dt, player.rect.center)
        bullets.update(dt)

        # Colisiones: bullets -> enemies
        for b in bullets.sprites():
            hit = pg.sprite.spritecollideany(b, enemies)
            if hit:
                hit.take_damage(b.damage)
                hud.add_floating_text(f"-{b.damage}", hit.rect.center, color=(255, 180, 50))
                b.kill()
                if hit.is_dead():
                    hud.add_score(100)
                    hud.add_floating_text("+100", hit.rect.center, color=(200, 255, 130))
                    hit.kill()

        # Colisiones: enemies -> player (CON COOLDOWN)
        hits = pg.sprite.spritecollide(player, enemies, False)
        if hits and player.can_take_hit():
            damage = 12
            player.apply_damage(damage)
            player.trigger_hit_cooldown(0.5)
            hud.add_floating_text(f"-{damage}", player.rect.center, (255, 100, 100))
            
            # Empujar jugador al recibir daño
            push = pg.math.Vector2(0, 0)
            for en in hits:
                push += (pg.math.Vector2(player.rect.center) - pg.math.Vector2(en.rect.center))
            if push.length_squared() > 0:
                push = push.normalize() * 8
                player.pos += push
                # Mantener dentro de límites
                half_w, half_h = player.rect.width // 2, player.rect.height // 2
                player.pos.x = max(half_w, min(cfg.WIDTH - half_w, player.pos.x))
                player.pos.y = max(half_h, min(cfg.HEIGHT - half_h, player.pos.y))
                player.rect.center = (int(player.pos.x), int(player.pos.y))
        
        # Game over
        if player.hp <= 0:
            game_over_screen(screen, clock, hud.score, hud.time_alive)
            return  # Volver al menú principal

        # Draw
        screen.fill(cfg.BG_COLOR)
        for s in all_sprites:
            screen.blit(s.image, s.rect)
            if hasattr(s, 'draw_health_bar'):
                s.draw_health_bar(screen)
            if hasattr(s, 'draw_hp'):
                s.draw_hp(screen)
        
        # Dibujar HUD (tiempo, score, corazones y textos flotantes)
        hud.draw(screen, player)

        pg.display.flip()