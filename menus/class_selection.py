# menus/class_selection.py
import pygame as pg
import math
import random
import settings as cfg

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
    fuente = cfg.get_fuente(0.07)  # tamaño más proporcionado
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


def dibujar_barra(
    screen, x, y, valor, max_valor, ancho=120, alto=12, color=(0, 200, 0)
):
    ratio = min(valor / max_valor, 1.0)
    pg.draw.rect(screen, (50, 50, 50), (x, y, ancho, alto), border_radius=4)
    pg.draw.rect(screen, color, (x, y, int(ancho * ratio), alto), border_radius=4)


def dibujar_clases(screen, mouse_pos=None, mouse_pressed=False):
    fuente = cfg.get_fuente(0.05)
    small_font = cfg.get_fuente(0.035)

    clases = list(cfg.CLASSES.keys())
    rects = []
    hover_index = -1

    # Distribución horizontal centrada
    espacio_x = 280  # distancia entre tarjetas
    ancho_total = (len(clases) - 1) * espacio_x
    inicio_x = (cfg.ANCHO // 2) - (ancho_total // 2)
    y_base = int(cfg.ALTO * 0.35)

    for i, cls in enumerate(clases):
        cx = inicio_x + i * espacio_x
        rect = pg.Rect(cx - 100, y_base - 80, 200, 320)
        rects.append(rect)
        if mouse_pos and rect.collidepoint(mouse_pos):
            hover_index = i

    for i, cls in enumerate(clases):
        rect = rects[i]
        data = cfg.CLASSES[cls]

        # Borde destacado
        if i == hover_index:
            pg.draw.rect(screen, cfg.ROJO, rect.inflate(12, 12), border_radius=14)
        pg.draw.rect(screen, (200, 200, 200), rect, width=2, border_radius=12)

        # Placeholder skin
        skin_rect = pg.Rect(0, 0, 90, 90)
        skin_rect.center = (rect.centerx, rect.top + 70)
        pg.draw.rect(screen, (100, 100, 250), skin_rect, border_radius=8)

        # Nombre
        text = fuente.render(cls, True, cfg.BLANCO)
        screen.blit(text, text.get_rect(center=(rect.centerx, rect.top + 160)))

        # Stats numéricos + barras
        stats = [
            ("Vida", data["hp"], 150, (0, 200, 0)),
            ("Vel", data["speed"], 350, (0, 150, 200)),
            ("Daño", data["damage"], 50, (200, 200, 0)),
        ]
        for j, (nombre, val, max_val, color) in enumerate(stats):
            label = small_font.render(f"{nombre}: {val}", True, cfg.BLANCO)
            screen.blit(
                label, label.get_rect(center=(rect.centerx, rect.top + 200 + j * 55))
            )
            dibujar_barra(
                screen,
                rect.centerx - 60,
                rect.top + 220 + j * 55,
                val,
                max_val,
                color=color,
            )

        # Cooldown
        cd_label = small_font.render(f"Cooldown: {data['cooldown']}s", True, cfg.BLANCO)
        screen.blit(
            cd_label, cd_label.get_rect(center=(rect.centerx, rect.bottom - 35))
        )

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
