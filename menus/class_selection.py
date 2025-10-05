# menus/class_selection.py
import pygame as pg
import math
import random
import settings as cfg
import os

# --- Fondo animado ---
estrellas = [
    {
        "pos": pg.Vector2(random.randint(0, cfg.ANCHO), random.randint(0, cfg.ALTO)),
        "vel": random.uniform(20, 80),
        "color": (random.randint(150, 255),) * 3,
        "radio": random.choice([2, 3]),
    }
    for _ in range(120)
]


def actualizar_fondo(dt):
    for estrella in estrellas:
        estrella["pos"].y += estrella["vel"] * dt
        if estrella["pos"].y > cfg.ALTO:
            estrella["pos"].y = -10
            estrella["pos"].x = random.randint(0, cfg.ANCHO)


def dibujar_fondo(screen):
    screen.fill(cfg.BG_COLOR)
    for estrella in estrellas:
        pg.draw.circle(
            screen,
            estrella["color"],
            (int(estrella["pos"].x), int(estrella["pos"].y)),
            estrella["radio"],
        )


def dibujar_titulo(screen, tiempo):
    fuente = cfg.get_fuente(0.07)
    texto = "Selecciona tu clase"
    alpha = int((math.sin(tiempo * 2) + 1) * 127)
    offset_y = int(math.sin(tiempo) * 10)

    render = fuente.render(texto, True, cfg.ROJO)
    render.set_alpha(alpha)
    rect = render.get_rect(center=(cfg.ANCHO // 2, int(cfg.ALTO * 0.15) + offset_y))

    sombra = fuente.render(texto, True, (30, 0, 0))
    sombra_rect = rect.copy()
    sombra_rect.move_ip(4, 4)
    screen.blit(sombra, sombra_rect)
    screen.blit(render, rect)


def dibujar_barra(screen, x, y, valor, max_valor, ancho=80, alto=8, color=(0, 200, 0)):
    ratio = min(valor / max_valor, 1.0)
    pg.draw.rect(screen, (50, 50, 50), (x, y, ancho, alto), border_radius=4)
    pg.draw.rect(screen, color, (x, y, int(ancho * ratio), alto), border_radius=4)
    pg.draw.rect(screen, (100, 100, 100), (x, y, ancho, alto), width=1, border_radius=4)


def cargar_imagen_clase(clase_nombre):
    mapping = {
        "Juggernaut": ("juggernaut_sur", 4),
        "Blaster": ("blaster_sur", 4),
        "Assault": ("assault_sur", 3),
    }
    archivo_info = mapping.get(clase_nombre, (clase_nombre.lower(), 1))
    nombre_archivo, frames_count = archivo_info

    try:
        ruta = os.path.join("assets", f"{nombre_archivo}.png")
        if os.path.exists(ruta):
            sheet = pg.image.load(ruta).convert_alpha()
            frame_w = sheet.get_width() // frames_count
            frame_h = sheet.get_height()
            frame = sheet.subsurface((0, 0, frame_w, frame_h))

            max_dim = 80
            scale_factor = min(max_dim / frame_w, max_dim / frame_h)
            new_w = int(frame_w * scale_factor)
            new_h = int(frame_h * scale_factor)
            frame_scaled = pg.transform.smoothscale(frame, (new_w, new_h))
            return frame_scaled
    except Exception as e:
        print(f"No se pudo cargar imagen para {clase_nombre}: {e}")
    return None


def dibujar_clases(screen, mouse_pos=None, mouse_pressed=False):
    fuente_nombre = cfg.get_fuente(0.038)
    fuente_stats = cfg.get_fuente(0.024)
    fuente_cd = cfg.get_fuente(0.022)

    clases = list(cfg.CLASSES.keys())
    rects = []
    hover_index = -1

    espacio_x = 280
    ancho_total = (len(clases) - 1) * espacio_x
    inicio_x = (cfg.ANCHO // 2) - (ancho_total // 2)
    y_base = int(cfg.ALTO * 0.38)

    for i, cls in enumerate(clases):
        cx = inicio_x + i * espacio_x
        rect = pg.Rect(cx - 100, y_base - 80, 200, 340)
        rects.append(rect)
        if mouse_pos and rect.collidepoint(mouse_pos):
            hover_index = i

    for i, cls in enumerate(clases):
        rect = rects[i]
        data = cfg.CLASSES[cls]

        if i == hover_index:
            pg.draw.rect(screen, cfg.ROJO, rect.inflate(12, 12), border_radius=14)

        pg.draw.rect(screen, (30, 30, 50), rect, border_radius=12)
        pg.draw.rect(screen, (200, 200, 200), rect, width=2, border_radius=12)

        # ===== ÁREA DE IMAGEN =====
        imagen_clase = cargar_imagen_clase(cls)
        if imagen_clase:
            img_rect = imagen_clase.get_rect(center=(rect.centerx, rect.top + 60))
            screen.blit(imagen_clase, img_rect)
        else:
            placeholder_rect = pg.Rect(0, 0, 80, 80)
            placeholder_rect.center = (rect.centerx, rect.top + 60)
            pg.draw.rect(screen, (100, 100, 250), placeholder_rect, border_radius=8)
            pg.draw.rect(screen, (150, 150, 150), placeholder_rect, width=2, border_radius=8)

        # ===== NOMBRE DE LA CLASE =====
        text = fuente_nombre.render(cls, True, cfg.BLANCO)
        text_rect = text.get_rect(center=(rect.centerx, rect.top + 110))
        screen.blit(text, text_rect)

        # ===== ESTADÍSTICAS =====
        stats = [
            ("Vida", data["hp"], 150, (0, 200, 0)),
            ("Velocidad", data["speed"], 350, (0, 150, 200)),
            ("Daño", data["damage"], 50, (200, 200, 0)),
        ]
        y_inicial_stats = rect.top + 130
        espacio_entre_stats = 50  # suficiente espacio vertical

        for j, (nombre, val, max_val, color) in enumerate(stats):
            y_pos = y_inicial_stats + j * espacio_entre_stats
            # Texto encima de la barra
            label = fuente_stats.render(f"{nombre}: {val}", True, cfg.BLANCO)
            label_rect = label.get_rect(centerx=rect.centerx, top=y_pos)
            screen.blit(label, label_rect)
            # Barra debajo del texto
            dibujar_barra(screen, rect.centerx - 40, y_pos + 16, val, max_val, ancho=80, alto=8, color=color)

        # ===== COOLDOWN =====
        cd_label = fuente_cd.render(f"Cooldown: {data['cooldown']}s", True, (180, 180, 180))
        cd_rect = cd_label.get_rect(center=(rect.centerx, rect.bottom - 18))
        screen.blit(cd_label, cd_rect)

    return rects, hover_index


def class_selection_screen(screen, clock):
    tiempo = 0
    while True:
        dt = clock.tick(cfg.FPS) / 1000.0
        tiempo += dt
        mouse_pos = pg.mouse.get_pos()

        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                raise SystemExit
            if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                rects, _ = dibujar_clases(screen, mouse_pos)
                for i, rect in enumerate(rects):
                    if rect.collidepoint(event.pos):
                        return list(cfg.CLASSES.keys())[i]

        actualizar_fondo(dt)
        dibujar_fondo(screen)
        dibujar_titulo(screen, tiempo)
        dibujar_clases(screen, mouse_pos)

        pg.display.flip()
