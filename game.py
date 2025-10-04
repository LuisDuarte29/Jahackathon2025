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
from inventory import InventoryHUD  # <-- HUD de consumibles

# --- Teclas mapeadas a clases ---
CLASS_KEYS = {pg.K_1: "Warrior", pg.K_2: "Rogue", pg.K_3: "Mage"}

# --- Tipos de enemigos y spawn ---
ENEMY_TYPES = ["basic", "fast", "tank"]
SPAWN_INTERVAL = 3.0  # segundos entre spawn de enemigos

# --- Variables de power-ups ---
POWERUP_ROOMS = [(200, 200), (400, 300), (600, 150)]  # ejemplo posiciones de habitaciones especiales
powerups_spawned = False

def class_selection_screen(screen, clock):
    """Pantalla para seleccionar la clase del jugador"""
    font = pg.font.Font(None, 48)
    small_font = pg.font.Font(None, 32)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); raise SystemExit
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
    """Bucle principal del juego"""
    global powerups_spawned
    # --- Selección de clase ---
    class_name = class_selection_screen(screen, clock)
    player = Player((cfg.WIDTH // 2, cfg.HEIGHT // 2), class_name=class_name)

    # --- HUD de inventario ---
    inventory = InventoryHUD(player)

    # --- Grupos de sprites ---
    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()
    powerups = pg.sprite.Group()
    consumables = pg.sprite.Group()
    all_sprites.add(player)

    # --- Variables de tiempo ---
    spawn_timer = 0.0
    time_to_fire = 0.0

    jugando = True
    while jugando:
        dt = clock.tick(cfg.FPS) / 1000.0
        keys = pg.key.get_pressed()
        spawn_timer += dt
        time_to_fire = max(0.0, time_to_fire - dt)

        # --- Manejo de eventos ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit(); raise SystemExit
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

        # --- Spawn dinámico de enemigos ---
        if spawn_timer >= SPAWN_INTERVAL:
            spawn_timer = 0
            pos = (random.randint(50, cfg.WIDTH - 50), random.randint(50, cfg.HEIGHT - 50))
            e_type = random.choice(ENEMY_TYPES)
            new_enemy = Enemy(pos, enemy_type=e_type)
            enemies.add(new_enemy)
            all_sprites.add(new_enemy)

        # --- Spawn de power-ups en habitaciones especiales ---
        if not powerups_spawned:
            for room_pos in POWERUP_ROOMS:
                p = PowerUp(room_pos)
                powerups.add(p)
                all_sprites.add(p)
            powerups_spawned = True

        # --- Actualizaciones ---
        player.update(dt, keys)
        for e in enemies:
            e.update(dt, player)
        bullets.update(dt)
        powerups.update(dt)
        consumables.update(dt)

        # --- Colisiones jugador <-> enemigos ---
        for e in enemies:
            if player.rect.colliderect(e.rect) and player.can_take_hit():
                player.apply_damage(e.damage)
                player.trigger_hit_cooldown(0.5)

        # --- Colisiones balas -> enemigos ---
        for b in bullets.sprites():
            hit = pg.sprite.spritecollideany(b, enemies)
            if hit:
                hit.take_damage(b.damage)
                b.kill()
                if hit.is_dead():
                    hit.kill()
                    # Sueltan consumibles
                    c = Consumable(hit.rect.center)
                    consumables.add(c)
                    all_sprites.add(c)

        # --- Colisiones jugador <-> power-ups ---
        for p in powerups:
            if player.rect.colliderect(p.rect):
                p.apply(player)

        # --- Colisiones jugador <-> consumibles ---
        for c in consumables:
            if player.rect.colliderect(c.rect):
                c.apply(player)
                inventory.add(c.item_type)  # actualizar HUD
                c.kill()

        # --- Dibujado ---
        screen.fill(cfg.BG_COLOR)
        for s in all_sprites:
            screen.blit(s.image, s.rect)
            if hasattr(s, 'draw_health_bar'):
                s.draw_health_bar(screen)
            if hasattr(s, 'draw_hp'):
                s.draw_hp(screen)

        # --- Dibujar HUD de inventario ---
        inventory.draw(screen)

        pg.display.flip()
