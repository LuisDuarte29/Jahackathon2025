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


def dibujar_barra(screen, x, y, valor, max_valor, ancho=100, alto=10, color=(0, 200, 0)):
    ratio = min(valor / max_valor, 1.0)
    # Fondo de la barra
    pg.draw.rect(screen, (50, 50, 50), (x, y, ancho, alto), border_radius=4)
    # Barra de progreso
    pg.draw.rect(screen, color, (x, y, int(ancho * ratio), alto), border_radius=4)
    # Borde
    pg.draw.rect(screen, (100, 100, 100), (x, y, ancho, alto), width=1, border_radius=4)


def cargar_imagen_clase(clase_nombre):
    """
    Intenta cargar la imagen de la clase desde la carpeta assets
    Si no existe, retorna None y se usará el placeholder
    
    Estructura esperada:
    assets/
            mago.png
            tanque.png
            guerrero.png
    """
    try:
        ruta = os.path.join("assets", f"{clase_nombre.lower()}.png")
        if os.path.exists(ruta):
            imagen = pg.image.load(ruta).convert_alpha()
  
            # Escalar la imagen al tamaño del placeholder (80x80)
            return pg.transform.scale(imagen, (80, 80))
    except Exception as e:
        print(f"No se pudo cargar imagen para {clase_nombre}: {e}")
    return None


def dibujar_clases(screen, mouse_pos=None, mouse_pressed=False):
    fuente_nombre = cfg.get_fuente(0.045)  # Fuente para el nombre de la clase
    fuente_stats = cfg.get_fuente(0.03)    # Fuente más pequeña para stats
    fuente_cd = cfg.get_fuente(0.028)      # Fuente para cooldown

    clases = list(cfg.CLASSES.keys())
    rects = []
    hover_index = -1

    # Distribución horizontal centrada
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

        # Borde destacado si hay hover
        if i == hover_index:
            pg.draw.rect(screen, cfg.ROJO, rect.inflate(12, 12), border_radius=14)
        
        # Fondo de la tarjeta
        pg.draw.rect(screen, (30, 30, 50), rect, border_radius=12)
        # Borde de la tarjeta
        pg.draw.rect(screen, (200, 200, 200), rect, width=2, border_radius=12)

        # ===== ÁREA DE IMAGEN (antes placeholder lila) =====
        skin_rect = pg.Rect(0, 0, 80, 80)
        skin_rect.center = (rect.centerx, rect.top + 55)
        
        # Intentar cargar imagen de la clase
        imagen_clase = cargar_imagen_clase(cls)
        
        if imagen_clase:
            # Si existe la imagen, mostrarla
            screen.blit(imagen_clase, skin_rect)
       
        else:
            # Si no existe, mostrar placeholder
            pg.draw.rect(screen, (100, 100, 250), skin_rect, border_radius=8)
          
        
        # Borde del área de imagen
        pg.draw.rect(screen, (150, 150, 150), skin_rect, width=2, border_radius=8)

        # ===== NOMBRE DE LA CLASE =====
        text = fuente_nombre.render(cls, True, cfg.BLANCO)
        screen.blit(text, text.get_rect(center=(rect.centerx, rect.top + 115)))

        # ===== ESTADÍSTICAS CON BARRAS =====
        stats = [
            ("Vida", data["hp"], 150, (0, 200, 0)),
            ("Velocidad", data["speed"], 350, (0, 150, 200)),
            ("Daño", data["damage"], 50, (200, 200, 0)),
        ]
        
        y_inicial_stats = rect.top + 150
        espacio_entre_stats = 50
        
        for j, (nombre, val, max_val, color) in enumerate(stats):
            y_pos = y_inicial_stats + j * espacio_entre_stats
            
            # Texto: "Nombre: valor"
            label = fuente_stats.render(f"{nombre}: {val}", True, cfg.BLANCO)
            label_rect = label.get_rect(centerx=rect.centerx, top=y_pos)
            screen.blit(label, label_rect)
            
            # Barra debajo del texto
            barra_y = y_pos + 20
            dibujar_barra(
                screen,
                rect.centerx - 50,  # Centrada, 100px de ancho
                barra_y,
                val,
                max_val,
                ancho=100,
                alto=10,
                color=color
            )

        # ===== COOLDOWN EN LA PARTE INFERIOR =====
        cd_label = fuente_cd.render(f"Cooldown: {data['cooldown']}s", True, (180, 180, 180))
        screen.blit(
            cd_label, cd_label.get_rect(center=(rect.centerx, rect.bottom - 20))
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