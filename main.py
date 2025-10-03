# main.py
import sys, random
import pygame as pg

from settings import *
from player import Player
from enemy import Enemy
from bullet import Bullet

def spawn_enemy(offscreen=True):
    if offscreen:
        side = random.choice(["l", "r", "t", "b"])
        if side == "l":
            x, y = -20, random.randint(0, HEIGHT)
        elif side == "r":
            x, y = WIDTH + 20, random.randint(0, HEIGHT)
        elif side == "t":
            x, y = random.randint(0, WIDTH), -20
        else:
            x, y = random.randint(0, WIDTH), HEIGHT + 20
    else:
        x, y = random.randint(50, WIDTH - 50), random.randint(50, HEIGHT - 50)
    return Enemy((x, y))

def draw_ui(screen, player, font, time_alive, score):
    txt = font.render(f"Tiempo: {int(time_alive)}s   Score: {score}", True, WHITE)
    screen.blit(txt, (12, 10))
    bar_w, bar_h = 240, 12
    x = WIDTH // 2 - bar_w // 2
    y = 14
    ratio = player.hp / player.max_hp if player.max_hp else 0
    pg.draw.rect(screen, GRAY, (x, y, bar_w, bar_h), border_radius=4)
    pg.draw.rect(screen, (40, 200, 60) if ratio > 0.35 else (220, 80, 60),
                 (x, y, int(bar_w * ratio), bar_h), border_radius=4)

def game_over_screen(screen, big_font, font, score):
    screen.fill(BG)
    title = big_font.render("GAME OVER", True, WHITE)
    msg = font.render(f"Puntaje: {score}", True, WHITE)
    hint = font.render("Presioná R para reiniciar o ESC para salir", True, GRAY)
    screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
    screen.blit(msg,    msg.get_rect(center=(WIDTH//2, HEIGHT//2 + 8)))
    screen.blit(hint,   hint.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))
    pg.display.flip()

def main():
    pg.init()
    pg.display.set_caption("Hackatón MVP — Pygame (auto-fire con click)")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    clock = pg.time.Clock()
    font = pg.font.SysFont("consolas,roboto,arial", 18)
    big_font = pg.font.SysFont("consolas,roboto,arial", 48, bold=True)

    running = True
    game_over = False
    time_alive = 0.0
    score = 0

    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()

    player = Player((WIDTH//2, HEIGHT//2))
    all_sprites.add(player)

    enemies.add(spawn_enemy())
    all_sprites.add(enemies)

    enemy_spawn_timer = 0.0
    enemy_spawn_interval = 2.0
    damage_tick = 12

    # --- Nuevo: estado de disparo continuo ---
    mouse_held = False
    fire_timer = 0.0
    # -----------------------------------------

    while running:
        dt = clock.tick(FPS) / 1000.0

        for e in pg.event.get():
            if e.type == pg.QUIT:
                running = False

            if e.type == pg.KEYDOWN:
                if game_over:
                    if e.key == pg.K_r:
                        return main()
                    if e.key == pg.K_ESCAPE:
                        running = False

            # Mouse: presionar/soltar para auto-fire
            if e.type == pg.MOUSEBUTTONDOWN and not game_over:
                if e.button == 1:  # izquierdo
                    mouse_held = True
                    # Disparo inmediato al presionar
                    mouse_pos = pg.mouse.get_pos()
                    b = Bullet(player.rect.center, mouse_pos)
                    bullets.add(b)
                    all_sprites.add(b)
                    fire_timer = 0.0  # reinicia temporizador

            if e.type == pg.MOUSEBUTTONUP and not game_over:
                if e.button == 1:
                    mouse_held = False

        if not running:
            break

        keys = pg.key.get_pressed()

        if not game_over:
            time_alive += dt

            # Dificultad incremental
            enemy_spawn_timer += dt
            enemy_spawn_interval = max(0.7, 2.0 - time_alive * 0.05)
            if enemy_spawn_timer >= enemy_spawn_interval:
                enemy_spawn_timer = 0
                en = spawn_enemy()
                enemies.add(en)
                all_sprites.add(en)

            # Player
            player.update(dt, keys)
            player.tick_hit_cooldown(dt, PLAYER_HIT_COOLDOWN)

            # --- Auto-fire mientras se mantiene el click ---
            if mouse_held:
                fire_timer += dt
                if fire_timer >= FIRE_COOLDOWN:
                    fire_timer = 0.0
                    mouse_pos = pg.mouse.get_pos()
                    b = Bullet(player.rect.center, mouse_pos)
                    bullets.add(b)
                    all_sprites.add(b)
            # -----------------------------------------------

            # Bullets
            bullets.update(dt)

            # Enemigos persiguen
            for en in enemies:
                en.update(dt, player.rect.center)

            # Colisiones: balas vs enemigos
            for b in bullets:
                hit_list = pg.sprite.spritecollide(b, enemies, False)
                if hit_list:
                    b.kill()
                    for en in hit_list:
                        en.take_damage(b.damage)
                        if en.is_dead():
                            en.kill()
                            score += 100

            # Colisiones: enemigos vs jugador
            hits = pg.sprite.spritecollide(player, enemies, False)
            if hits and player.can_take_hit():
                player.apply_damage(damage_tick)
                player.trigger_hit_cooldown(PLAYER_HIT_COOLDOWN)
                # pequeño empujón
                push = pg.math.Vector2(0, 0)
                for en in hits:
                    push += (player.pos - pg.math.Vector2(en.rect.center))
                if push.length_squared() > 0:
                    push = push.normalize() * 8
                    player.pos += push
                    # clamp inmediato tras empujón
                    half_w, half_h = player.rect.width//2, player.rect.height//2
                    player.pos.x = max(half_w, min(WIDTH - half_w, player.pos.x))
                    player.pos.y = max(half_h, min(HEIGHT - half_h, player.pos.y))
                    player.rect.center = (int(player.pos.x), int(player.pos.y))

            if player.hp <= 0:
                game_over = True

            # Render
            screen.fill(BG)
            all_sprites.draw(screen)
            player.draw_health_bar(screen)
            for en in enemies:
                en.draw_hp(screen)
                en.draw(screen)
            draw_ui(screen, player, font, time_alive, score)
            pg.display.flip()
        else:
            game_over_screen(screen, big_font, font, score)

    pg.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()