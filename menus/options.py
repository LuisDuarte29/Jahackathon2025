# options.py
# Este archivo maneja el MENÚ DE OPCIONES del juego.
# Aquí el jugador puede ajustar configuraciones como el volumen
# y regresar al menú principal.

import pygame as pg
import sys
import settings as cfg
# pygame para manejar la parte gráfica y sys para salir del programa


# Opciones disponibles en este menú
opciones = ["Volumen", "Volver"]

# Índice de la opción seleccionada actualmente
opcion_seleccionada = 0

# Valor inicial del volumen (entre 0.0 y 1.0)
volumen_actual = 0.5  


def dibujar_options():
    """
    Esta función dibuja el menú de opciones en pantalla,
    incluyendo las etiquetas y la barra de volumen centradas.
    """
    cfg.VENTANA.fill(cfg.GRIS)  # Fondo gris del menú de opciones
    fuente = cfg.get_fuente(0.07)  # Tamaño de letra relativo a la resolución

    # Recorremos todas las opciones del menú
    for i, texto in enumerate(opciones):
        color = cfg.ROJO if i == opcion_seleccionada else cfg.BLANCO

        # Renderizamos el texto en una superficie
        render = fuente.render(texto, True, color)
        texto_ancho = render.get_width()
        texto_alto = render.get_height()

        # Separación vertical de cada opción
        y = int(cfg.ALTO // 2 + i * 100 * cfg.escala_y)

        if texto == "Volumen":
            barra_width = 200
            barra_height = 20
            espacio = 20
            total_ancho = texto_ancho + espacio + barra_width
            start_x = (cfg.ANCHO - total_ancho) // 2
            cfg.VENTANA.blit(render, (start_x, y - texto_alto // 2))
            barra_x = start_x + texto_ancho + espacio
            barra_y = y - barra_height // 2
            pg.draw.rect(cfg.VENTANA, cfg.BLANCO, (barra_x, barra_y, barra_width, barra_height), 2)
            filled = int(barra_width * volumen_actual)
            pg.draw.rect(cfg.VENTANA, cfg.ROJO, (barra_x, barra_y, filled, barra_height))
        else:
            rect = render.get_rect(center=(cfg.ANCHO // 2, y))
            cfg.VENTANA.blit(render, rect)



def loop_options(clock):
    """
    Bucle principal del menú de opciones.
    Aquí controlamos la interacción con el teclado.
    """
    global opcion_seleccionada, volumen_actual
    
    while True:
        # Recorremos todos los eventos de pygame
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if evento.type == pg.KEYDOWN:
                if evento.key in (pg.K_UP, pg.K_w):
                    opcion_seleccionada = (opcion_seleccionada - 1) % len(opciones)
                if evento.key in (pg.K_DOWN, pg.K_s):
                    opcion_seleccionada = (opcion_seleccionada + 1) % len(opciones)

                if opcion_seleccionada == 0:
                    if evento.key in (pg.K_RIGHT, pg.K_d):
                        volumen_actual = min(volumen_actual + 0.1, 1.0)
                    if evento.key in (pg.K_LEFT, pg.K_a):
                        volumen_actual = max(volumen_actual - 0.1, 0.0)

                elif opcion_seleccionada == 1:
                    if evento.key in (pg.K_RETURN, pg.K_SPACE):
                        return

        dibujar_options()
        pg.display.flip()
        clock.tick(cfg.FPS)