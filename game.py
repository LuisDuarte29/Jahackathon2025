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
    """Bucle principal del juego."""
    class_name = class_selection_screen(screen, clock)
    player = Player((cfg.WIDTH // 2, cfg.HEIGHT // 2), class_name=class_name)

    hud = HUD(player)
    inventory_hud = InventoryHUD(player)

    all_sprites = pg.sprite.Group(player)
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()  # balas del jugador
    enemy_bullets = pg.sprite.Group()  # balas de los enemigos
    powerups = pg.sprite.Group()
    consumables = pg.sprite.Group()

    time_to_fire = 0.0
    enemy_spawn_timer = 2.0
    powerups_spawned = False

    while True:
        dt = clock.tick(cfg.FPS) / 1000.0
        keys = pg.key.get_pressed()
        time_to_fire = max(0.0, time_to_fire - dt)

        # --- Eventos ---
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                if pause.loop_pausa(clock) == "menu":
                    return
            if (
                event.type == pg.MOUSEBUTTONDOWN
                and event.button == 1
                and time_to_fire <= 0.0
            ):
                b = Bullet(player.rect.center, event.pos, damage=player.damage)
                bullets.add(b)
                all_sprites.add(b)
                time_to_fire = player.fire_cooldown

        # --- Actualizaciones ---
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
                hud.add_floating_text(
                    f"-{enemy.damage}", player.rect.center, (255, 100, 100)
                )
            player.trigger_hit_cooldown(0.5)

        # Balas del jugador contra enemigos
        for bullet in bullets:
            hit_enemy = pg.sprite.spritecollideany(bullet, enemies)
            if hit_enemy:
                hit_enemy.take_damage(bullet.damage)
                hud.add_floating_text(
                    f"-{bullet.damage}", hit_enemy.rect.center, (255, 180, 50)
                )
                bullet.kill()
                if hit_enemy.is_dead():
                    hud.add_score(100)
                    hud.add_floating_text(
                        "+100", hit_enemy.rect.center, (200, 255, 130)
                    )
                    # 20% probabilidad de dropear consumible (configurable en settings)
                    if random.random() < cfg.CONSUMABLE_DROP_RATE:
                        c = Consumable(hit_enemy.rect.center)
                        consumables.add(c)
                        all_sprites.add(c)
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
            screen.blit(s.image, s.rect)
            if hasattr(s, "draw_health_bar"):
                s.draw_health_bar(screen)
            if hasattr(s, "draw_hp"):
                s.draw_hp(screen)

        # Dibujar balas enemigas (están en grupo separado)
        for eb in enemy_bullets:
            screen.blit(eb.image, eb.rect)

        hud.draw(screen)
        inventory_hud.draw(screen)

        pg.display.flip()
