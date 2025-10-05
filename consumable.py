import pygame as pg
import settings as cfg

# Solo monedas
CONSUMABLE_TYPES = ["coin"]


class Consumable(pg.sprite.Sprite):
    def __init__(self, pos, item_type=None):
        super().__init__()
        self.item_type = "coin"  # ya no hay más opciones

        # --- imagen simple para testeo (círculo dorado) ---
        size = 20
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(self.image, (255, 215, 0), (size // 2, size // 2), size // 2)

        self.rect = self.image.get_rect(center=pos)

    def apply(self, hud):
        """
        Efecto al recoger el consumible.
        Ahora interactúa con el HUD directamente en lugar del player.
        """
        hud.add_coin(1)  # Llama al método add_coin del HUD
        hud.add_floating_text("+1 Moneda", self.rect.center, (255, 215, 0))
        print(f"Moneda recogida! Total: {hud.coins}")  # Debug
        self.kill()