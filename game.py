# game.py
import pygame as pg
import math
import random
import settings as cfg
from player import Player
from enemy import Enemy
from bullet import Bullet
from powerup import PowerUp
from consumable import Consumable
from menus import main_menu, pause
from inventory import InventoryHUD
from hud import HUD

# --- Constantes del juego ---
CLASS_KEYS = {pg.K_1: "Warrior", pg.K_2: "Rogue", pg.K_3: "Mage"}
ENEMY_TYPES = ["basic", "fast", "tank"]
POWERUP_LOCATIONS = [(200, 200), (cfg.WIDTH - 200, 200), (cfg.WIDTH / 2, cfg.HEIGHT - 150)]


def spawn_enemy(offscreen=True):
    """Genera un enemigo de un tipo aleatorio fuera de la pantalla."""
    enemy_type = random.choice(ENEMY_TYPES)
    if offscreen:
        side = random.choice(["l", "r", "t", "b"])
        if side == "l": pos = (-30, random.randint(0, cfg.HEIGHT))
        elif side == "r": pos = (cfg.WIDTH + 30, random.randint(0, cfg.HEIGHT))
        elif side == "t": pos = (random.randint(0, cfg.WIDTH), -30)
        else: pos = (random.randint(0, cfg.WIDTH), cfg.HEIGHT + 30)
    else:
        pos = (random.randint(50, cfg.WIDTH - 50), random.randint(50, cfg.HEIGHT - 50))
    return Enemy(pos, enemy_type=enemy_type)


def game_over_screen(screen, clock, score, time_alive):
    """Muestra la pantalla de Game Over."""
    big_font = pg.font.SysFont("consolas,roboto,arial", 48, bold=True)
    font = pg.font.SysFont("consolas,roboto,arial", 24)
    
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit(); raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_RETURN, pg.K_SPACE]:
                    main_menu.loop_menu(clock, loop_juego)
                    return
                if event.key == pg.K_ESCAPE:
                    pg.quit(); raise SystemExit
        
        screen.fill(cfg.BG_COLOR)
        title = big_font.render("GAME OVER", True, cfg.RED)
        score_txt = font.render(f"Score: {score}", True, cfg.WHITE)
        time_txt = font.render(f"Tiempo: {int(time_alive)}s", True, cfg.WHITE)
        hint = font.render("Presiona ENTER para volver al menu", True, cfg.GRAY)
        
        screen.blit(title, title.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2 - 60)))
        screen.blit(score_txt, score_txt.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2)))
        screen.blit(time_txt, time_txt.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2 + 40)))
        screen.blit(hint, hint.get_rect(center=(cfg.WIDTH//2, cfg.HEIGHT//2 + 100)))
        pg.display.flip()
        clock.tick(cfg.FPS)


def class_selection_screen(screen, clock):
    """Pantalla para seleccionar la clase del jugador."""
    font = pg.font.Font(None, 48)
    small_font = pg.font.Font(None, 32)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit(); raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key in CLASS_KEYS:
                    return CLASS_KEYS[event.key]

        screen.fill(cfg.BG_COLOR)
        title = font.render("Selecciona tu clase:", True, cfg.WHITE)
        opts = [small_font.render(f"{i+1} - {cls}", True, cfg.GREEN) for i, cls in enumerate(CLASS_KEYS.values())]
        screen.blit(title, (cfg.WIDTH//2 - title.get_rect().width//2, cfg.HEIGHT//3))
        for i, opt in enumerate(opts):
             screen.blit(opt, (cfg.WIDTH//2 - opt.get_rect().width//2, cfg.HEIGHT//2 + i*40))
        pg.display.flip()
        clock.tick(cfg.FPS)


def loop_juego(screen, clock):
    """Bucle principal del juego."""
    class_name = class_selection_screen(screen, clock)
    player = Player((cfg.WIDTH // 2, cfg.HEIGHT // 2), class_name=class_name)
    
    hud = HUD()
    inventory_hud = InventoryHUD(player)

    all_sprites = pg.sprite.Group(player)
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()
    powerups = pg.sprite.Group()
    consumables = pg.sprite.Group()
    
    time_to_fire = 0.0
    enemy_spawn_timer = 2.0
    powerups_spawned = False
    
    while True:
        dt = clock.tick(cfg.FPS) / 1000.0
        keys = pg.key.get_pressed()
        time_to_fire = max(0.0, time_to_fire - dt)

        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit(); raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if pause.loop_pausa(clock) == "menu": return
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and time_to_fire <= 0.0:
                b = Bullet(player.rect.center, event.pos, damage=player.damage)
                bullets.add(b); all_sprites.add(b)
                time_to_fire = player.fire_cooldown

        # --- Actualizaciones ---
        hud.update(dt)
        player.tick_hit_cooldown(dt, 0.5)
        player.update(dt, keys)
        # Los enemigos ahora solo necesitan la posición del jugador para seguirlo
        enemies.update(dt, player.rect.center)
        bullets.update(dt)

        # --- Lógica de Spawn ---
        enemy_spawn_timer += dt
        enemy_spawn_interval = max(0.5, 3.0 - hud.time_alive * 0.04)
        if enemy_spawn_timer >= enemy_spawn_interval:
            enemy_spawn_timer = 0.0
            new_enemy = spawn_enemy()
            enemies.add(new_enemy); all_sprites.add(new_enemy)

        if not powerups_spawned and hud.time_alive > 1.0:
            for pos in POWERUP_LOCATIONS:
                p = PowerUp(pos)
                powerups.add(p); all_sprites.add(p)
            powerups_spawned = True

        # --- Lógica de Colisiones ---
        # ARREGLO 1: Colisión Jugador <-> Enemigos (movido aquí desde enemy.py)
        collided_enemies = pg.sprite.spritecollide(player, enemies, False)
        if collided_enemies and player.can_take_hit():
            for enemy in collided_enemies:
                player.apply_damage(enemy.damage)
                # ARREGLO 2: Añadir texto flotante de daño al jugador
                hud.add_floating_text(f"-{enemy.damage}", player.rect.center, (255, 100, 100))
            player.trigger_hit_cooldown(0.5)

        # Balas contra enemigos
        for bullet in bullets:
            hit_enemy = pg.sprite.spritecollideany(bullet, enemies)
            if hit_enemy:
                hit_enemy.take_damage(bullet.damage)
                hud.add_floating_text(f"-{bullet.damage}", hit_enemy.rect.center, (255, 180, 50))
                bullet.kill()
                if hit_enemy.is_dead():
                    hud.add_score(100)
                    hud.add_floating_text("+100", hit_enemy.rect.center, (200, 255, 130))
                    c = Consumable(hit_enemy.rect.center)
                    consumables.add(c); all_sprites.add(c)
                    hit_enemy.kill()

        # Jugador contra consumibles
        picked_consumables = pg.sprite.spritecollide(player, consumables, True)
        for item in picked_consumables:
            inventory_hud.add(item.item_type)
            hud.add_floating_text(f"+1 {item.item_type}", item.rect.center, cfg.WHITE)

        # Jugador contra power-ups
        picked_powerups = pg.sprite.spritecollide(player, powerups, True)
        for p_up in picked_powerups:
            p_up.apply(player)
            hud.add_floating_text(p_up.effect.replace("_", " ").title(), p_up.rect.center, (255,215,0))

        if player.hp <= 0:
            game_over_screen(screen, clock, hud.score, hud.time_alive)
            return

        # --- Dibujado en pantalla ---
        screen.fill(cfg.BG_COLOR)
        for s in all_sprites:
            screen.blit(s.image, s.rect)
            # ARREGLO 3: Llamar a la barra de vida del jugador
            if hasattr(s, 'draw_health_bar'): s.draw_health_bar(screen)
            if hasattr(s, 'draw_hp'): s.draw_hp(screen)
        
        hud.draw(screen, player)
        inventory_hud.draw(screen)

        pg.display.flip()