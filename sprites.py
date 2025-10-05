# sprites.py
from pathlib import Path
import pygame as pg

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

def load_image(name_or_path: str) -> pg.Surface:
    """
    Carga una imagen desde project/assets, aceptando:
    - "player_sheet.png"
    - "assets/player_sheet.png"
    - ruta absoluta (se usa tal cual)
    """
    p = Path(name_or_path)

    if not p.is_absolute():
        parts = p.parts
        # Evitar duplicar "assets" si ya viene en el path
        if len(parts) > 0 and parts[0].lower() == "assets":
            p = ASSETS_DIR.joinpath(*parts[1:])
        else:
            p = ASSETS_DIR / p

    # DEBUG opcional: ver la ruta final
    # print("Loading image from:", p)

    if not p.exists():
        raise FileNotFoundError(
            f"No se encontró la imagen:\n  {p}\n"
            f"Sugerencia: debería existir junto a: {ASSETS_DIR}"
        )
    return pg.image.load(str(p)).convert_alpha()

def slice_spritesheet(sheet: pg.Surface, frame_w: int, frame_h: int, cols: int, rows: int):
    frames = []
    sheet_w, sheet_h = sheet.get_size()

    print(f"[DEBUG] Cortando spritesheet de {sheet_w}x{sheet_h} en {cols}x{rows} frames ({frame_w}x{frame_h} cada uno)")

    for r in range(rows):
        for c in range(cols):
            x = c * frame_w
            y = r * frame_h

            # Evitar que el rectángulo se salga de la superficie
            if x + frame_w > sheet_w or y + frame_h > sheet_h:
                print(f"[WARN] Frame fuera de rango: x={x}, y={y}, w={frame_w}, h={frame_h}")
                continue

            rect = pg.Rect(x, y, frame_w, frame_h)
            frames.append(sheet.subsurface(rect).copy())

    print(f"[DEBUG] Total frames generados: {len(frames)}")
    return frames


class Animation:
    def __init__(self, frames, sec_per_frame=0.12, loop=True, scale=None):
        self.frames = frames
        self.spf = sec_per_frame
        self.loop = loop
        self.time = 0.0
        self.index = 0
        if scale is not None:
            self.frames = [pg.transform.smoothscale(f, scale) for f in self.frames]

    def update(self, dt):
        if len(self.frames) <= 1:
            return
        self.time += dt
        while self.time >= self.spf:
            self.time -= self.spf
            self.index += 1
            if self.loop:
                self.index %= len(self.frames)
            else:
                self.index = min(self.index, len(self.frames) - 1)

    def frame(self) -> pg.Surface:
        return self.frames[self.index] if self.frames else None
