import pygame as pg
import sys
import settings as cfg

opciones = ["Volumen", "Volver"]
opcion_seleccionada = -1  # Ninguna opción seleccionada al abrir
volumen_actual = 0.5  # Valor inicial del volumen

def dibujar_options(mouse_pos=None, mouse_pressed=False):
    cfg.VENTANA.fill(cfg.GRIS)
    fuente = cfg.get_fuente(0.07)
    
    rects = []
    hover_index = -1

    # Detectar hover
    for i, texto in enumerate(opciones):
        y = int(cfg.ALTO // 2 + i * 100 * cfg.escala_y)

        if texto == "Volumen":
            render = fuente.render(texto, True, cfg.BLANCO)
            texto_ancho = render.get_width()
            texto_alto = render.get_height()
            barra_width = 200
            barra_height = 20
            espacio = 20
            total_ancho = texto_ancho + espacio + barra_width
            start_x = (cfg.ANCHO - total_ancho) // 2
            barra_x = start_x + texto_ancho + espacio
            barra_y = y - barra_height // 2

            # Rect del texto + barra para hover
            rect = pg.Rect(start_x, y - texto_alto//2, total_ancho, max(texto_alto, barra_height))
        else:
            render = fuente.render(texto, True, cfg.BLANCO)
            rect = render.get_rect(center=(cfg.ANCHO // 2, y))

        rects.append(rect)
        if mouse_pos and rect.collidepoint(mouse_pos):
            hover_index = i

    # Dibujar opciones
    for i, texto in enumerate(opciones):
        rect = rects[i]
        y = int(cfg.ALTO // 2 + i * 100 * cfg.escala_y)

        if i == hover_index:
            color = (150, 0, 0) if mouse_pressed else cfg.ROJO
        elif hover_index == -1 and opcion_seleccionada >= 0 and i == opcion_seleccionada:
            color = cfg.ROJO
        else:
            color = cfg.BLANCO

        if texto == "Volumen":
            render = fuente.render(texto, True, color)
            texto_ancho = render.get_width()
            barra_width = 200
            barra_height = 20
            espacio = 20
            total_ancho = texto_ancho + espacio + barra_width
            start_x = (cfg.ANCHO - total_ancho) // 2
            barra_x = start_x + texto_ancho + espacio
            barra_y = y - barra_height // 2
            cfg.VENTANA.blit(render, (start_x, y - render.get_height()//2))
            pg.draw.rect(cfg.VENTANA, cfg.BLANCO, (barra_x, barra_y, barra_width, barra_height), 2)
            filled = int(barra_width * volumen_actual)
            pg.draw.rect(cfg.VENTANA, cfg.ROJO, (barra_x, barra_y, filled, barra_height))
        else:
            render = fuente.render(texto, True, color)
            cfg.VENTANA.blit(render, rect)

    return rects, hover_index  # <-- Retornamos hover_index para usarlo fuera

def loop_options(clock):
    global opcion_seleccionada, volumen_actual
    opcion_seleccionada = -1  # Reiniciar al abrir

    while True:
        mouse_pos = pg.mouse.get_pos()
        mouse_pressed = pg.mouse.get_pressed()[0]
        rects, hover_index = dibujar_options(mouse_pos, mouse_pressed)

        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Navegación con teclado
            if evento.type == pg.KEYDOWN:
                if opcion_seleccionada == -1:
                    opcion_seleccionada = 0
                if evento.key in (pg.K_UP, pg.K_w):
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                if evento.key in (pg.K_DOWN, pg.K_s):
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)

                # Ajuste de volumen con teclas
                if opcion_seleccionada == 0:
                    if evento.key in (pg.K_RIGHT, pg.K_d):
                        volumen_actual = min(volumen_actual + 0.1, 1.0)
                    if evento.key in (pg.K_LEFT, pg.K_a):
                        volumen_actual = max(volumen_actual - 0.1, 0.0)
                # Volver
                elif opcion_seleccionada == 1:
                    if evento.key in (pg.K_RETURN, pg.K_SPACE):
                        return

            # Click del mouse
            if evento.type == pg.MOUSEBUTTONDOWN and evento.button == 1:
                mx, my = evento.pos
                for i, rect in enumerate(rects):
                    if rect.collidepoint(mx, my):
                        opcion_seleccionada = i
                        if opciones[i] == "Volver":
                            return
                        elif opciones[i] == "Volumen":
                            # Ajustar volumen al click en la barra
                            barra_width = 200
                            texto_render = cfg.get_fuente(0.07).render("Volumen", True, cfg.BLANCO)
                            texto_ancho = texto_render.get_width()
                            espacio = 20
                            total_ancho = texto_ancho + espacio + barra_width
                            start_x = (cfg.ANCHO - total_ancho) // 2
                            barra_x = start_x + texto_ancho + espacio
                            volumen_actual = max(0.0, min(1.0, (mx - barra_x) / barra_width))

            # Drag para la barra de volumen
            if evento.type == pg.MOUSEMOTION and mouse_pressed and hover_index == 0:
                mx, my = evento.pos
                barra_width = 200
                texto_render = cfg.get_fuente(0.07).render("Volumen", True, cfg.BLANCO)
                texto_ancho = texto_render.get_width()
                espacio = 20
                total_ancho = texto_ancho + espacio + barra_width
                start_x = (cfg.ANCHO - total_ancho) // 2
                barra_x = start_x + texto_ancho + espacio
                volumen_actual = max(0.0, min(1.0, (mx - barra_x) / barra_width))

        pg.display.flip()
        clock.tick(cfg.FPS)
