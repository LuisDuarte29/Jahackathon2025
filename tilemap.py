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
            # generar mapa aleatorio simple
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
                # Usamos la imagen de suelo cargada
                self.background_image.blit(
                    self.floor_image, (col * cfg.TILESIZE, row * cfg.TILESIZE)
                )

    def render(self, surface):
        """Dibuja el fondo y los muros en la superficie del juego."""
        # Dibuja el suelo
        surface.blit(self.background_image, (0, 0))
        # Dibuja los muros (que son sprites y se dibujan en el bucle principal)

    def make_map(self):
        """Crea los sprites de los muros a partir del archivo de mapa."""
        # Antes de crear muros, asegurar que la salida y sus adyacentes sean transitable
        self._ensure_exit_accessible()

        self.walls = pg.sprite.Group()
        self.exit_pos = None
        for row, tiles in enumerate(self.data):
            for col, tile in enumerate(tiles):
                if tile == "1":
                    # Añade un muro usando la imagen de muro cargada
                    self.walls.add(
                        Tile(col * cfg.TILESIZE, row * cfg.TILESIZE, self.wall_image)
                    )
                elif tile == "X":
                    # Guardar posición en píxeles (centro de la tile)
                    self.exit_pos = (
                        col * cfg.TILESIZE + cfg.TILESIZE // 2,
                        row * cfg.TILESIZE + cfg.TILESIZE // 2,
                    )
        return self.walls, self.exit_pos

    def _ensure_exit_accessible(self):
        """Asegura que la salida 'X' tenga un pasillo estrecho hacia el centro del mapa.
        En lugar de despejar todo el entorno, determinamos la dirección hacia el centro
        y convertimos 1-2 tiles en esa dirección a suelo '0', dejando la 'X' en su lugar.
        """
        # Buscar la salida en self.data
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

        # Centro del mapa (en tiles)
        cx = self.tilewidth // 2
        cy = self.tileheight // 2

        dx = cx - ex
        dy = cy - ey

        # Determinar dirección principal hacia el centro (unit vector -1/0/1)
        if abs(dx) >= abs(dy):
            dirx = 1 if dx > 0 else -1
            diry = 0
        else:
            dirx = 0
            diry = 1 if dy > 0 else -1

        # Convertir a lista mutable de listas
        grid = [list(row) for row in self.data]

        # Limpiar 1 o 2 tiles hacia el interior para crear un pasillo estrecho
        for dist in (1, 2):
            nx = ex + dirx * dist
            ny = ey + diry * dist
            if 0 <= ny < len(grid) and 0 <= nx < len(grid[0]):
                # No tocar si es la propia 'X'
                if not (nx == ex and ny == ey):
                    grid[ny][nx] = "0"

        # Reconvertir a strings
        self.data = ["".join(row) for row in grid]

    def _generate_random_map(self):
        """Generador simple: random fill + smoothing (cellular automata).
        Marca '1' para muros y '0' para suelo. Añade una 'X' en un muro de borde.
        """
        data = []
        for r in range(self.tileheight):
            row = ""
            for c in range(self.tilewidth):
                # bordes fijos
                if (
                    r == 0
                    or r == self.tileheight - 1
                    or c == 0
                    or c == self.tilewidth - 1
                ):
                    row += "1"
                else:
                    row += "1" if random.random() < 0.42 else "0"
            data.append(row)

        # Smoothing iterations
        def count_wall_neighbors(d, rr, cc):
            cnt = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    r2 = rr + dr
                    c2 = cc + dc
                    if (
                        r2 < 0
                        or r2 >= self.tileheight
                        or c2 < 0
                        or c2 >= self.tilewidth
                    ):
                        cnt += 1
                    elif d[r2][c2] == "1":
                        cnt += 1
            return cnt

        for _ in range(3):
            new = []
            for r in range(self.tileheight):
                row = ""
                for c in range(self.tilewidth):
                    if (
                        r == 0
                        or r == self.tileheight - 1
                        or c == 0
                        or c == self.tilewidth - 1
                    ):
                        row += "1"
                        continue
                    neighbors = count_wall_neighbors(data, r, c)
                    if neighbors >= 5:
                        row += "1"
                    else:
                        row += "0"
                new.append(row)
            data = new

        # Colocar una salida 'X' en un muro de borde aleatorio
        border_positions = []
        for c in range(1, self.tilewidth - 1):
            if data[0][c] == "1":
                border_positions.append((c, 0))
            if data[self.tileheight - 1][c] == "1":
                border_positions.append((c, self.tileheight - 1))
        for r in range(1, self.tileheight - 1):
            if data[r][0] == "1":
                border_positions.append((0, r))
            if data[r][self.tilewidth - 1] == "1":
                border_positions.append((self.tilewidth - 1, r))

        if border_positions:
            sx, sy = random.choice(border_positions)
            row_list = list(data[sy])
            row_list[sx] = "X"
            data[sy] = "".join(row_list)

        self.data = data
