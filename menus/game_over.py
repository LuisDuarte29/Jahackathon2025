# menus/game_over.py
import pygame as pg
import settings as cfg
from menus import main_menu


def game_over_screen(screen, clock, score, time_alive, loop_juego):
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
                if event.key in [pg.K_RETURN, pg.K_SPACE]:
                    main_menu.loop_menu(clock, loop_juego)
                    return
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    raise SystemExit

        screen.fill(cfg.BG_COLOR)
        title = big_font.render("GAME OVER", True, cfg.RED)
        score_txt = font.render(f"Score: {score}", True, cfg.WHITE)
        time_txt = font.render(f"Tiempo: {int(time_alive)}s", True, cfg.WHITE)
        hint = font.render("Presiona ENTER para volver al menu", True, cfg.GRAY)

        screen.blit(
            title, title.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 - 60))
        )
        screen.blit(
            score_txt, score_txt.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2))
        )
        screen.blit(
            time_txt, time_txt.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 40))
        )
        screen.blit(hint, hint.get_rect(center=(cfg.WIDTH // 2, cfg.HEIGHT // 2 + 100)))

        pg.display.flip()
        clock.tick(cfg.FPS)
