# game.py
import pygame as pg
import random
import settings as cfg
from player import Player
from enemy import Enemy
from bullet import Bullet
from powerup import PowerUp
from consumable import Consumable
from menus import main_menu, pause
from menus.class_selection import class_selection_screen
from hud import HUD
from inventory import InventoryHUD
from tilemap import Map
from scenario import Room, Exit

# --- Constantes y Funciones de Ayuda ---
ENEMY_TYPES = ["basic", "fast", "tank"]

def game_over_screen(screen, clock, score, time_alive):
    big_font = pg.font.SysFont("consolas,roboto,arial", 48, bold=True)
    font = pg.font.SysFont("consolas,roboto,arial", 24)
    game_over_surface = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT))
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit(); raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_RETURN, pg.K_SPACE]: return
                if event.key == pg.K_ESCAPE: pg.quit(); raise SystemExit
        game_over_surface.fill(cfg.BG_COLOR)
        title = big_font.render("GAME OVER", True, cfg.RED)
        score_txt = font.render(f"Score: {score}", True, cfg.WHITE)
        time_txt = font.render(f"Tiempo: {int(time_alive)}s", True, cfg.WHITE)
        hint = font.render("Presiona ENTER para volver al menu", True, cfg.GRAY)
        game_over_surface.blit(title, title.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2 - 60)))
        game_over_surface.blit(score_txt, score_txt.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2)))
        game_over_surface.blit(time_txt, time_txt.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2 + 40)))
        game_over_surface.blit(hint, hint.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2 + 100)))
        scaled_surface = pg.transform.smoothscale(game_over_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pg.display.flip()
        clock.tick(cfg.FPS)

# --- Bucle Principal del Juego ---
def loop_juego(screen, clock):
    
    levels = [
        Room("map_A1_forest.txt", enemies_to_spawn=[("basic", 3), ("fast", 2)]),
        Room("map_A2_ruins.txt",  enemies_to_spawn=[("tank", 2), ("fast", 3)]),
        Room("map_B1_cave.txt",   enemies_to_spawn=[("fast", 5)]),
        Room("map_B2_lab.txt",    enemies_to_spawn=[("basic", 2), ("tank", 3)]),
    ]
    current_level_index = 0

    game_surface = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT))

    class_name = class_selection_screen(screen, clock)
    player = Player((0,0), class_name=class_name) 
    hud = HUD(player)
    inventory_hud = InventoryHUD(player)

    all_sprites = pg.sprite.Group(player)
    walls = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()
    consumables = pg.sprite.Group()
    exit_group = pg.sprite.Group()
    
    exit_pos = None
    game_map = None
    
    # --- ¡NUEVO! Variables para el Cooldown de enemigos ---
    enemy_spawn_timer = -1.0 # -1 significa inactivo
    pending_enemies_to_spawn = []

    def load_level(level_index):
        nonlocal walls, enemies, all_sprites, exit_pos, game_map, exit_group, consumables
        nonlocal pending_enemies_to_spawn, enemy_spawn_timer

        walls.empty(); enemies.empty(); exit_group.empty(); consumables.empty()
        all_sprites.empty(); all_sprites.add(player)

        level_data = levels[level_index]
        game_map = Map(level_data.map_file)
        new_walls, new_exit_pos = game_map.make_map()
        
        walls.add(new_walls)
        all_sprites.add(walls)
        exit_pos = new_exit_pos
        
        # --- CORRECCIÓN #1: Reaparición en el centro en un lugar seguro ---
        center_tile_x = cfg.LOGICAL_WIDTH // (cfg.TILESIZE * 2)
        center_tile_y = cfg.LOGICAL_HEIGHT // (cfg.TILESIZE * 2)
        
        found_safe_spot = False
        for r in range(game_map.tileheight):
            for c in range(game_map.tilewidth):
                # Busca en espiral hacia afuera desde el centro
                check_x = center_tile_x + (c if c % 2 == 0 else -c)
                check_y = center_tile_y + (r if r % 2 == 0 else -r)
                if 0 <= check_y < game_map.tileheight and 0 <= check_x < game_map.tilewidth:
                    if game_map.data[check_y][check_x] != '1':
                        # Se encontró un lugar seguro
                        player.pos.x = (check_x * cfg.TILESIZE) + cfg.TILESIZE / 2
                        player.pos.y = (check_y * cfg.TILESIZE) + cfg.TILESIZE / 2
                        player.rect.center = player.pos
                        found_safe_spot = True
                        break
            if found_safe_spot:
                break
        
        # --- CORRECCIÓN #2: Preparar enemigos para aparecer tras el cooldown ---
        pending_enemies_to_spawn = level_data.enemies_to_spawn
        enemy_spawn_timer = 5.0 # Inicia el temporizador de 5 segundos

    load_level(current_level_index)
    
    time_to_fire = 0.0

    while True:
        dt = clock.tick(cfg.FPS) / 1000.0
        keys = pg.key.get_pressed()
        time_to_fire = max(0.0, time_to_fire - dt)
        
        mouse_pos = pg.mouse.get_pos()
        screen_w, screen_h = screen.get_size()
        scale_x = cfg.LOGICAL_WIDTH / screen_w
        scale_y = cfg.LOGICAL_HEIGHT / screen_h
        logical_mouse_pos = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit(); raise SystemExit
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if pause.loop_pausa(clock) == "menu": return
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and time_to_fire <= 0.0:
                b = Bullet(player.rect.center, logical_mouse_pos, damage=player.damage)
                bullets.add(b); all_sprites.add(b)
                time_to_fire = player.fire_cooldown

        # --- ¡NUEVO! Lógica para el Cooldown de enemigos ---
        if enemy_spawn_timer > 0:
            enemy_spawn_timer -= dt
            if enemy_spawn_timer <= 0:
                # El temporizador terminó, ¡aparecen los enemigos!
                safe_zone = player.rect.inflate(cfg.TILESIZE * 5, cfg.TILESIZE * 5)
                for enemy_type, count in pending_enemies_to_spawn:
                    for _ in range(count):
                        while True:
                            x = random.randint(cfg.TILESIZE, cfg.LOGICAL_WIDTH - cfg.TILESIZE)
                            y = random.randint(cfg.TILESIZE, cfg.LOGICAL_HEIGHT - cfg.TILESIZE)
                            enemy_rect = pg.Rect(x, y, 32, 32)
                            if not safe_zone.colliderect(enemy_rect): break
                        
                        new_enemy = Enemy((x, y), enemy_type=enemy_type)
                        enemies.add(new_enemy)
                        all_sprites.add(new_enemy)
                pending_enemies_to_spawn = [] # Limpiar la lista

        if not enemies and not exit_group and not pending_enemies_to_spawn:
            if exit_pos:
                exit_sprite = Exit(exit_pos[0], exit_pos[1])
                exit_group.add(exit_sprite)
                all_sprites.add(exit_sprite)

        if pg.sprite.spritecollide(player, exit_group, False):
            current_level_index += 1
            if current_level_index < len(levels):
                load_level(current_level_index)
            else:
                main_menu.loop_menu(clock, loop_juego); return

        player.update(dt, keys)
        enemies.update(dt, player.rect.center)
        bullets.update(dt)
        hud.update(dt)
        player.tick_hit_cooldown(dt, 0.5)

        player.pos.x += player.vel.x * dt; player.rect.centerx = round(player.pos.x)
        for wall in pg.sprite.spritecollide(player, walls, False):
            if player.vel.x > 0: player.rect.right = wall.rect.left
            if player.vel.x < 0: player.rect.left = wall.rect.right
            player.pos.x = player.rect.centerx
        
        player.pos.y += player.vel.y * dt; player.rect.centery = round(player.pos.y)
        for wall in pg.sprite.spritecollide(player, walls, False):
            if player.vel.y > 0: player.rect.bottom = wall.rect.top
            if player.vel.y < 0: player.rect.top = wall.rect.bottom
            player.pos.y = player.rect.centery

        if pg.sprite.spritecollide(player, enemies, False) and player.can_take_hit():
            for enemy in pg.sprite.spritecollide(player, enemies, False):
                player.apply_damage(enemy.damage)
                hud.add_floating_text(f"-{enemy.damage}", player.rect.center, (255, 100, 100))
            player.trigger_hit_cooldown(0.5)

        for bullet in bullets:
            hit_enemy = pg.sprite.spritecollideany(bullet, enemies)
            if hit_enemy:
                hit_enemy.take_damage(bullet.damage)
                bullet.kill()
                if hit_enemy.is_dead():
                    hud.add_score(100)
                    if random.random() < cfg.CONSUMABLE_DROP_RATE:
                        c = Consumable(hit_enemy.rect.center)
                        consumables.add(c); all_sprites.add(c)
                    hit_enemy.kill()

        for item in pg.sprite.spritecollide(player, consumables, True):
            item.apply(hud)
            inventory_hud.add(getattr(item, 'item_type', 'coin'))

        if player.hp <= 0:
            game_over_screen(screen, clock, hud.score, hud.time_alive)
            main_menu.loop_menu(clock, loop_juego); return

        game_surface.fill(cfg.BG_COLOR)
        if game_map: game_map.render(game_surface)
        
        all_sprites.draw(game_surface)

        for s in all_sprites:
            if hasattr(s, "draw_hp"): s.draw_hp(game_surface)
            if hasattr(s, "draw_health_bar"): s.draw_health_bar(game_surface)

        hud.draw(game_surface)
        inventory_hud.draw(game_surface)

        scaled_surface = pg.transform.smoothscale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))

        pg.display.flip()