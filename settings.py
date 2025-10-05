# settings.py
import pygame

# --- Inicialización ---
pygame.init()

# --- Resolución ---
info = pygame.display.Info()
ANCHO, ALTO = info.current_w, info.current_h
VENTANA = pygame.display.set_mode((ANCHO, ALTO), pygame.FULLSCREEN)

# Basado en los mapas de 20x12 tiles (20*64=1280, 12*64=768)
LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 768

# Resolución base para escalado
BASE_ANCHO, BASE_ALTO = 1280, 720
escala_x = ANCHO / BASE_ANCHO
escala_y = ALTO / BASE_ALTO

# --- FPS ---
FPS = 60

# --- Colores ---
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROJO = (220, 60, 60)
GRIS = (120, 120, 120)
AMARILLO = (240, 220, 0)  # para balas, HUD, etc.
VERDE = (60, 200, 80)
BG = (18, 18, 24)
ENEMY_COLOR = (200, 90, 90)

# --- Jugabilidad base ---
PLAYER_SPEED = 260
PLAYER_MAX_HP = 100
PLAYER_HIT_COOLDOWN = 0.5

BULLET_SPEED = 520
BULLET_SIZE = (10, 10)
BULLET_DAMAGE = 34
BULLET_LIFETIME = 1.2

ENEMY_SPEED = 180
ENEMY_SIZE = (34, 34)
ENEMY_MAX_HP = 100

# --- Cooldown de disparo continuo ---
FIRE_COOLDOWN = 0.18

# --- Clases de personaje ---
CLASSES = {
    "Juggernaut": {"hp": 140, "speed": 220, "damage": 34, "cooldown": 0.25},
    "Assault": {"hp": 80, "speed": 300, "damage": 28, "cooldown": 0.12},
    "Blaster": {"hp": 100, "speed": 260, "damage": 42, "cooldown": 0.20},
}

# --- Probabilidades y drops ---
CONSUMABLE_DROP_RATE = 0.20  # 20% de chance de soltar consumible


# --- Función para fuentes escaladas ---
def get_fuente(alto_porcentaje):
    return pygame.font.SysFont("Arial", max(int(ALTO * alto_porcentaje), 20))


# --- English aliases / compatibility ---
WIDTH, HEIGHT = ANCHO, ALTO
WHITE = BLANCO
BLACK = NEGRO
RED = ROJO
GRAY = GRIS
YELLOW = AMARILLO
GREEN = VERDE
BG_COLOR = BG
ENEMY_COL = ENEMY_COLOR

# Colores de balas por clase
BULLET_COLORS = {
    "Warrior": (255, 100, 100),  # rojo intenso
    "Rogue": (100, 255, 100),  # verde
    "Mage": (100, 150, 255),  # azul
}

# scale aliases
SCALE_X, SCALE_Y = escala_x, escala_y
# --- Tilemap Settings ---
TILESIZE = 64
