# menu.py
# Este archivo controla el MENÚ PRINCIPAL del juego.
# Aquí se definen las opciones (Inicio, Opciones, Salir),
# cómo se dibujan en pantalla y cómo el jugador interactúa con ellas.

import pygame as pg
import sys
import settings as cfg
# relative import to work when `menus` is imported as a package
from .options import loop_options
# Usamos cfg.VENTANA, cfg.FPS, cfg.get_fuente, cfg.ANCHO/ALTO (aliases WIDTH/HEIGHT también disponibles)

# Lista con las opciones del menú principal
opciones = ["Inicio", "Opciones", "Salir"]

# Índice que indica cuál opción está seleccionada actualmente
opcion_seleccionada = 0


def dibujar_menu():
    """Dibuja el menú en pantalla, con las opciones centradas y resaltando la opción seleccionada."""
    cfg.VENTANA.fill(cfg.GRIS)
    fuente = cfg.get_fuente(0.07)
    for i, texto in enumerate(opciones):
        color = cfg.ROJO if i == opcion_seleccionada else cfg.BLANCO
        render = fuente.render(texto, True, color)
        rect = render.get_rect(center=(cfg.ANCHO // 2, int(cfg.ALTO // 2 + i * 100 * cfg.escala_y)))
        cfg.VENTANA.blit(render, rect)


def loop_menu(clock, loop_juego):
    """
    Bucle principal del menú.
    Controla los eventos del teclado y decide si el jugador empieza el juego,
    entra en opciones o sale.
    """
    global opcion_seleccionada  # Necesitamos modificar la variable global que guarda la opción
    
    while True:
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit(); sys.exit()
            if evento.type == pg.KEYDOWN:
                if evento.key in (pg.K_UP, pg.K_w):
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                if evento.key in (pg.K_DOWN, pg.K_s):
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)
                if evento.key in (pg.K_RETURN, pg.K_SPACE):
                    if opciones[opcion_seleccionada] == "Inicio":
                        # start game; pass the main surface and clock
                        return loop_juego(cfg.VENTANA, clock)
                    elif opciones[opcion_seleccionada] == "Opciones":
                        loop_options(clock)
                    elif opciones[opcion_seleccionada] == "Salir":
                        pg.quit(); sys.exit()

        dibujar_menu()
        pg.display.flip()
        clock.tick(cfg.FPS)