import pygame as pg
import sys
import math
import random
import settings as cfg
from .options import loop_options

# Opciones del menú principal
opciones = ["Jugar", "Opciones", "Salir"]
opcion_seleccionada = -1  # Ninguna opción seleccionada al abrir

# Fondo animado (estrellas con movimiento aleatorio)
estrellas = [
    {
        "pos": pg.Vector2(random.randint(0, cfg.ANCHO), random.randint(0, cfg.ALTO)),
        "vel": random.uniform(20, 80),
        "color": (random.randint(150, 255),) * 3,
        "radio": random.choice([1, 2, 2, 3]),
    }
    for _ in range(100)
]


def actualizar_fondo(dt):
    for estrella in estrellas:
        estrella["pos"].y += estrella["vel"] * dt
        if estrella["pos"].y > cfg.ALTO:
            estrella["pos"].y = -10
            estrella["pos"].x = random.randint(0, cfg.ANCHO)


def dibujar_fondo():
    cfg.VENTANA.fill((10, 10, 30))
    for estrella in estrellas:
        pg.draw.circle(
            cfg.VENTANA,
            estrella["color"],
            (int(estrella["pos"].x), int(estrella["pos"].y)),
            estrella["radio"],
        )


def dibujar_titulo(tiempo):
    """Dibuja el título animado con efecto respiración y flotación"""
    fuente = cfg.get_fuente(0.15)
    texto = "Alien Slayer"  # Nombre del juego

    # Efecto respiración (brillo)
    alpha = int((math.sin(tiempo * 2) + 1) * 127)

    # Movimiento vertical sutil
    offset_y = int(math.sin(tiempo) * 10)

    render = fuente.render(texto, True, cfg.ROJO)
    render.set_alpha(alpha)
    rect = render.get_rect(center=(cfg.ANCHO // 2, int(cfg.ALTO * 0.25) + offset_y))

    # Sombra para más impacto
    sombra = fuente.render(texto, True, (30, 0, 0))
    sombra_rect = rect.copy()
    sombra_rect.move_ip(4, 4)
    cfg.VENTANA.blit(sombra, sombra_rect)

    cfg.VENTANA.blit(render, rect)


def dibujar_menu(mouse_pos=None, mouse_pressed=False):
    fuente = cfg.get_fuente(0.07)

    rects = []
    hover_index = -1

    # Detectar hover
    for i, texto in enumerate(opciones):
        y = int(cfg.ALTO // 2 + i * 100 * cfg.escala_y)
        render = fuente.render(texto, True, cfg.BLANCO)
        rect = render.get_rect(center=(cfg.ANCHO // 2, y))
        rects.append(rect)

        if mouse_pos and rect.collidepoint(mouse_pos):
            hover_index = i

    # Dibujar opciones
    for i, texto in enumerate(opciones):
        rect = rects[i]

        if i == hover_index:
            color = (200, 50, 50) if mouse_pressed else cfg.ROJO
        elif opcion_seleccionada == i:
            color = cfg.ROJO
        else:
            color = cfg.BLANCO

        # Sombra ligera
        sombra = fuente.render(texto, True, (30, 30, 30))
        sombra_rect = rect.copy()
        sombra_rect.move_ip(3, 3)
        cfg.VENTANA.blit(sombra, sombra_rect)

        render = fuente.render(texto, True, color)
        cfg.VENTANA.blit(render, rect)

    return rects


def loop_menu(clock, loop_juego):
    global opcion_seleccionada
    opcion_seleccionada = -1  # Reiniciar al abrir
    tiempo = 0

    while True:
        dt = clock.tick(cfg.FPS) / 1000.0
        tiempo += dt
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]

        actualizar_fondo(dt)
        dibujar_fondo()
        dibujar_titulo(tiempo)
        rects = dibujar_menu(mouse_pos, mouse_pressed)

        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Navegación por teclado
            if evento.type == pg.KEYDOWN:
                if opcion_seleccionada == -1:
                    opcion_seleccionada = 0
                if evento.key in (pg.K_UP, pg.K_w):
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                if evento.key in (pg.K_DOWN, pg.K_s):
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)
                if evento.key in (pg.K_RETURN, pg.K_SPACE) and opcion_seleccionada >= 0:
                    accion = opciones[opcion_seleccionada]
                    if accion == "Jugar":
                        return loop_juego(cfg.VENTANA, clock)
                    elif accion == "Opciones":
                        loop_options(clock)
                    elif accion == "Salir":
                        pg.quit()
                        sys.exit()

            # Click del mouse
            if evento.type == pg.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mx, my):
                        opcion_seleccionada = i
                        accion = opciones[i]
                        if accion == "Jugar":
                            print(cfg.VENTANA, clock)
                            return loop_juego(cfg.VENTANA, clock)
                        elif accion == "Opciones":
                            loop_options(clock)
                        elif accion == "Salir":
                            pg.quit()
                            sys.exit()

        pg.display.flip()
