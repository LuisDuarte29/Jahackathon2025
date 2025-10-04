# hud.py
import pygame as pg
from settings import WIDTH, HEIGHT, WHITE


def create_heart_surface(color):
    """Crea una superficie de corazón de 24x24 píxeles."""
    surf = pg.Surface((24, 24), pg.SRCALPHA)
    points = [(12, 20), (4, 12), (4, 8), (8, 4), (12, 8),
              (16, 4), (20, 8), (20, 12), (12, 20)]
    pg.draw.polygon(surf, color, points)
    # Borde brillante
    pg.draw.polygon(surf, (min(color[0] + 30, 255),
                           min(color[1] + 30, 255),
                           min(color[2] + 30, 255)), points, 2)
    return surf


def draw_hearts(screen, player, y=40):
    """Dibuja los corazones de vida del jugador."""
    # Obtener HP máximo y actual
    max_hp = getattr(player, "max_hp", 100)
    current_hp = getattr(player, "hp", 100)
    
    # Calcular cantidad de corazones (20 HP por corazón)
    hearts_to_draw = (max_hp + 19) // 20
    
    # Configuración de corazones
    heart_w, heart_h = 24, 24
    spacing = 6
    total_w = hearts_to_draw * heart_w + (hearts_to_draw - 1) * spacing
    start_x = WIDTH // 2 - total_w // 2
    
    # Crear superficies de corazones
    heart_full = create_heart_surface((255, 50, 50))
    heart_empty = create_heart_surface((80, 80, 80))
    
    # Dibujar cada corazón
    for i in range(hearts_to_draw):
        x = start_x + i * (heart_w + spacing)
        # Corazón vacío de fondo
        screen.blit(heart_empty, (x, y))
        
        # Calcular HP de este corazón específico
        heart_health = min(20, max(0, current_hp - (i * 20)))
        
        if heart_health > 0:
            # Crear máscara para mostrar corazón parcialmente lleno
            mask = pg.Surface((heart_w, heart_h), pg.SRCALPHA)
            height = int((heart_health / 20.0) * heart_h)
            mask.fill((255, 255, 255, 255), (0, heart_h - height, heart_w, height))
            
            # Aplicar máscara al corazón lleno
            piece = heart_full.copy()
            piece.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MULT)
            screen.blit(piece, (x, y))


def draw_ui(screen, player, time_alive, score, font=None):
    """Dibuja toda la interfaz de usuario (HUD)."""
    if font is None:
        font = pg.font.SysFont("consolas,roboto,arial", 18)
    
    # Texto de tiempo y score (esquina superior izquierda)
    txt = font.render(f"Tiempo: {int(time_alive)}s   Score: {score}", True, WHITE)
    screen.blit(txt, (12, 10))
    
    # Corazones (centrados en la parte superior)
    draw_hearts(screen, player, y=40)


class HUD:
    """Clase para manejar el HUD del juego."""
    
    def __init__(self, font=None):
        if font is None:
            self.font = pg.font.SysFont("consolas,roboto,arial", 18)
        else:
            self.font = font
        self.score = 0
        self.time_alive = 0.0
        self.floating_texts = []
    
    def update(self, dt):
        """Actualiza elementos animados del HUD."""
        self.time_alive += dt
        # Actualizar textos flotantes
        for ft in self.floating_texts[:]:
            ft['lifetime'] -= dt
            ft['y'] -= 30 * dt  # flotar hacia arriba
            if ft['lifetime'] <= 0:
                self.floating_texts.remove(ft)
    
    def add_score(self, points):
        """Añade puntos al score."""
        self.score += points
    
    def add_floating_text(self, text, pos, color=(255, 255, 255)):
        """Añade texto flotante (ej: +100, -10 HP)."""
        self.floating_texts.append({
            'text': text,
            'x': pos[0],
            'y': pos[1],
            'color': color,
            'lifetime': 1.5
        })
    
    def draw(self, screen, player):
        """Dibuja el HUD completo."""
        draw_ui(screen, player, self.time_alive, self.score, self.font)
        
        # Dibujar textos flotantes
        for ft in self.floating_texts:
            alpha = int(255 * (ft['lifetime'] / 1.5))
            surf = self.font.render(ft['text'], True, ft['color'])
            surf.set_alpha(alpha)
            screen.blit(surf, (ft['x'] - surf.get_width()//2, ft['y']))