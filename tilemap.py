import pygame as pg
import settings as cfg
from pathlib import Path
import random
from sprites import load_image  # Usamos la función de sprites.py para cargar imágenes


class Tile(pg.sprite.Sprite):
    """Representa una única baldosa del mapa, usando una imagen."""

    def __init__(self, x, y, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)


class Map:
    def __init__(self, filename):
        # Intentar cargar imágenes desde assets; si fallan, usar placeholders
        try:
            wall_img = load_image("wall.png")
        except Exception:
            wall_img = pg.Surface((cfg.TILESIZE, cfg.TILESIZE))
            wall_img.fill((100, 100, 100))
            print("Warning: wall.png not found, using placeholder")

        try:
            floor_img = load_image("floor.png")
        except Exception:
            floor_img = pg.Surface((cfg.TILESIZE, cfg.TILESIZE))
            floor_img.fill((40, 40, 40))
            print("Warning: floor.png not found, using placeholder")

        # Escalamos las imágenes al tamaño definido en TILESIZE
        self.wall_image = pg.transform.scale(wall_img, (cfg.TILESIZE, cfg.TILESIZE))
        self.floor_image = pg.transform.scale(floor_img, (cfg.TILESIZE, cfg.TILESIZE))

        # Soporta filename == 'RANDOM' para generar mapas procedurales
        self.data = []
        if isinstance(filename, str) and filename.upper() == "RANDOM":
            self.tilewidth = 20
            self.tileheight = 12
            self._generate_random_map()
        else:
            # Leemos el archivo de mapa desde la carpeta maps
            map_path = Path("maps") / filename
            self.data = []
            with open(map_path, "rt") as f:
                for line in f:
                    self.data.append(line.strip())
            self.tilewidth = len(self.data[0])
            self.tileheight = len(self.data)

        # Creamos una imagen de fondo pre-renderizada para el suelo
        self.background_image = pg.Surface(
            (self.tilewidth * cfg.TILESIZE, self.tileheight * cfg.TILESIZE)
        )
        self.render_background()

    def render_background(self):
        """Dibuja todas las baldosas de suelo en la imagen de fondo."""
        for row, tiles in enumerate(self.data):
            for col, tile in enumerate(tiles):
                self.background_image.blit(
                    self.floor_image, (col * cfg.TILESIZE, row * cfg.TILESIZE)
                )

    def render(self, surface):
        """Dibuja el fondo y los muros en la superficie del juego."""
        # Dibuja el suelo
        surface.blit(self.background_image, (0, 0))
        # Los muros se dibujan en el bucle principal como sprites

    def make_map(self):
        """Crea los sprites de los muros a partir del archivo de mapa."""
        # Asegura que la salida sea accesible
        self._ensure_exit_accessible()

        self.walls = pg.sprite.Group()
        self.exit_pos = None
        for row, tiles in enumerate(self.data):
            for col, tile in enumerate(tiles):
                if tile == "1":
                    self.walls.add(
                        Tile(col * cfg.TILESIZE, row * cfg.TILESIZE, self.wall_image)
                    )
                elif tile == "X":
                    self.exit_pos = (
                        col * cfg.TILESIZE + cfg.TILESIZE // 2,
                        row * cfg.TILESIZE + cfg.TILESIZE // 2,
                    )
        return self.walls, self.exit_pos

    def _ensure_exit_accessible(self):
        """Asegura que la salida 'X' tenga al menos 1 tile libre hacia el centro."""
        ex = ey = None
        for r, row in enumerate(self.data):
            for c, ch in enumerate(row):
                if ch == "X":
                    ex, ey = c, r
                    break
            if ex is not None:
                break
        if ex is None:
            return

        cx = self.tilewidth // 2
        cy = self.tileheight // 2

        dx = cx - ex
        dy = cy - ey

        dirx = 1 if dx > 0 else -1 if dx < 0 else 0
        diry = 1 if dy > 0 else -1 if dy < 0 else 0

        grid = [list(row) for row in self.data]

        for dist in (1, 2):
            nx = ex + dirx * dist
            ny = ey + diry * dist
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                if not (nx == ex and ny == ey):
                    grid[ny][nx] = "0"

        self.data = ["".join(row) for row in grid]

    def _generate_random_map(self):
        """Genera un mapa con suelo, paredes en bordes, obstáculos internos y salida."""
        # Paso 1: crear solo suelo
        data = [["0" for c in range(self.tilewidth)] for r in range(self.tileheight)]

        # Paso 2: rodear de muros
        for r in range(self.tileheight):
            for c in range(self.tilewidth):
                if r == 0 or r == self.tileheight - 1 or c == 0 or c == self.tilewidth - 1:
                    data[r][c] = "1"

        # Paso 3: colocar algunos obstáculos internos aleatorios (10% de tiles interiores)
        for r in range(1, self.tileheight - 1):
            for c in range(1, self.tilewidth - 1):
                if random.random() < 0.1:
                    data[r][c] = "1"

        # Paso 4: elegir una tile de suelo aleatoria para la salida
        floor_positions = [
            (r, c)
            for r in range(1, self.tileheight - 1)
            for c in range(1, self.tilewidth - 1)
            if data[r][c] == "0"
        ]
        if floor_positions:
            ey, ex = random.choice(floor_positions)
            data[ey][ex] = "X"

        self.data = ["".join(row) for row in data]
