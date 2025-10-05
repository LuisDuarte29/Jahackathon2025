# game.py
import pygame as pg
import random
import settings as cfg

# --- Clases de Entidades y Módulos ---
from player import Player
from enemy import Enemy, Boss
from bullet import Bullet, EnemyBullet  # <--- IMPORTADO
from powerup import PowerUp             # <--- IMPORTADO
from consumable import Consumable
from hud import HUD
from inventory import InventoryHUD
from tilemap import Map
from scenario import Room, Exit

# --- Módulos de Menús ---
from menus import main_menu, pause
from menus.class_selection import class_selection_screen
from menus.game_over import game_over_screen # <--- IMPORTADO (en vez de la función local)

# --- Constantes del Juego ---
ENEMY_TYPES = ["basic", "fast", "tank"]
# La probabilidad de drop se lee directamente de cfg, como en el original
cfg.CONSUMABLE_DROP_RATE = getattr(cfg, "CONSUMABLE_DROP_RATE", 0.2)

def victory_screen(screen, clock):
    """Muestra la pantalla de Victoria."""
    big_font = pg.font.SysFont("consolas,roboto,arial", 60, bold=True)
    font = pg.font.SysFont("consolas,roboto,arial", 24)
    victory_surface = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT))
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT: pg.quit(); raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_RETURN, pg.K_SPACE]: return
        victory_surface.fill(cfg.BG_COLOR)
        title = big_font.render("¡HAS GANADO!", True, cfg.GREEN)
        hint = font.render("Presiona ENTER para volver al menu", True, cfg.WHITE)
        victory_surface.blit(title, title.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2)))
        victory_surface.blit(hint, hint.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2 + 100)))
        scaled_surface = pg.transform.smoothscale(victory_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pg.display.flip()
        clock.tick(cfg.FPS)


# --- Bucle Principal del Juego ---
def loop_juego(screen, clock):
    # --- Configuración Inicial del Nivel ---
    levels = [
        Room("map_A1_forest.txt", enemies_to_spawn=[("basic", 3), ("fast", 2)]),
        Room("map_A2_ruins.txt",  enemies_to_spawn=[("tank", 2), ("fast", 3)]),
        Room("map_B1_cave.txt",   enemies_to_spawn=[("fast", 5)]),
        Room("map_B2_lab.txt",    enemies_to_spawn=[("basic", 2), ("tank", 3)]),
        Room("map_C1_boss.txt",   enemies_to_spawn=[("boss", 1)]) # <-- NIVEL DEL JEFE
    ]
    current_level_index = 0

    # Superficie lógica para escalado de resolución
    game_surface = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT))

    # --- Inicialización del Jugador y HUD ---
    class_name = class_selection_screen(screen, clock)
    player = Player((0,0), class_name=class_name) 
    hud = HUD(player)
    inventory_hud = InventoryHUD(player)

    # --- Grupos de Sprites ---
    all_sprites = pg.sprite.Group(player)
    walls = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()          # Balas del jugador
    enemy_bullets = pg.sprite.Group()    # Balas de los enemigos
    powerups = pg.sprite.Group()         # Power-ups
    consumables = pg.sprite.Group()
    exit_group = pg.sprite.Group()
    
    # --- Variables de Estado del Juego ---
    exit_pos = None
    game_map = None
    enemy_spawn_timer = -1.0 # -1 significa inactivo
    pending_enemies_to_spawn = []
    time_to_fire = 0.0

    # --- Función para Cargar Nivel ---
    def load_level(level_index):
        nonlocal walls, enemies, all_sprites, exit_pos, game_map, exit_group, consumables, powerups
        nonlocal pending_enemies_to_spawn, enemy_spawn_timer

        # Limpiar todos los grupos para el nuevo nivel
        for group in [walls, enemies, exit_group, consumables, powerups, bullets, enemy_bullets]:
            group.empty()
        all_sprites.empty()
        all_sprites.add(player)

        # Cargar datos del nivel y crear mapa
        level_data = levels[level_index]
        game_map = Map(level_data.map_file)
        new_walls, new_exit_pos = game_map.make_map()
        
        walls.add(new_walls)
        all_sprites.add(walls)
        exit_pos = new_exit_pos
        
        # Reposicionar al jugador en un lugar seguro del nuevo mapa
        center_tile_x = cfg.LOGICAL_WIDTH // (cfg.TILESIZE * 2)
        center_tile_y = cfg.LOGICAL_HEIGHT // (cfg.TILESIZE * 2)
        
        pending_enemies_to_spawn = level_data.enemies_to_spawn
        enemy_spawn_timer = 5.0

        found_safe_spot = False
        for r in range(max(game_map.tileheight, game_map.tilewidth)):
            for i in range(-r, r + 1):
                # Busca en un cuadrado creciente alrededor del centro
                test_points = [
                    (center_tile_x + i, center_tile_y - r), (center_tile_x + i, center_tile_y + r),
                    (center_tile_x - r, center_tile_y + i), (center_tile_x + r, center_tile_y + i)
                ]
                for tx, ty in test_points:
                    if 0 <= ty < game_map.tileheight and 0 <= tx < game_map.tilewidth:
                        if game_map.data[ty][tx] != '1':
                            player.pos.x = (tx * cfg.TILESIZE) + cfg.TILESIZE / 2
                            player.pos.y = (ty * cfg.TILESIZE) + cfg.TILESIZE / 2
                            player.rect.center = player.pos
                            found_safe_spot = True
                            break
                if found_safe_spot: break
            if found_safe_spot: break
        
        # Preparar enemigos para aparecer tras un cooldown
        pending_enemies_to_spawn = level_data.enemies_to_spawn
        enemy_spawn_timer = 3.0 # Inicia el temporizador de 3 segundos

        # ⭐ MERGE: Spawnea 3 power-ups en posiciones aleatorias seguras
        for _ in range(3):
            while True:
                px = random.randint(cfg.TILESIZE, cfg.LOGICAL_WIDTH - cfg.TILESIZE * 2)
                py = random.randint(cfg.TILESIZE, cfg.LOGICAL_HEIGHT - cfg.TILESIZE * 2)
                temp_rect = pg.Rect(px, py, 24, 24)
                if not any(wall.rect.colliderect(temp_rect) for wall in walls):
                    p = PowerUp((px, py))
                    powerups.add(p)
                    all_sprites.add(p)
                    break

    # Carga inicial
    load_level(current_level_index)

    # =============== BUCLE PRINCIPAL ===============
    while True:
        dt = clock.tick(cfg.FPS) / 1000.0
        keys = pg.key.get_pressed()
        time_to_fire = max(0.0, time_to_fire - dt)
        
        # Obtener posición del mouse escalada a la resolución lógica
        mouse_pos = pg.mouse.get_pos()
        screen_w, screen_h = screen.get_size()
        scale_x = cfg.LOGICAL_WIDTH / screen_w
        scale_y = cfg.LOGICAL_HEIGHT / screen_h
        logical_mouse_pos = (mouse_pos[0] * scale_x, mouse_pos[1] * scale_y)

        # --- Manejo de Eventos ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if pause.loop_pausa(clock) == "menu":
                    return
            if (event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and time_to_fire <= 0.0):
                b = Bullet(player.rect.center, logical_mouse_pos, damage=player.damage)
                bullets.add(b)
                all_sprites.add(b)
                time_to_fire = player.fire_cooldown

        # --- Lógica de Spawn ---
        if enemy_spawn_timer > 0:
            enemy_spawn_timer -= dt
            if enemy_spawn_timer <= 0:
                safe_zone = player.rect.inflate(cfg.TILESIZE * 6, cfg.TILESIZE * 6)
                for enemy_type, count in pending_enemies_to_spawn:
                    for _ in range(count):
                        while True:
                            x = random.randint(cfg.TILESIZE, cfg.LOGICAL_WIDTH - cfg.TILESIZE)
                            y = random.randint(cfg.TILESIZE, cfg.LOGICAL_HEIGHT - cfg.TILESIZE)
                            enemy_rect = pg.Rect(x, y, 32, 32)
                            # Asegurarse de no spawnear sobre el jugador o en una pared
                            if not safe_zone.colliderect(enemy_rect) and not any(wall.rect.colliderect(enemy_rect) for wall in walls):
                                break
                                 # --- CORRECCIÓN: Usar la clase Boss si el tipo es "boss" ---
                        if enemy_type == "boss":
                            new_enemy = Boss((x, y))
                        else:
                            new_enemy = Enemy((x, y), enemy_type=enemy_type)
                        
                        enemies.add(new_enemy)
                        all_sprites.add(new_enemy)
                pending_enemies_to_spawn = []

        # Si todos los enemigos están muertos y no hay una salida, crearla
        if not enemies and not exit_group and not pending_enemies_to_spawn and enemy_spawn_timer <= 0:
            if exit_pos:
                exit_sprite = Exit(exit_pos[0], exit_pos[1])
                exit_group.add(exit_sprite)
                all_sprites.add(exit_sprite)

        # --- Actualizaciones ---
        player.tick_hit_cooldown(dt, 0.5)
        player.update(dt, keys)
        enemies.update(dt, player.rect.center, enemy_bullets) # ⭐ MERGE: Pasa el grupo de balas enemigas
        bullets.update(dt)
        enemy_bullets.update(dt) # ⭐ MERGE: Actualiza las balas enemigas
        powerups.update(dt)
        consumables.update(dt)
        hud.update(dt)

        # Colisión con paredes (movimiento)
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

        # --- Colisiones y Lógica de Combate ---
        # Jugador choca con la salida
        if pg.sprite.spritecollide(player, exit_group, False):
            current_level_index += 1
            if current_level_index < len(levels):
                load_level(current_level_index)
            else:
                # --- ¡VICTORIA! ---
                victory_screen(screen, clock)
                main_menu.loop_menu(clock, loop_juego); return

        # Jugador contra enemigos (contacto)
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
                # ⭐ MERGE: Añadido texto flotante de daño
                hud.add_floating_text(f"-{bullet.damage}", hit_enemy.rect.center, (255, 180, 50))
                bullet.kill()
                if hit_enemy.is_dead():
                    hud.add_score(100)
                    # ⭐ MERGE: Añadido texto flotante de puntuación
                    hud.add_floating_text("+100", hit_enemy.rect.center, (200, 255, 130))
                    if random.random() < cfg.CONSUMABLE_DROP_RATE:
                        c = Consumable(hit_enemy.rect.center)
                        consumables.add(c)
                        all_sprites.add(c)
                    hit_enemy.kill()

        # ⭐ MERGE: Balas enemigas contra jugador
        enemy_hits = pg.sprite.spritecollide(player, enemy_bullets, True)
        for eb in enemy_hits:
            if player.can_take_hit():
                player.apply_damage(eb.damage)
                hud.add_floating_text(f"-{eb.damage}", player.rect.center, (255, 120, 120))
                player.trigger_hit_cooldown(0.5)

        # Jugador contra consumibles
        picked_consumables = pg.sprite.spritecollide(player, consumables, True)
        for item in picked_consumables:
            # ⭐ MERGE: Lógica try-except robusta del primer archivo
            try: item.apply(hud)
            except TypeError: item.apply(player) # Fallback
            inventory_hud.add(getattr(item, 'item_type', 'coin'))

        # ⭐ MERGE: Jugador contra power-ups
        picked_powerups = pg.sprite.spritecollide(player, powerups, True)
        for p_up in picked_powerups:
            p_up.apply(player)
            hud.add_floating_text(p_up.effect.replace("_", " ").title(), p_up.rect.center, (255, 215, 0))

        # --- Game Over ---
        if player.hp <= 0:
            # ⭐ MERGE: Llamada a la pantalla de game over importada
            game_over_screen(screen, clock, hud.score, hud.time_alive, loop_juego)
            return

        # --- Dibujado ---
        game_surface.fill(cfg.BG_COLOR)
        if game_map: game_map.render(game_surface)
        
        # Dibujar todos los sprites
        all_sprites.draw(game_surface)
        bullets.draw(game_surface)
        enemy_bullets.draw(game_surface) # Dibujar balas enemigas

        # Dibujar elementos extra como barras de vida
        for s in all_sprites:
            if hasattr(s, "draw_health_bar"): s.draw_health_bar(game_surface)
            if hasattr(s, "draw_hp"): s.draw_hp(game_surface)

        # Dibujar HUDs encima de todo
        hud.draw(game_surface)
        inventory_hud.draw(game_surface)

        # Escalar la superficie lógica a la pantalla real y mostrar
        scaled_surface = pg.transform.smoothscale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pg.display.flip()