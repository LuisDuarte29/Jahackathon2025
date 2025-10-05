import pygame

pygame.init()
from tilemap import Map

m = Map("RANDOM")
walls, exit_pos = m.make_map()
print("Map generated:", len(m.data), "rows,", len(m.data[0]), "cols")
print("Walls:", len(walls), "Exit:", exit_pos)
