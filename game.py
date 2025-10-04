# game.py
import pygame as pg
import settings as cfg
from player import Player
from enemy import Enemy
from bullet import Bullet
from menus import main_menu, pause


CLASS_KEYS = {pg.K_1: "Warrior", pg.K_2: "Rogue", pg.K_3: "Mage"}


def class_selection_screen(screen, clock):
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
    class_name = class_selection_screen(screen, clock)
    player = Player((cfg.WIDTH // 2, cfg.HEIGHT // 2), class_name=class_name)
    all_sprites = pg.sprite.Group()
    enemies = pg.sprite.Group()
    bullets = pg.sprite.Group()
    all_sprites.add(player)

    # simple starter enemy
    enemy = Enemy((100, 100))
    enemies.add(enemy); all_sprites.add(enemy)

    time_to_fire = 0.0
    jugando = True

    while jugando:
        dt = clock.tick(cfg.FPS) / 1000.0
        keys = pg.key.get_pressed()
        time_to_fire = max(0.0, time_to_fire - dt)

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
                    bullets.add(b); all_sprites.add(b)
                    time_to_fire = player.fire_cooldown

        # Updates
        player.update(dt, keys)
        for e in enemies:
            e.update(dt, player.rect.center)
        bullets.update(dt)

        # Collisions: bullets -> enemies
        for b in bullets.sprites():
            hit = pg.sprite.spritecollideany(b, enemies)
            if hit:
                hit.take_damage(b.damage)
                b.kill()
                if hit.is_dead():
                    hit.kill()

        # Draw
        screen.fill(cfg.BG_COLOR)
        for s in all_sprites:
            screen.blit(s.image, s.rect)
            if hasattr(s, 'draw_health_bar'):
                s.draw_health_bar(screen)
            if hasattr(s, 'draw_hp'):
                s.draw_hp(screen)

        pg.display.flip()

