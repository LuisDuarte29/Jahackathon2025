# game.py
import pygame as pg
import random
import settings as cfg
from player import Player
from enemy import Enemy
from bullet import Bullet, EnemyBullet
from powerup import PowerUp
from consumable import Consumable
from menus import main_menu, pause
from menus.class_selection import class_selection_screen
from menus.game_over import game_over_screen
from hud import HUD
from inventory import InventoryHUD

# --- Constantes del juego ---
CLASS_KEYS = {pg.K_1: "Warrior", pg.K_2: "Rogue", pg.K_3: "Mage"}
ENEMY_TYPES = ["basic", "fast", "tank"]
POWERUP_LOCATIONS = [
    (200, 200),
    (cfg.WIDTH - 200, 200),
    (cfg.WIDTH / 2, cfg.HEIGHT - 150),
]

# Probabilidad de que un enemigo dropee consumible (configurable en settings)
cfg.CONSUMABLE_DROP_RATE = getattr(cfg, "CONSUMABLE_DROP_RATE", 0.2)


def spawn_enemy(offscreen=True):
    """Genera un enemigo de un tipo aleatorio fuera de la pantalla."""
    enemy_type = random.choice(ENEMY_TYPES)
    if offscreen:
        side = random.choice(["l", "r", "t", "b"])
        if side == "l":
            pos = (-30, random.randint(0, cfg.HEIGHT))
        elif side == "r":
            pos = (cfg.WIDTH + 30, random.randint(0, cfg.HEIGHT))
        elif side == "t":
            pos = (random.randint(0, cfg.WIDTH), -30)
        else:
            pos = (random.randint(0, cfg.WIDTH), cfg.HEIGHT + 30)
    else:
        pos = (random.randint(50, cfg.WIDTH - 50), random.randint(50, cfg.HEIGHT - 50))
    return Enemy(pos, enemy_type=enemy_type)


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
    bullets = pg.sprite.Group()  # balas del jugador
    enemy_bullets = pg.sprite.Group()  # balas de los enemigos
    powerups = pg.sprite.Group()
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
        player.update(dt, keys)

        # Pasamos enemy_bullets para que los enemigos puedan spawnear balas ahí
        enemies.update(dt, player.rect.center, enemy_bullets)
        bullets.update(dt)
        enemy_bullets.update(dt)  # actualizar balas enemigas
        powerups.update(dt)
        consumables.update(dt)

        # --- Lógica de Spawn ---
        enemy_spawn_timer += dt
        enemy_spawn_interval = max(0.5, 3.0 - hud.time_alive * 0.04)
        if enemy_spawn_timer >= enemy_spawn_interval:
            enemy_spawn_timer = 0.0
            new_enemy = spawn_enemy()
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        if not powerups_spawned and hud.time_alive > 1.0:
            for pos in POWERUP_LOCATIONS:
                p = PowerUp(pos)
                powerups.add(p)
                all_sprites.add(p)
            powerups_spawned = True

        # --- Colisiones ---
        # Jugador contra enemigos (contacto cuerpo a cuerpo)
        collided_enemies = pg.sprite.spritecollide(player, enemies, False)
        if collided_enemies and player.can_take_hit():
            for enemy in collided_enemies:
                player.apply_damage(enemy.damage)
                hud.add_floating_text(f"-{enemy.damage}", player.rect.center, (255, 100, 100))
            player.trigger_hit_cooldown(0.5)

        # Balas del jugador contra enemigos
        for bullet in bullets:
            hit_enemy = pg.sprite.spritecollideany(bullet, enemies)
            if hit_enemy:
                hit_enemy.take_damage(bullet.damage)
                bullet.kill()
                if hit_enemy.is_dead():
                    hud.add_score(100)
                    hud.add_floating_text(
                        "+100", hit_enemy.rect.center, (200, 255, 130)
                    )
                    # 20% probabilidad de dropear consumible (configurable en settings)
                    if random.random() < cfg.CONSUMABLE_DROP_RATE:
                        c = Consumable(hit_enemy.rect.center)
                        consumables.add(c); all_sprites.add(c)
                    hit_enemy.kill()

        # Balas enemigas contra jugador
        enemy_hits = pg.sprite.spritecollide(player, enemy_bullets, True)
        for eb in enemy_hits:
            if player.can_take_hit():
                player.apply_damage(eb.damage)
                hud.add_floating_text(
                    f"-{eb.damage}", player.rect.center, (255, 120, 120)
                )
                player.trigger_hit_cooldown(0.5)

        # Jugador contra consumibles
        picked_consumables = pg.sprite.spritecollide(player, consumables, True)
        for item in picked_consumables:
            # Consumable.apply expects the HUD so puede añadir monedas/texto
            try:
                item.apply(hud)
            except TypeError:
                # fallback: si apply espera player
                item.apply(player)
            # actualizar HUD de inventario visual
            try:
                inventory_hud.add(item.item_type)
            except Exception:
                inventory_hud.add("coin")

        # Jugador contra power-ups
        picked_powerups = pg.sprite.spritecollide(player, powerups, True)
        for p_up in picked_powerups:
            p_up.apply(player)
            hud.add_floating_text(
                p_up.effect.replace("_", " ").title(), p_up.rect.center, (255, 215, 0)
            )

        # --- Game Over ---
        if player.hp <= 0:
            game_over_screen(screen, clock, hud.score, hud.time_alive, loop_juego)
            return

        # --- Dibujado ---
        screen.fill(cfg.BG_COLOR)

        # Dibujar sprites principales
        for s in all_sprites:
            if hasattr(s, "draw_hp"): s.draw_hp(game_surface)
            if hasattr(s, "draw_health_bar"): s.draw_health_bar(game_surface)

        hud.draw(game_surface)
        inventory_hud.draw(game_surface)

        # Dibujar balas enemigas (están en grupo separado)
        for eb in enemy_bullets:
            screen.blit(eb.image, eb.rect)

        hud.draw(screen)
        inventory_hud.draw(screen)

        pg.display.flip()