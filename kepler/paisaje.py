"""
kepler/paisaje.py
Cielo y terreno de Kepler-7 con estilo de 16 bits: degradados con trama (dithering),
esferas con luz y sombra, cordilleras con el borde iluminado y dunas.

El CIELO es el mismo en todas las pantallas de exterior (choque, cueva, mercado,
boletería y plataforma), porque quedan una al lado de la otra: así no "salta" al cambiar
de pantalla. Cada escenario pinta encima su propio terreno.
"""

import math
import random

import pygame

from kepler.arte import _tono

ANCHO = 320
ALTO = 150
HORIZONTE = 100      # hasta dónde llega el degradado del cielo (las pantallas lo tapan con su terreno)
BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def _umbral(x, y):
    return (BAYER[y % 4][x % 4] + 0.5) / 16


def _mezclar(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def degradado_tramado(sup, rect, colores):
    """Degradado vertical entre varios colores; las transiciones se hacen con trama de puntitos."""
    x0, y0, w, h = rect
    n = len(colores)
    for y in range(y0, y0 + h):
        p = (y - y0) / max(1, h - 1) * (n - 1)
        i = min(int(p), n - 2)
        frac = p - i
        for x in range(x0, x0 + w):
            sup.set_at((x, y), colores[i + 1] if frac > _umbral(x, y) else colores[i])


def esfera(sup, cx, cy, r, rampa, luz_dir=(-0.55, -0.5), bandas=0.0, fase=0.0):
    """Una esfera con luz desde 'luz_dir'. 'rampa' va de lo más oscuro a lo más claro."""
    lx, ly = luz_dir
    lz = math.sqrt(max(0.01, 1 - lx * lx - ly * ly))
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            nx, ny = (x - cx) / r, (y - cy) / r
            d2 = nx * nx + ny * ny
            if d2 > 1:
                continue
            nz = math.sqrt(1 - d2)
            luz = max(0.0, nx * lx + ny * ly + nz * lz)
            luz += bandas * math.sin(ny * 9 + fase + nx * 1.4)
            luz = max(0.0, min(0.999, luz))
            p = luz * (len(rampa) - 1)
            i = int(p)
            sup.set_at((x, y), rampa[i + 1] if (p - i) > _umbral(x, y) and i + 1 < len(rampa) else rampa[i])


def cielo(sup):
    """El cielo de Kepler-7: degradado de noche a atardecer, estrellas, un planeta con anillo y lunas."""
    degradado_tramado(sup, (0, 0, ANCHO, HORIZONTE),
                      [(12, 8, 34), (22, 12, 52), (40, 18, 70), (68, 26, 84), (106, 38, 90),
                       (156, 58, 90), (206, 92, 84), (240, 140, 96), (250, 176, 112)])
    azar = random.Random(3)
    for _ in range(90):
        x, y = azar.randrange(ANCHO), azar.randrange(0, 46)
        c = azar.choice(((255, 255, 255), (255, 236, 190), (190, 210, 255), (150, 140, 200)))
        sup.set_at((x, y), _mezclar((30, 16, 60), c, azar.uniform(0.4, 1.0) * (1 - y / 70)))
    for x, y in ((40, 14), (118, 30), (176, 9), (300, 8), (22, 34)):        # estrellas brillantes, en cruz
        for dx, dy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            sup.set_at((x + dx, y + dy), (255, 250, 230) if dx == dy == 0 else (170, 150, 200))

    cx, cy, r = 236, 40, 20                                                    # planeta gigante con anillo
    rampa = [(50, 24, 70), (96, 44, 92), (154, 76, 112), (214, 128, 128), (250, 192, 156), (255, 232, 200)]
    for y in range(cy - 7, cy):                                                # anillo, parte de atrás
        for x in range(cx - 38, cx + 39):
            e = ((x - cx) / 36) ** 2 + ((y - cy) / 8) ** 2
            if 0.55 < e < 1.0 and (x - cx) ** 2 + (y - cy) ** 2 > r * r:
                sup.set_at((x, y), _mezclar((120, 70, 120), (232, 190, 170), 0.5 + 0.4 * _umbral(x, y)))
    esfera(sup, cx, cy, r, rampa, bandas=0.10, fase=1.0)
    for y in range(cy, cy + 8):                                                # anillo, parte de adelante
        for x in range(cx - 38, cx + 39):
            e = ((x - cx) / 36) ** 2 + ((y - cy) / 8) ** 2
            if 0.55 < e < 1.0:
                base = (240, 200, 176) if x < cx + 10 else (150, 90, 120)
                sup.set_at((x, y), _mezclar(base, _tono(base, 0.2), _umbral(x, y)))
    esfera(sup, 290, 22, 8, [(120, 100, 120), (170, 150, 160), (214, 196, 196), (244, 232, 220), (255, 250, 240)])
    for x, y in ((287, 20), (292, 25), (289, 24)):                             # cráteres de la luna
        sup.set_at((x, y), (170, 150, 160))
    esfera(sup, 40, 44, 4, [(46, 60, 120), (80, 110, 190), (140, 170, 230), (210, 226, 250)])


def cordillera(sup, puntos, base_y, color_alto, color_bajo):
    """Una cadena de montañas suaves con la ladera de la izquierda iluminada y la derecha en sombra."""
    tops = []
    for x in range(ANCHO):
        j = 0
        while j < len(puntos) - 2 and puntos[j + 1][0] <= x:
            j += 1
        (xa, ya), (xb, yb) = puntos[j], puntos[j + 1]
        t = (x - xa) / max(1, xb - xa)
        t = t * t * (3 - 2 * t)                      # suaviza las cumbres
        tops.append(round(ya + (yb - ya) * t))
    paleta = [color_alto, _mezclar(color_alto, color_bajo, 0.4), _mezclar(color_alto, color_bajo, 0.75), color_bajo]
    for x in range(ANCHO):
        for y in range(tops[x], base_y):
            t = (y - tops[x]) / max(1, base_y - tops[x] - 1) * 3
            i = min(int(t), 2)
            sup.set_at((x, y), paleta[i + 1] if (t - i) > _umbral(x, y) else paleta[i])
        prev = tops[x - 1] if x > 0 else tops[x]
        nxt = tops[x + 1] if x < ANCHO - 1 else tops[x]
        if tops[x] < nxt:             # ladera que mira a la luz (la izquierda)
            sup.set_at((x, tops[x]), _tono(color_alto, 0.35))
            if tops[x] + 1 < base_y:
                sup.set_at((x, tops[x] + 1), _tono(color_alto, 0.15))
        elif tops[x] > prev:          # ladera en sombra
            sup.set_at((x, tops[x]), _tono(color_alto, -0.25))
        else:
            sup.set_at((x, tops[x]), _tono(color_alto, 0.2))
    return tops


def suelo_marte(sup):
    """El suelo rojizo del sitio del choque: degradado, dunas con borde de luz y puntitos de arena."""
    degradado_tramado(sup, (0, 84, ANCHO, ALTO - 84),
                      [(178, 80, 70), (192, 90, 66), (204, 100, 66), (212, 108, 68),
                       (206, 102, 64), (190, 90, 58), (170, 78, 54)])
    azar = random.Random(5)
    for base, amp, fase, anch in ((98, 3, 0.5, 70), (116, 4, 2.0, 90), (134, 3, 4.1, 60)):   # dunas
        for x in range(ANCHO):
            y = int(base + amp * math.sin(x / anch * 6.28 + fase) + 1.5 * math.sin(x / 17 + fase))
            sup.set_at((x, y), (236, 150, 98))
            sup.set_at((x, y + 1), (222, 130, 86))
            for k in range(2, 6):
                if k < 5 - 3 * _umbral(x, y + k) and (x + y + k) % 2 == 0:
                    sup.set_at((x, y + k), (150, 62, 56))
    for _ in range(420):
        x, y = azar.randrange(ANCHO), azar.randrange(86, ALTO)
        sup.set_at((x, y), azar.choice(((150, 62, 52), (160, 70, 54), (232, 140, 92), (226, 128, 84))))


def suelo_llano(sup, y0, colores, semilla, dunas=(), puntitos=300):
    """Un suelo con degradado tramado desde 'y0' hasta abajo, dunas suaves opcionales y puntitos de arena."""
    degradado_tramado(sup, (0, y0, ANCHO, ALTO - y0), colores)
    azar = random.Random(semilla)
    for base, amp, fase, anch in dunas:
        for x in range(ANCHO):
            y = int(base + amp * math.sin(x / anch * 6.28 + fase) + 1.2 * math.sin(x / 17 + fase))
            claro, oscuro = _tono(colores[len(colores) // 2], 0.3), _tono(colores[-1], -0.2)
            sup.set_at((x, y), claro)
            for k in range(1, 4):
                if k < 3 - 2 * _umbral(x, y + k) and (x + y + k) % 2 == 0:
                    sup.set_at((x, y + k), oscuro)
    for _ in range(puntitos):
        x, y = azar.randrange(ANCHO), azar.randrange(y0 + 2, ALTO)
        base = colores[min(len(colores) - 1, (y - y0) * len(colores) // max(1, ALTO - y0))]
        sup.set_at((x, y), _tono(base, azar.choice((-0.25, -0.15, 0.2, 0.3))))


def pared_cueva(sup):
    """La montaña de la cueva: dos capas de roca con la cumbre iluminada, estratos, grietas, rocas y la
    boca oscura alrededor de la compuerta."""
    cordillera(sup, [(0, 40), (40, 26), (80, 38), (120, 20), (170, 30), (220, 16), (270, 32), (320, 26)],
               112, (112, 48, 76), (160, 72, 82))
    tops = cordillera(sup, [(0, 66), (50, 54), (100, 66), (130, 44), (200, 48), (250, 62), (320, 54)],
                      112, (150, 64, 72), (204, 94, 80))
    for k in range(6):                                           # estratos de la roca: línea oscura con luz abajo
        base = 66 + k * 7
        for x in range(ANCHO):
            y = base + int(2 * math.sin(x / 21 + k * 1.9) + math.sin(x / 7 + k))
            if tops[x] + 3 < y < 108 and (x * 3 + y) % 5 != 0:
                c = sup.get_at((x, y))
                sup.set_at((x, y), _tono((c.r, c.g, c.b), -0.2))
                c2 = sup.get_at((x, y + 1))
                sup.set_at((x, y + 1), _tono((c2.r, c2.g, c2.b), 0.1))
    for puntos in (((30, 70), (44, 86), (38, 100)), ((240, 66), (252, 80), (246, 96)), ((280, 46), (292, 62), (286, 74))):
        for (xa, ya), (xb, yb) in zip(puntos, puntos[1:]):       # grietas: línea oscura y borde claro al lado
            pygame.draw.line(sup, (70, 28, 44), (xa, ya), (xb, yb))
            pygame.draw.line(sup, (206, 108, 90), (xa + 1, ya), (xb + 1, yb))
    for y in range(40, 112):                                     # la boca de la cueva: sombra por bandas, solo sobre la roca
        for x in range(120, 204):
            d = math.hypot((x - 162) / 42, (y - 82) / 40)
            if d >= 1 or y <= tops[x] + 1:
                continue
            p = min(2.999, (1 - d) * 3.4)
            i = int(p)
            nivel = i + 1 if (p - i) > _umbral(x, y) else i
            alfa = (0.0, 0.22, 0.42, 0.62)[nivel]
            if alfa:
                c = sup.get_at((x, y))
                sup.set_at((x, y), _mezclar((c.r, c.g, c.b), (34, 14, 34), alfa))
    for x, y, rx, ry in ((24, 108, 9, 5), (300, 110, 8, 5), (110, 111, 6, 4), (232, 110, 7, 4)):
        roca(sup, x, y, rx, ry)


def suelo_cueva(sup):
    """El suelo de roca de la entrada de la cueva."""
    suelo_llano(sup, 108, [(172, 84, 64), (160, 76, 58), (148, 70, 54), (136, 62, 50)], 12,
                dunas=((124, 2, 0.8, 60), (142, 2, 2.2, 80)), puntitos=260)
    for x, y, rx, ry in ((40, 140, 4, 3), (230, 136, 5, 3), (290, 144, 4, 3)):
        roca(sup, x, y, rx, ry)


def roca(sup, cx, cy, rx, ry):
    """Una roca con volumen (luz arriba a la izquierda) y su sombra en el piso."""
    for y in range(cy + ry // 2, cy + ry + 2):
        for x in range(cx - rx, cx + rx + 5):
            if ((x - cx - 3) / (rx + 3)) ** 2 + ((y - cy - ry * 0.7) / (ry * 0.45)) ** 2 < 1 and _umbral(x, y) < 0.7:
                sup.set_at((x, y), (120, 48, 50))
    rampa = [(92, 38, 50), (140, 62, 64), (190, 98, 80), (232, 146, 104)]
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny > 1:
                continue
            luz = max(0, min(0.99, 0.55 - 0.55 * nx - 0.5 * ny + 0.25 * math.sqrt(max(0, 1 - nx * nx - ny * ny))))
            p = luz * 3
            i = int(p)
            sup.set_at((x, y), rampa[i + 1] if (p - i) > _umbral(x, y) else rampa[i])


def fondo_choque(sup):
    """El fondo completo del sitio del choque."""
    cielo(sup)
    cordillera(sup, [(0, 70), (30, 62), (64, 72), (100, 56), (140, 70), (180, 63), (225, 74), (262, 58),
                     (300, 68), (320, 64)], 84, (150, 64, 92), (222, 110, 96))
    cordillera(sup, [(0, 78), (50, 71), (96, 79), (150, 72), (210, 80), (260, 73), (320, 79)],
               86, (112, 46, 78), (172, 78, 80))
    suelo_marte(sup)
    for x, y, rx, ry in ((20, 140, 5, 3), (180, 132, 4, 3), (250, 142, 6, 4), (290, 118, 4, 3),
                         (110, 138, 3, 2), (70, 122, 3, 2)):
        roca(sup, x, y, rx, ry)
    for i in range(61):                              # marca del aterrizaje forzoso: surco con el borde iluminado
        x = 90 + i
        y = 108 + int(i * 4 / 60)
        sup.set_at((x, y), (230, 140, 92))
        sup.set_at((x, y + 1), (104, 42, 44))
        sup.set_at((x, y + 2), (126, 52, 50))
