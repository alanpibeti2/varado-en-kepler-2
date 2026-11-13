"""
kepler/arte_cueva.py
El interior de la cueva de cristales, con el mismo estilo de 16 bits que el resto del juego: roca pintada punto por
punto con rampas de color y trama (dithering), iluminada por el brillo del cristal gigante, racimos de cristales
facetados, estalactitas, charcos y partículas.

Todo lo estático se pinta UNA vez en el fondo; lo que se mueve (el halo, el brillo del cristal, las motas de luz,
las gotas y las ondas del agua) se dibuja cada cuadro desde la escena.
"""

import math
import random

import pygame

from kepler.arte import _tono
from kepler.arte16 import _elegir

ANCHO, ALTO = 320, 150
CONTORNO = (10, 8, 28)
FOCO = (160, 84)                  # el centro del cristal gigante: de ahí sale la luz
CIAN_LUZ = (120, 228, 242)

RAMPAS_CRISTAL = {
    "cian": [(12, 40, 84), (22, 84, 130), (40, 150, 190), (100, 220, 240), (200, 252, 255)],
    "violeta": [(40, 20, 90), (80, 44, 150), (130, 84, 200), (184, 140, 238), (236, 214, 255)],
    "verde": [(10, 56, 64), (20, 110, 100), (48, 176, 140), (120, 232, 180), (214, 255, 230)],
}
FONDO = [(8, 5, 22), (16, 10, 38), (28, 16, 58), (44, 26, 82), (66, 40, 108)]
ROCA = [(26, 12, 34), (46, 22, 52), (76, 38, 70), (112, 58, 86), (156, 86, 104), (200, 124, 126)]
SUELO = [(36, 18, 40), (58, 28, 54), (88, 44, 68), (122, 62, 84), (160, 88, 98)]
AGUA = [(12, 30, 66), (20, 64, 108), (38, 124, 158), (104, 208, 228), (214, 250, 255)]


def _ruido(x, y, semilla=0):
    """Un número entre 0 y 1 repetible para cada punto (granito de la roca)."""
    n = (x * 374761393 + y * 668265263 + semilla * 1442695041) & 0xFFFFFFFF
    n = (n ^ (n >> 13)) * 1274126177 & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def luz_del_cristal(x, y):
    """Cuánta luz del cristal llega a un punto (0 a 1): fuerte cerca, se apaga con la distancia."""
    d = math.hypot((x - FOCO[0]) / 150.0, (y - FOCO[1]) / 85.0)
    return max(0.0, 1.0 - d) ** 1.5


def teñir(color, x, y, extra=0.0):
    """Pinta de celeste la roca que está cerca del cristal, por escalones y con trama de puntitos."""
    p = min(2.999, (luz_del_cristal(x, y) + extra) * 4.4)
    if p <= 0:
        return color
    i = int(p)
    nivel = i + 1 if (p - i) > ((_BAYER[y % 4][x % 4] + 0.5) / 16) else i
    alfa = (0.0, 0.16, 0.32, 0.5)[min(3, nivel)]
    if not alfa:
        return color
    return (int(color[0] * (1 - alfa) + CIAN_LUZ[0] * alfa), int(color[1] * (1 - alfa) + CIAN_LUZ[1] * alfa),
            int(color[2] * (1 - alfa) + CIAN_LUZ[2] * alfa))


_BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))


def _estrato(x, y, fase=0.0):
    """Ondas horizontales suaves que dan la idea de capas de roca."""
    return math.sin(y * 0.33 + math.sin(x * 0.045 + fase) * 2.0 + math.sin(x * 0.13) * 0.6)


# ---------------------------------------------------------------------- #
#  Roca
# ---------------------------------------------------------------------- #

def pared_del_fondo(sup):
    """La pared lejana, muy oscura, con capas, y una boca de túnel más negra detrás del cristal."""
    for y in range(0, 112):
        for x in range(ANCHO):
            v = 0.16 + 0.34 * (y / 112.0) + 0.08 * _estrato(x, y) + 0.05 * (_ruido(x, y) - 0.5)
            # el túnel del fondo: un arco oscuro
            d = math.hypot((x - 160) / 74.0, (y - 108) / 70.0)
            if d < 1.0:
                v -= 0.2 * (1 - d) ** 0.7
            color = _elegir(FONDO, v, x, y)
            sup.set_at((x, y), teñir(color, x, y))


def masa_de_roca(sup, puntos, lado_luz, semilla=1):
    """
    Una mole de roca en primer plano (los laterales, el techo y el pedestal): se pinta punto por punto dentro del polígono. El borde
    que mira al cristal (lado_luz = +1 derecha, -1 izquierda, 0 abajo, 2 arriba) queda más claro, y todo se tiñe de celeste cerca
    del cristal.
    """
    xs = [p[0] for p in puntos]
    ys = [p[1] for p in puntos]
    mascara = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    pygame.draw.polygon(mascara, (255, 255, 255, 255), puntos)
    x0, x1, y0, y1 = max(0, min(xs)), min(ANCHO - 1, max(xs)), max(0, min(ys)), min(ALTO - 1, max(ys))
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if not mascara.get_at((x, y)).a:
                continue
            # cuánto está cerca del borde que mira a la luz: se ve más claro (borde iluminado)
            borde = 0
            if lado_luz != 0:
                for k in range(1, 7):
                    if not (0 <= x + lado_luz * k < ANCHO) or not mascara.get_at((x + lado_luz * k, y)).a:
                        borde = (7 - k) / 6.0
                        break
            elif lado_luz == 2:                                     # el borde de arriba (un pedestal iluminado)
                for k in range(1, 7):
                    if y - k < 0 or not mascara.get_at((x, y - k)).a:
                        borde = (7 - k) / 6.0
                        break
            else:                                                   # el borde de abajo (el techo, iluminado desde abajo)
                for k in range(1, 7):
                    if y + k >= ALTO or not mascara.get_at((x, y + k)).a:
                        borde = (7 - k) / 6.0
                        break
            v = 0.22 + 0.13 * _estrato(x, y, semilla) + 0.05 * (_ruido(x, y, semilla) - 0.5) * 2 + 0.5 * borde ** 1.4
            v += 0.2 * luz_del_cristal(x, y)
            color = _elegir(ROCA, v, x, y)
            sup.set_at((x, y), teñir(color, x, y, 0.1 * borde))
    # contorno oscuro de la mole
    pygame.draw.polygon(sup, (14, 6, 22), puntos, 1)


def techo_con_estalactitas(sup):
    """El techo de roca, con estalactitas de distintos largos. Devuelve la lista de puntas (x, y)."""
    azar = random.Random(4)
    borde = []
    x = 0
    puntas = []
    while x <= ANCHO:
        base = 16 + int(3 * math.sin(x / 19.0))
        borde.append((x, base))
        if x > 6 and x < ANCHO - 6 and azar.random() < 0.55:
            largo = azar.randint(10, 30)
            if x in (92, 232):
                largo = 34
            ancho = azar.randint(5, 8)
            borde.append((x + ancho // 2 - 3, base + 2))
            borde.append((x + ancho // 2 + 1, base + largo))                   # la punta
            borde.append((x + ancho + 3, base + 2))
            puntas.append((x + ancho // 2 + 1, base + largo))
            x += ancho + 6
        else:
            x += 6
    # dos estalactitas fijas largas, para que goteen sobre los charcos
    pol = [(0, 0)] + borde + [(ANCHO, 0)]
    masa_de_roca(sup, pol, 0, semilla=7)
    return puntas


def piso(sup):
    """El suelo de roca, con piedritas y un brillo celeste alrededor del cristal."""
    for y in range(112, ALTO):
        for x in range(ANCHO):
            f = (y - 112) / 38.0
            v = 0.26 + 0.28 * f + 0.07 * math.sin(x / 9.0 + y / 4.0) + 0.06 * (_ruido(x, y, 3) - 0.5) * 2
            g = max(0.0, 1.0 - math.hypot((x - 160) / 130.0, (y - 122) / 30.0))
            v += 0.16 * g ** 1.3
            color = _elegir(SUELO, v, x, y)
            sup.set_at((x, y), teñir(color, x, y, 0.3 * g))
    pygame.draw.line(sup, (20, 8, 28), (0, 111), (ANCHO, 111))                  # el borde del fondo con el piso
    pygame.draw.line(sup, (150, 84, 100), (0, 112), (ANCHO, 112))


def piedra(sup, cx, cy, rx, ry):
    """Una piedra con luz a la izquierda y sombra a la derecha, apoyada en el piso."""
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            if nx * nx + ny * ny > 1:
                continue
            v = 0.48 - 0.35 * nx - 0.25 * ny + 0.3 * luz_del_cristal(x, y)
            sup.set_at((x, y), teñir(_elegir(ROCA, v, x, y), x, y))
    pygame.draw.ellipse(sup, (14, 6, 22), (cx - rx, cy - ry, rx * 2 + 1, ry * 2 + 1), 1)
    pygame.draw.line(sup, (20, 8, 28), (cx - rx, cy + ry + 1), (cx + rx, cy + ry + 1))


# ---------------------------------------------------------------------- #
#  Cristales
# ---------------------------------------------------------------------- #

def prisma(sup, cx, base, ancho, alto, tono="cian", brillo=0.0):
    """
    Un prisma de cristal: cara izquierda clara, cara derecha oscura y la punta con facetas, con vetas y un destello.
    'brillo' (-1 a 1) lo enciende o lo apaga un poco (así late el cristal gigante).
    """
    m = max(2, ancho // 2)
    punta = base - alto
    hombro = punta + int(m * 1.1) + 1
    rampa = RAMPAS_CRISTAL[tono]
    for y in range(punta, base + 1):
        for x in range(cx - m, cx + m + 1):
            tope = punta + abs(x - cx) / m * (hombro - punta)
            if y < tope:
                continue
            izq = x < cx
            if y < hombro:                                           # la faceta de la punta
                v = 0.82 if izq else 0.58
            else:
                v = 0.6 if izq else 0.3
            v += 0.2 * (1 - min(1.0, math.hypot((x - cx) / m, (y - (base - alto * 0.45)) / (alto * 0.6))))
            v += 0.12 * brillo + 0.05 * math.sin(y * 0.9 + x * 0.4)
            if x in (cx - m, cx + m):
                v -= 0.18
            sup.set_at((x, y), _elegir(rampa, v, x, y))
    pts = [(cx - m, base), (cx - m, hombro), (cx, punta), (cx + m, hombro), (cx + m, base)]
    pygame.draw.polygon(sup, CONTORNO, pts, 1)
    pygame.draw.line(sup, rampa[1], (cx, hombro), (cx, base - 1))             # la arista del medio
    if alto > 14:
        pygame.draw.line(sup, rampa[4], (cx - m + 2, hombro + 3), (cx - m + 2, base - alto // 3))   # el destello largo
        sup.set_at((cx - m + 3, hombro + 2), (255, 255, 255))


def racimo(sup, x, base, ancho, alto, tono="cian", brillo=0.0):
    """Un grupito de prismas de distinto tamaño (los de atrás primero)."""
    for rx, rw, rh in ((0.12, 0.22, 0.46), (0.88, 0.22, 0.4), (0.3, 0.3, 0.7), (0.7, 0.3, 0.62), (0.5, 0.42, 1.0)):
        prisma(sup, x + int(ancho * rx), base - (0 if rx not in (0.12, 0.88) else 1), max(4, int(ancho * rw)),
               int(alto * rh), tono, brillo)


def racimo_colgante(sup, x, techo, ancho, largo, tono="violeta"):
    """Un racimo que cuelga del techo: se pinta al derecho en una imagen aparte y se da vuelta."""
    capa = pygame.Surface((ancho + 4, largo + 2), pygame.SRCALPHA)
    racimo(capa, 2, largo + 1, ancho, largo, tono)
    sup.blit(pygame.transform.flip(capa, False, True), (x, techo - 1))


def cristal_gigante(sup, x, base, ancho, alto, brillo=0.0):
    """El cristal de energía enorme del fondo: un racimo grande de prismas celestes, con un núcleo que late."""
    racimo(sup, x, base, ancho, alto, "cian", brillo)


# ---------------------------------------------------------------------- #
#  Agua
# ---------------------------------------------------------------------- #

def charco(sup, cx, cy, rx, ry):
    """Un charco de agua clara en el piso, con reflejos del cristal."""
    for y in range(cy - ry, cy + ry + 1):
        for x in range(cx - rx, cx + rx + 1):
            nx, ny = (x - cx) / rx, (y - cy) / ry
            d = nx * nx + ny * ny
            if d > 1:
                continue
            v = 0.34 + 0.4 * luz_del_cristal(x, y) + 0.06 * math.sin(y * 1.7 + x * 0.25) - 0.12 * (ny > 0.4)
            v += 0.25 * max(0.0, 1 - abs(x - 160) / 22.0) * (ny < 0.2)         # el reflejo del cristal
            if d > 0.78:
                v -= 0.2                                                       # la orilla, más oscura
            sup.set_at((x, y), _elegir(AGUA, v, x, y))
    pygame.draw.ellipse(sup, (20, 8, 28), (cx - rx - 1, cy - ry - 1, rx * 2 + 3, ry * 2 + 3), 1)
    pygame.draw.line(sup, (150, 84, 100), (cx - rx + 2, cy + ry + 2), (cx + rx - 2, cy + ry + 2))   # luz en el borde de abajo


# ---------------------------------------------------------------------- #
#  Animados (se dibujan cada cuadro)
# ---------------------------------------------------------------------- #

def halo(sup, cx, cy, t):
    """El halo del cristal: discos de puntitos celestes que laten despacio (sin transparencias)."""
    pulso = 0.5 + 0.5 * math.sin(t * 2.4)
    for radio, color, hueco in ((int(46 + 5 * pulso), (40, 120, 170), 0.82), (int(34 + 4 * pulso), (70, 170, 210), 0.72),
                                (int(22 + 3 * pulso), (130, 224, 240), 0.62)):
        for y in range(cy - radio, cy + radio + 1):
            for x in range(cx - radio, cx + radio + 1):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radio * radio and ((_BAYER[y % 4][x % 4] + 0.5) / 16) >= hueco:
                    if 0 <= x < ANCHO and 0 <= y < ALTO:
                        sup.set_at((x, y), color)


def motas(sup, t, cx=160, base=108):
    """Motitas de luz que flotan hacia arriba alrededor del cristal."""
    for k in range(18):
        ciclo = (t * (6 + k % 4) + k * 13) % 80
        x = cx + int(math.sin(k * 2.3 + t * 0.7) * (22 + (k * 5) % 34))
        y = base - int(ciclo)
        color = (230, 255, 255) if k % 3 == 0 else (130, 228, 242) if k % 3 == 1 else (170, 150, 255)
        if ciclo < 60 or (int(t * 8) + k) % 2 == 0:                        # al final titilan y se apagan
            sup.set_at((x, y), color)
            if k % 4 == 0:
                sup.set_at((x + 1, y), color)


def destellos(sup, rect, t):
    """Destellos en cruz que titilan sobre el cristal."""
    x0, y0, w, h = rect
    n = int(t * 3)
    for i, (fx, fy) in enumerate(((0.22, 0.3), (0.62, 0.18), (0.78, 0.55), (0.4, 0.7))):
        if (n + i) % 4 == 0:
            x, y = x0 + int(w * fx), y0 + int(h * fy)
            for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1), (-2, 0), (2, 0), (0, -2), (0, 2)):
                sup.set_at((x + dx, y + dy), (255, 255, 255) if abs(dx) + abs(dy) < 2 else (190, 244, 255))


def goteras(sup, t, puntas_y):
    """
    Gotas que caen de dos estalactitas a los charcos, y las ondas que se abren al caer.
    puntas_y: {x_de_la_gota: (y_de_la_punta, y_del_agua)}.
    """
    for k, (gx, (punta, agua)) in enumerate(puntas_y.items()):
        ciclo = (t + k * 1.3) % 3.4
        caida = (agua - punta) / 90.0                                       # segundos que tarda en caer
        if 0.5 < ciclo < 0.5 + caida:                                       # la gota cae acelerando
            u = (ciclo - 0.5) / caida
            y = punta + int((agua - punta) * u * u)
            sup.set_at((gx, y), (190, 244, 255))
            sup.set_at((gx, y - 1), (110, 200, 230))
        e = ciclo - (0.5 + caida)                                           # segundos desde que cayó
        if 0 <= e < 1.0:                                                    # ondas que crecen y se apagan
            for r, color in ((int(2 + e * 10), (214, 250, 255)), (int(e * 7), (130, 210, 230))):
                if r < 2 or (e > 0.7 and r % 2):
                    continue
                for ang in range(0, 360, 12):
                    px = gx + int(math.cos(math.radians(ang)) * r)
                    py = agua + int(math.sin(math.radians(ang)) * r * 0.35)
                    sup.set_at((px, py), color)
