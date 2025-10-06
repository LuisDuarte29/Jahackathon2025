# inventory.py
import pygame as pg
import settings as cfg


class InventoryHUD:
    """Panel de inventario/minimap.
    Ahora muestra SIEMPRE las monedas actuales leyendo del HUD principal,
    por lo que se actualiza automáticamente al recoger o comprar.
    """

    def __init__(self, player, hud):
        self.player = player
        self.hud = hud  # referencia al HUD principal (fuente de la verdad de coins)
        # Si quieres contar otros ítems distintos a monedas, puedes mantener este dict:
        self.items = {}
        self.font = pg.font.SysFont("Arial", 24)

    def add(self, item_type, amount=1):
        """Aumenta la cantidad de un tipo de consumible (distinto de monedas)."""
        if item_type == "coin":
            # Las monedas se cuentan en HUD; no duplicamos aquí.
            return
        self.items[item_type] = self.items.get(item_type, 0) + amount

    def set_hud(self, hud):
        """Permite re-vincular el HUD si fuera necesario."""
        self.hud = hud

    def draw(self, screen):
        """Dibuja la HUD de inventario en pantalla."""
        x, y = 40, 40

        # --- Monedas (miran al HUD principal) ---
        coins = getattr(self.hud, "coins", 0)
        text = self.font.render(f"Coins: {coins}", True, cfg.WHITE)
        screen.blit(text, (x, y))
        y += 30

        # --- Otros ítems (si los usas) ---
        for item, count in self.items.items():
            text = self.font.render(f"{item.capitalize()}: {count}", True, cfg.WHITE)
            screen.blit(text, (x, y))
            y += 30
