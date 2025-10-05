# menus/victory.py
import pygame as pg
import settings as cfg

def victory_screen(screen, clock):
    """Muestra la pantalla de Victoria."""
    big_font = pg.font.SysFont("consolas,roboto,arial", 60, bold=True)
    font = pg.font.SysFont("consolas,roboto,arial", 24)
    victory_surface = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT))
    waiting = True
    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_RETURN, pg.K_SPACE]:
                    return

        victory_surface.fill(cfg.BG_COLOR)
        title = big_font.render("¡HAS GANADO!", True, cfg.GREEN)
        hint = font.render("Presiona ENTER para volver al menu", True, cfg.WHITE)
        victory_surface.blit(
            title,
            title.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2)),
        )
        victory_surface.blit(
            hint,
            hint.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2 + 100)),
        )

        scaled_surface = pg.transform.smoothscale(victory_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pg.display.flip()
        clock.tick(cfg.FPS)
