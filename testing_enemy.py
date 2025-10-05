import pygame as pg

pg.init()

img = pg.image.load("assets/blaster_norte.png")
print("player_norte.png size:", img.get_size())

img = pg.image.load("assets/blaster_sur.png")
print("player_sur.png size:", img.get_size())

img = pg.image.load("assets/blaster_este.png")
print("player_este.png size:", img.get_size())

img = pg.image.load("assets/blaster_oeste.png")
print("player_oeste.png size:", img.get_size())
