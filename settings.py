# settings.py
WIDTH, HEIGHT = 960, 540
FPS = 60

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BG = (18, 18, 24)
GREEN = (60, 200, 80)
RED = (220, 60, 60)
GRAY = (120, 120, 120)
YELLOW = (240, 220, 0)

# Jugabilidad
PLAYER_SPEED = 260
PLAYER_MAX_HP = 100
PLAYER_HIT_COOLDOWN = 0.5

BULLET_SPEED = 520
BULLET_SIZE = (10, 10)
BULLET_DAMAGE = 34
BULLET_LIFETIME = 1.2

ENEMY_SPEED = 180
ENEMY_SIZE = (34, 34)
ENEMY_COLOR = (200, 90, 90)
ENEMY_MAX_HP = 100

# --- Nuevo: cooldown de disparo continuo (en segundos) ---
FIRE_COOLDOWN = 0.18
