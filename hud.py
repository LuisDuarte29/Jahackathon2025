# hud.py
import pygame as pg
from settings import WIDTH, HEIGHT, WHITE


def create_heart_surface(color):
    """Crea una superficie de corazón de 24x24 píxeles."""
    surf = pg.Surface((24, 24), pg.SRCALPHA)
    points = [
        (12, 20),
        (4, 12),
        (4, 8),
        (8, 4),
        (12, 8),
        (16, 4),
        (20, 8),
        (20, 12),
        (12, 20),
    ]
    pg.draw.polygon(surf, color, points)
    # Borde brillante
    pg.draw.polygon(
        surf,
        (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255)),
        points,
        2,
    )
    return surf


def draw_hearts(screen, player, y=40):
    """Dibuja los corazones de vida del jugador."""
    max_hp = getattr(player, "max_hp", 100)
    current_hp = getattr(player, "hp", 100)

    # Cantidad de corazones (20 HP por corazón)
    hearts_to_draw = (max_hp + 19) // 20

    heart_w, heart_h = 24, 24
    spacing = 6
    total_w = hearts_to_draw * heart_w + (hearts_to_draw - 1) * spacing
    start_x = WIDTH // 2 - total_w // 2

    heart_full = create_heart_surface((255, 50, 50))
    heart_empty = create_heart_surface((80, 80, 80))

    for i in range(hearts_to_draw):
        x = start_x + i * (heart_w + spacing)
        # Fondo (corazón vacío)
        screen.blit(heart_empty, (x, y))

        # HP en este corazón
        heart_health = min(20, max(0, current_hp - (i * 20)))
        if heart_health > 0:
            mask = pg.Surface((heart_w, heart_h), pg.SRCALPHA)
            height = int((heart_health / 20.0) * heart_h)
            mask.fill((255, 255, 255, 255), (0, heart_h - height, heart_w, height))
            piece = heart_full.copy()
            piece.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
            screen.blit(piece, (x, y))


class HUD:
    """HUD unificado: muestra vida, score, tiempo y monedas."""

    def __init__(self, player, font=None):
        self.player = player
        self.score = 0
        self.time_alive = 0.0
        self.floating_texts = []

        # Fuente
        self.font = font if font else pg.font.SysFont("consolas,roboto,arial", 18)

        # Contador de monedas
        self.coins = 0
        self.icon_coin = pg.Surface((24, 24))
        self.icon_coin.fill((255, 215, 0))  # dorado

    def update(self, dt):
        """Actualiza el HUD y textos flotantes."""
        self.time_alive += dt
        for ft in self.floating_texts[:]:
            ft["lifetime"] -= dt
            ft["y"] -= 30 * dt
            if ft["lifetime"] <= 0:
                self.floating_texts.remove(ft)

    def add_score(self, points):
        """Añade puntos al score."""
        self.score += points

    def add_coin(self, amount=1):
        """Añade monedas al HUD."""
        self.coins += amount

    def add_floating_text(self, text, pos, color=(255, 255, 255)):
        """Texto flotante (ej: +100, +1 moneda)."""
        self.floating_texts.append(
            {"text": text, "x": pos[0], "y": pos[1], "color": color, "lifetime": 1.5}
        )

    def draw(self, screen):
        """Dibuja el HUD completo en pantalla."""
        # Tiempo y score (arriba izquierda)
        txt = self.font.render(
            f"Tiempo: {int(self.time_alive)}s   Score: {self.score}", True, WHITE
        )
        screen.blit(txt, (12, 10))

        # Corazones (arriba centro)
        draw_hearts(screen, self.player, y=40)

        # Monedas (arriba derecha)
        x = WIDTH - 100
        y = 10
        screen.blit(self.icon_coin, (x, y))
        txt_coin = self.font.render(str(self.coins), True, WHITE)
        screen.blit(txt_coin, (x + 28, y + 2))

        # Textos flotantes
        for ft in self.floating_texts:
            alpha = int(255 * (ft["lifetime"] / 1.5))
            surf = self.font.render(ft["text"], True, ft["color"])
            surf.set_alpha(alpha)
            screen.blit(surf, (ft["x"] - surf.get_width() // 2, ft["y"]))
