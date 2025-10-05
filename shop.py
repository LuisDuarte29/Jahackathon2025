# shop.py
import pygame as pg
import settings as cfg

class Shop:
    def __init__(self, player, hud):
        self.player = player
        self.hud = hud
        self.items = [
            {
                "name": "Más Daño",
                "description": "Aumenta el daño de las balas +5",
                "price": 3,
                "effect": "damage",
                "value": 5
            },
            {
                "name": "Curación", 
                "description": "Recupera 30 puntos de vida",
                "price": 2,
                "effect": "heal",
                "value": 30
            },
            {
                "name": "Más Velocidad",
                "description": "Aumenta la velocidad +40", 
                "price": 4,
                "effect": "speed", 
                "value": 40
            }
        ]
        self.selected_index = 0
        self.font = pg.font.SysFont("consolas,roboto,arial", 24)
        self.title_font = pg.font.SysFont("consolas,roboto,arial", 36, bold=True)
        self.small_font = pg.font.SysFont("consolas,roboto,arial", 18)
        self.message = ""
        self.message_timer = 0

    def draw(self, surface):
        """Dibuja la interfaz de la tienda en la superficie lógica"""
        # Fondo semi-transparente
        overlay = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))
        
        # Título
        title = self.title_font.render("TIENDA", True, cfg.YELLOW)
        surface.blit(title, (cfg.LOGICAL_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Monedas disponibles
        coins_text = self.font.render(f"Monedas: {self.hud.coins}", True, cfg.YELLOW)
        surface.blit(coins_text, (cfg.LOGICAL_WIDTH // 2 - coins_text.get_width() // 2, 100))
        
        # Items de la tienda
        for i, item in enumerate(self.items):
            y_pos = 180 + i * 120
            
            # Color según selección
            color = cfg.RED if i == self.selected_index else cfg.WHITE
            
            # Nombre y precio
            name_text = self.font.render(f"{item['name']} - {item['price']} monedas", True, color)
            surface.blit(name_text, (cfg.LOGICAL_WIDTH // 2 - name_text.get_width() // 2, y_pos))
            
            # Descripción
            desc_text = self.small_font.render(item['description'], True, cfg.WHITE)
            surface.blit(desc_text, (cfg.LOGICAL_WIDTH // 2 - desc_text.get_width() // 2, y_pos + 35))
            
            # Indicador de selección
            if i == self.selected_index:
                selector = self.font.render(">", True, cfg.RED)
                surface.blit(selector, (cfg.LOGICAL_WIDTH // 2 - name_text.get_width() // 2 - 30, y_pos))
        
        # Mensaje de compra
        if self.message and self.message_timer > 0:
            message_color = cfg.GREEN if "Comprado" in self.message else cfg.RED
            message_text = self.font.render(self.message, True, message_color)
            surface.blit(message_text, (cfg.LOGICAL_WIDTH // 2 - message_text.get_width() // 2, cfg.LOGICAL_HEIGHT - 100))
        
        # Instrucciones - ACTUALIZADO con W/S
        instructions = self.small_font.render("W/S: Navegar | ESPACIO: Comprar | ESC: Salir", True, cfg.GRAY)
        surface.blit(instructions, (cfg.LOGICAL_WIDTH // 2 - instructions.get_width() // 2, cfg.LOGICAL_HEIGHT - 50))

    def update(self, dt):
        """Actualiza el temporizador del mensaje"""
        if self.message_timer > 0:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.message = ""

    def handle_input(self):
        """Maneja la entrada del usuario en la tienda"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            
            if event.type == pg.KEYDOWN:
                # CAMBIADO: Usar W/S en lugar de flechas
                if event.key == pg.K_w:  # W para subir
                    self.selected_index = (self.selected_index - 1) % len(self.items)
                    self.message = ""
                elif event.key == pg.K_s:  # S para bajar
                    self.selected_index = (self.selected_index + 1) % len(self.items)
                    self.message = ""
                elif event.key == pg.K_SPACE:
                    self.buy_item()
                elif event.key == pg.K_ESCAPE:
                    return "exit"
        return "continue"

    def buy_item(self):
        """Compra el item seleccionado"""
        item = self.items[self.selected_index]
        
        print(f"Intentando comprar: {item['name']} por {item['price']} monedas")
        print(f"Monedas disponibles antes: {self.hud.coins}")
        
        if self.hud.coins >= item["price"]:
            # Aplicar efecto según el tipo de item
            if item["effect"] == "damage":
                self.player.damage += item["value"]
                self.message = f"¡Comprado! +{item['value']} de daño"
            elif item["effect"] == "heal":
                self.player.hp = min(self.player.max_hp, self.player.hp + item["value"])
                self.message = f"¡Comprado! +{item['value']} de vida"
            elif item["effect"] == "speed":
                self.player.speed += item["value"]
                self.message = f"¡Comprado! +{item['value']} de velocidad"
            
            # Restar monedas
            self.hud.coins -= item["price"]
            
            self.message_timer = 3.0
            print(f"Compra exitosa! Monedas después: {self.hud.coins}")
            
        else:
            self.message = "Monedas insuficientes"
            self.message_timer = 2.0
            print("Monedas insuficientes!")

def shop_screen(screen, clock, player, hud):
    """Muestra la pantalla de tienda"""
    shop = Shop(player, hud)
    
    # Crear superficie lógica para la tienda
    game_surface = pg.Surface((cfg.LOGICAL_WIDTH, cfg.LOGICAL_HEIGHT))
    
    running = True
    while running:
        dt = clock.tick(cfg.FPS) / 1000.0
        
        # Actualizar tienda
        shop.update(dt)
        
        # Manejar entrada
        result = shop.handle_input()
        if result == "exit":
            running = False
        
        # Dibujar en la superficie lógica
        game_surface.fill(cfg.BG_COLOR)
        shop.draw(game_surface)
        
        # Escalar a la pantalla real
        scaled_surface = pg.transform.smoothscale(game_surface, screen.get_size())
        screen.blit(scaled_surface, (0, 0))
        pg.display.flip()