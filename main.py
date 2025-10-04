"""Launcher for the modularized game.

This main.py initializes pygame and runs the main menu from
`menus.main_menu.loop_menu`. When the player chooses "Inicio", the
menu will call `game.loop_juego` to start the game.
"""

import pygame as pg
from settings import VENTANA, FPS
from menus.main_menu import loop_menu
import game


def main():
    # pygame is already initialized in settings, but ensure a Clock exists
    clock = pg.time.Clock()
    # Run the menu which will call into game.loop_juego when "Inicio" chosen
    loop_menu(clock, game.loop_juego)


if __name__ == '__main__':
    main()
