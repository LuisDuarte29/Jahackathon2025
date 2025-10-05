import pygame as pg
import sys
import math
import settings as cfg
from .options import loop_options
from menus.main_menu import loop_menu
import game
from menus.main_menu import loop_menu

# Opciones del menú de pausa
opciones = ["Seguir", "Opciones", "Salir al menú"]
opcion_seleccionada = -1  # Ninguna opción seleccionada al abrir


def dibujar_pausa(mouse_pos=None, mouse_pressed=False, frame=0):
    # Fondo semitransparente
    overlay = pg.Surface((cfg.ANCHO, cfg.ALTO))
    overlay.set_alpha(180)
    overlay.fill((30, 30, 30))  # gris oscuro
    cfg.VENTANA.blit(overlay, (0, 0))

    fuente = cfg.get_fuente(0.07)

    # Título con "efecto pulso"
    escala = 1 + 0.02 * math.sin(frame * 0.05)  # pequeño efecto de zoom
    titulo_font = cfg.get_fuente(0.1)
    titulo = titulo_font.render("Pausa", True, cfg.BLANCO)
    titulo = pg.transform.rotozoom(titulo, 0, escala)
    rect_titulo = titulo.get_rect(center=(cfg.ANCHO // 2, cfg.ALTO // 4))
    cfg.VENTANA.blit(titulo, rect_titulo)

    rects = []
    hover_index = -1

    # Detectar hover
    for i, texto in enumerate(opciones):
        y = int(cfg.ALTO // 2 + i * 100 * cfg.escala_y)
        rect = pg.Rect(0, 0, 350 * cfg.escala_x, 70 * cfg.escala_y)
        rect.center = (cfg.ANCHO // 2, y)
        rects.append(rect)

        if mouse_pos and rect.collidepoint(mouse_pos):
            hover_index = i

    # Dibujar botones
    for i, texto in enumerate(opciones):
        rect = rects[i]

        # Estado hover / seleccionado
        if i == hover_index:
            color_fondo = (180, 50, 50)
        elif (
            hover_index == -1 and opcion_seleccionada >= 0 and i == opcion_seleccionada
        ):
            color_fondo = (180, 50, 50)
        else:
            color_fondo = (80, 80, 80)

        # Dibujar rectángulo de botón
        pg.draw.rect(cfg.VENTANA, color_fondo, rect, border_radius=15)
        pg.draw.rect(cfg.VENTANA, (255, 255, 255), rect, 3, border_radius=15)

        # Texto centrado
        render = fuente.render(texto, True, cfg.BLANCO)
        text_rect = render.get_rect(center=rect.center)
        cfg.VENTANA.blit(render, text_rect)

    return rects


def loop_pausa(clock):
    global opcion_seleccionada
    opcion_seleccionada = -1  # Reiniciar al abrir
    frame = 0

    while True:
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        rects = dibujar_pausa(mouse_pos, mouse_pressed, frame)

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
                    if accion == "Seguir":
                        return "seguir"
                    elif accion == "Opciones":
                        loop_options(clock)
                    elif accion == "Salir al menú":
                         loop_menu(clock,game.loop_juego)
                    

            # Click del mouse
            if evento.type == pg.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mx, my):
                        opcion_seleccionada = i
                        accion = opciones[i]
                        if accion == "Seguir":
                            return "seguir"
                        elif accion == "Opciones":
                            loop_options(clock)
                        elif accion == "Salir al menú":
                         loop_menu(clock,game.loop_juego)

        pg.display.flip()
        clock.tick(cfg.FPS)
        frame += 1
