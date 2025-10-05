# menus/class_selection.py
import pygame as pg
import settings as cfg

CLASS_KEYS = {pg.K_1: "Warrior", pg.K_2: "Rogue", pg.K_3: "Mage"}


def class_selection_screen(screen, clock):
    """Pantalla para seleccionar la clase del jugador."""
    font = pg.font.Font(None, 48)
    small_font = pg.font.Font(None, 32)

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN and event.key in CLASS_KEYS:
                return CLASS_KEYS[event.key]

        screen.fill(cfg.BG_COLOR)
        title = font.render("Selecciona tu clase:", True, cfg.WHITE)
        opts = [
            small_font.render(f"{i+1} - {cls}", True, cfg.GREEN)
            for i, cls in enumerate(CLASS_KEYS.values())
        ]
        screen.blit(
            title, (cfg.WIDTH // 2 - title.get_rect().width // 2, cfg.HEIGHT // 3)
        )
        for i, opt in enumerate(opts):
            screen.blit(
                opt,
                (cfg.WIDTH // 2 - opt.get_rect().width // 2, cfg.HEIGHT // 2 + i * 40),
            )
        pg.display.flip()
        clock.tick(cfg.FPS)
