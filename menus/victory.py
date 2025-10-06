# menus/victory.py
import pygame as pg
import random
import math
import settings as cfg


# Generar partículas de confeti
def generar_confeti(n=50):
    confeti = []
    for _ in range(n):
        x = random.randint(0, cfg.LOGICAL_WIDTH)
        y = random.randint(-cfg.LOGICAL_HEIGHT, 0)
        color = random.choice(
            [(255, 0, 0), (0, 255, 0), (0, 180, 255), (255, 255, 0), (255, 0, 200)]
        )
        vel = random.uniform(1, 3)
        size = random.randint(4, 8)
        confeti.append([x, y, color, vel, size])
    return confeti


def victory_screen(screen, clock):
    """Muestra la pantalla de Victoria con efectos visuales."""
    big_font = pg.font.SysFont("consolas,roboto,arial", 70, bold=True)
    font = pg.font.SysFont("consolas,roboto,arial", 28)
    victory_surface = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT))

    confeti = generar_confeti(120)
    frame = 0
    waiting = True

    while waiting:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.KEYDOWN:
                if event.key in [pg.K_RETURN, pg.K_SPACE]:
                    return

        # Fondo degradado dinámico
        victory_surface.fill((30, 30, 80))
        for i in range(cfg.LOGICAL_HEIGHT):
            color = (30, 30, 80 + i // 10)
            pg.draw.line(victory_surface, color, (0, i), (cfg.LOGICAL_WIDTH, i))

        # Actualizar y dibujar confeti
        for c in confeti:
            c[1] += c[3]
            if c[1] > cfg.LOGICAL_HEIGHT:
                c[0] = random.randint(0, cfg.LOGICAL_WIDTH)
                c[1] = random.randint(-50, -10)
            pg.draw.rect(victory_surface, c[2], (c[0], int(c[1]), c[4], c[4]))

        # Título con efecto pulso
        scale = 1 + 0.05 * math.sin(frame * 0.1)
        title = big_font.render("¡HAS GANADO!", True, cfg.GREEN)
        title = pg.transform.rotozoom(title, 0, scale)
        victory_surface.blit(
            title,
            title.get_rect(
                center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2 - 100)
            ),
        )

        # Hint parpadeante
        alpha = 200 + 55 * math.sin(frame * 0.1)
        hint = font.render("Presiona ENTER para volver al menú", True, cfg.WHITE)
        hint.set_alpha(alpha)
        victory_surface.blit(
            hint,
            hint.get_rect(center=(cfg.LOGICAL_WIDTH / 2, cfg.LOGICAL_HEIGHT / 2 + 100)),
        )

        # Escalar a la pantalla real
        scaled_surface = pg.transform.smoothscale(victory_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))

        pg.display.flip()
        clock.tick(cfg.FPS)
        frame += 1
