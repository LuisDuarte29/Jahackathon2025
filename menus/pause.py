import pygame as pg
import sys
import settings as cfg
from .options import loop_options

# Opciones del menú de pausa
opciones = ["Seguir", "Opciones", "Salir al menú"]
opcion_seleccionada = -1  # Ninguna opción seleccionada al abrir

def dibujar_pausa(mouse_pos=None, mouse_pressed=False):
    cfg.VENTANA.fill(cfg.GRIS)
    fuente = cfg.get_fuente(0.07)
    
    # Título
    titulo = cfg.get_fuente(0.1).render("Pausa", True, cfg.BLANCO)
    rect_titulo = titulo.get_rect(center=(cfg.ANCHO // 2, cfg.ALTO // 4))
    cfg.VENTANA.blit(titulo, rect_titulo)

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

    # Dibujar opciones con prioridad a hover
    for i, texto in enumerate(opciones):
        rect = rects[i]
        if i == hover_index:
            color = (150, 0, 0) if mouse_pressed else cfg.ROJO
        elif hover_index == -1 and opcion_seleccionada >= 0 and i == opcion_seleccionada:
            color = cfg.ROJO
        else:
            color = cfg.BLANCO

        render = fuente.render(texto, True, color)
        cfg.VENTANA.blit(render, rect)

    return rects

def loop_pausa(clock):
    global opcion_seleccionada
    opcion_seleccionada = -1  # Reiniciar al abrir

    while True:
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        rects = dibujar_pausa(mouse_pos, mouse_pressed)

        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit(); sys.exit()

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
                        return "menu"

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
                            return "menu"

        pg.display.flip()
        clock.tick(cfg.FPS)
