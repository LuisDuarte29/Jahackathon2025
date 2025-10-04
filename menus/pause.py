# pause.py
# Este archivo maneja el MENÚ DE PAUSA del juego.
# Se activa cuando el jugador presiona ESC durante el juego.
# Permite continuar, ir a opciones o salir al menú principal.

import pygame as pg
import sys
import settings as cfg

from .options import loop_options
# Importamos el menú de opciones para poder entrar a él desde la pausa

# Opciones disponibles en el menú de pausa
opciones = ["Seguir", "Opciones", "Salir al menú"]

# Índice que indica la opción actualmente seleccionada
opcion_seleccionada = 0


def dibujar_pausa():
    """
    Función que dibuja el menú de pausa en pantalla.
    Muestra un título y las opciones con la opción seleccionada resaltada.
    """
    cfg.VENTANA.fill(cfg.GRIS)

    fuente = cfg.get_fuente(0.07)
    titulo = cfg.get_fuente(0.1).render("Pausa", True, cfg.BLANCO)
    rect_titulo = titulo.get_rect(center=(cfg.ANCHO // 2, cfg.ALTO // 4))
    cfg.VENTANA.blit(titulo, rect_titulo)

    # Recorremos todas las opciones del menú
    for i, texto in enumerate(opciones):
        color = cfg.ROJO if i == opcion_seleccionada else cfg.BLANCO
        render = fuente.render(texto, True, color)
        rect = render.get_rect(center=(cfg.ANCHO // 2, int(cfg.ALTO // 2 + i * 100 * cfg.escala_y)))
        cfg.VENTANA.blit(render, rect)


def loop_pausa(clock):
    """
    Bucle principal del menú de pausa.
    Maneja la navegación con teclado y la selección de opciones.
    """
    global opcion_seleccionada
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
                    if opciones[opcion_seleccionada] == "Seguir":
                        return "seguir"
                    elif opciones[opcion_seleccionada] == "Opciones":
                        loop_options(clock)
                    elif opciones[opcion_seleccionada] == "Salir al menú":
                        return "menu"

        dibujar_pausa()
        pg.display.flip()
        clock.tick(cfg.FPS)