"""Lanzador para el juego modularizado.

Este main.py inicializa pygame y ejecuta el menú principal desde
`menus.main_menu.loop_menu`. Cuando el jugador elige "Inicio", el
menú llamará a `game.loop_juego` para iniciar el juego.
"""

import pygame as pg
from menus.main_menu import loop_menu
import game

def main():
    # Inicializar pygame
    pg.init()
    pg.display.set_caption("Jahackathon 2025 - Roguelike")

    # Crear reloj de pygame para controlar FPS
    clock = pg.time.Clock()

    # Ejecutar el menú principal; al seleccionar "Inicio" se llamará a game.loop_juego
    loop_menu(clock, game.loop_juego)

    # Salir de pygame al terminar
    pg.quit()


if __name__ == '__main__':
    main()
