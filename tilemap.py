import pygame as pg
import settings as cfg
from sprites import load_image # Usamos la función de sprites.py para cargar imágenes

class Tile(pg.sprite.Sprite):
    """Representa una única baldosa del mapa, usando una imagen."""
    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

class Map:
    def __init__(self, filename):
        # --- CORRECCIÓN: Se especifica la ruta desde la carpeta 'assets' ---
        # Cargamos las imágenes originales de los assets.
        wall_img = load_image('assets/wall.png')
        floor_img = load_image('assets/floor.png')
        
        # Escalamos las imágenes al tamaño definido en TILESIZE
        self.wall_image = pg.transform.scale(wall_img, (cfg.TILESIZE, cfg.TILESIZE))
        self.floor_image = pg.transform.scale(floor_img, (cfg.TILESIZE, cfg.TILESIZE))
        
        # Leemos el archivo de mapa
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())
        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        
        # Creamos una imagen de fondo pre-renderizada para el suelo
        self.background_image = pg.Surface((self.tilewidth * cfg.TILESIZE, self.tileheight * cfg.TILESIZE))
        self.render_background()

    def render_background(self):
        """Dibuja todas las baldosas de suelo en la imagen de fondo."""
        for row, tiles in enumerate(self.data):
            for col, tile in enumerate(tiles):
                # Usamos la imagen de suelo cargada
                self.background_image.blit(self.floor_image, (col * cfg.TILESIZE, row * cfg.TILESIZE))

    def render(self, surface):
        """Dibuja el fondo y los muros en la superficie del juego."""
        # Dibuja el suelo
        surface.blit(self.background_image, (0, 0))
        # Dibuja los muros (que son sprites y se dibujan en el bucle principal)

    def make_map(self):
        """Crea los sprites de los muros a partir del archivo de mapa."""
        self.walls = pg.sprite.Group()
        self.exit_pos = None
        for row, tiles in enumerate(self.data):
            for col, tile in enumerate(tiles):
                if tile == '1':
                    # Añade un muro usando la imagen de muro cargada
                    self.walls.add(Tile(col * cfg.TILESIZE, row * cfg.TILESIZE, self.wall_image))
                elif tile == 'X':
                    self.exit_pos = (col * cfg.TILESIZE, row * cfg.TILESIZE)
        return self.walls, self.exit_pos