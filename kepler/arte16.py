"""
kepler/arte16.py
Los objetos grandes de los escenarios, redibujados con estilo de 16 bits: varios tonos por material,
luz desde arriba a la izquierda, sombras frías, brillos y degradados con trama (dithering).

Reemplaza a las versiones planas de arte.py: la nave, el cohete, la compuerta, los puestos del mercado
(toldo, mostrador y mercadería), la caja negra y las cosas del interior de la nave.
"""

import math

import pygame

from kepler.arte import _tono, _caja_sombreada
from kepler.paisaje import esfera, _umbral, _mezclar

CONTORNO = (30, 26, 46)


def _rampa(color, niveles=5):
    """Una escala de tonos del color: de sombra fría a luz cálida."""
    if niveles == 5:
        return [_tono(color, -0.55), _tono(color, -0.28), color, _tono(color, 0.32), _tono(color, 0.65)]
    return [_tono(color, -0.45), color, _tono(color, 0.4)]


def _elegir(rampa, valor, x, y, tramar=True):
    """Elige un tono de la rampa para 'valor' (0 a 1). Con 'tramar', entre un tono y el siguiente hay puntitos
    alternados (dithering); sin 'tramar', se pasa de un tono al otro en bandas limpias."""
    p = max(0.0, min(0.999, valor)) * (len(rampa) - 1)
    i = int(p)
    if not tramar:
        return rampa[min(len(rampa) - 1, int(p + 0.5))]
    return rampa[i + 1] if (p - i) > _umbral(x, y) else rampa[i]


def _columnas(puntos, ancho, alto):
    """Para un polígono, devuelve {x: (y_arriba, y_abajo)} de cada columna que ocupa."""
    mascara = pygame.Surface((ancho, alto))
    mascara.fill((0, 0, 0))
    pygame.draw.polygon(mascara, (255, 255, 255), puntos)
    limites = {}
    for x in range(ancho):
        ys = [y for y in range(alto) if mascara.get_at((x, y))[0] > 0]
        if ys:
            limites[x] = (min(ys), max(ys))
    return limites


def _madera(sup, rect, tono=(140, 92, 58), horizontal=True, tablones=0):
    """Una tabla de madera con vetas (puntitos más oscuros), luz arriba y sombra abajo."""
    x, y, w, h = rect
    rampa = _rampa(tono)
    for py in range(y, y + h):
        t = (py - y) / max(1, h - 1) if horizontal else (py - y) / max(1, h - 1) * 0.3
        for px in range(x, x + w):
            u = (px - x) / max(1, w - 1)
            v = 0.64 - 0.32 * (t if horizontal else u)
            if (px * 5 + py * 3) % 17 == 0:
                v -= 0.14                       # veta
            sup.set_at((px, py), _elegir(rampa, v, px, py, tramar=False))
    for k in range(1, tablones):                # separaciones entre tablones
        px = x + k * w // tablones
        pygame.draw.line(sup, _tono(tono, -0.6), (px, y), (px, y + h - 1))
        pygame.draw.line(sup, _tono(tono, 0.25), (px + 1, y), (px + 1, y + h - 1))


# ---------------------------------------------------------------------- #
#  Cápsula estrellada
# ---------------------------------------------------------------------- #

def capsula(sup, rect):
    """La cápsula de escape estrellada: casco metálico con luz y sombra, ventanilla rota, quemaduras y humo."""
    x, y, w, h = rect
    # Sombra en el piso, con trama
    for py in range(y + h - 6, y + h + 4):
        for px in range(x - 2, x + w + 4):
            if ((px - (x + w / 2 + 2)) / (w / 2 + 4)) ** 2 + ((py - (y + h - 1)) / 5.0) ** 2 < 1 and _umbral(px, py) < 0.65:
                sup.set_at((px, py), (104, 42, 48))

    cuerpo = [(x + 4, y + h - 4), (x + 10, y + 10), (x + 44, y + 4), (x + 60, y + 18), (x + 56, y + h - 2)]
    aleta = [(x + 56, y + h - 2), (x + 64, y + h - 10), (x + 62, y + h)]
    pygame.draw.polygon(sup, (112, 116, 140), aleta)
    pygame.draw.line(sup, (170, 174, 196), (x + 57, y + h - 3), (x + 63, y + h - 9))
    pygame.draw.polygon(sup, CONTORNO, aleta, 1)

    # Casco: cada columna va de luz arriba a sombra abajo, y se oscurece hacia la derecha
    rampa = [(240, 242, 252), (200, 204, 222), (160, 164, 188), (120, 124, 154), (84, 86, 116)]
    ancho, alto = w + 8, h + 4
    limites = _columnas([(px - x, py - y) for px, py in cuerpo], ancho, alto)
    casco = {(x + cx, y + cy) for cx, (a, b) in limites.items() for cy in range(a, b + 1)}   # píxeles del casco
    for cx, (arriba, abajo) in limites.items():
        for cy in range(arriba, abajo + 1):
            t = (cy - arriba) / max(1, abajo - arriba)
            valor = t * 0.82 + (cx / w) * 0.22
            sup.set_at((x + cx, y + cy), _elegir(rampa, valor, x + cx, y + cy))

    # Franja roja con volumen
    franja = [(x + 8, y + 21), (x + 57, y + 15), (x + 58, y + 19), (x + 8, y + 25)]
    pygame.draw.polygon(sup, (196, 66, 52), franja)
    pygame.draw.line(sup, (248, 138, 96), (x + 8, y + 21), (x + 57, y + 15))
    pygame.draw.line(sup, (120, 34, 44), (x + 8, y + 25), (x + 58, y + 19))

    # Junturas de los paneles (línea oscura + línea de luz al lado) con remaches
    for x0, y0, x1, y1 in ((22, 7, 20, 31), (41, 5, 40, 32)):
        pygame.draw.line(sup, (86, 90, 120), (x + x0, y + y0), (x + x1, y + y1))
        pygame.draw.line(sup, (214, 218, 234), (x + x0 + 1, y + y0), (x + x1 + 1, y + y1))
        for ry in range(y0 + 3, y1, 6):
            sup.set_at((x + x0 + (x1 - x0) * (ry - y0) // max(1, y1 - y0) + 2, y + ry), (240, 242, 252))

    # Ventanilla rota: marco, vidrio degradado, reflejo y grieta
    pygame.draw.ellipse(sup, (64, 66, 90), (x + 23, y + 9, 14, 11))
    pygame.draw.ellipse(sup, (140, 144, 168), (x + 23, y + 9, 14, 11), 1)
    for py in range(y + 11, y + 19):
        for px in range(x + 25, x + 35):
            if ((px - (x + 30)) / 5) ** 2 + ((py - (y + 15)) / 4) ** 2 <= 1:
                sup.set_at((px, py), _mezclar((22, 34, 92), (90, 138, 218), (py - y - 11) / 7 if _umbral(px, py) < 0.8 else 0.3))
    for dx, dy in ((27, 12), (28, 12), (27, 13)):
        sup.set_at((x + dx, y + dy), (206, 232, 255))
    for dx, dy in ((31, 11), (32, 13), (31, 14), (33, 16)):
        sup.set_at((x + dx, y + dy), (232, 244, 255))

    # Quemaduras: manchas de hollín con trama, más densas en el centro
    for cx, cy, r in ((x + 16, y + 26, 7), (x + 44, y + 25, 6), (x + 50, y + 30, 6)):
        for py in range(cy - r, cy + r + 1):
            for px in range(cx - r, cx + r + 1):
                d = math.hypot(px - cx, py - cy) / r
                if d < 1 and (1 - d) * 1.4 > _umbral(px, py):
                    if (px, py) in casco:
                        color = sup.get_at((px, py))
                        sup.set_at((px, py), _mezclar((color.r, color.g, color.b), (46, 38, 52), 0.8))

    # Rotura del frente: se ve el interior oscuro y cables
    pygame.draw.polygon(sup, (22, 18, 30), [(x + 52, y + 22), (x + 57, y + 20), (x + 56, y + 27), (x + 51, y + 26)])
    for dx, dy, c in ((53, 23, (240, 200, 60)), (55, 24, (230, 60, 60)), (54, 25, (90, 200, 240))):
        sup.set_at((x + dx, y + dy), c)

    # Contorno oscuro y brillo del borde de arriba
    pygame.draw.polygon(sup, CONTORNO, cuerpo, 1)
    pygame.draw.line(sup, (250, 250, 255), (x + 12, y + 11), (x + 43, y + 6))

    # Humo: bolas con luz arriba a la izquierda
    humo = [(52, 48, 60), (84, 78, 92), (122, 114, 128), (166, 158, 170)]
    for cx, cy, r in ((x + 46, y - 2, 4), (x + 51, y - 10, 5), (x + 47, y - 20, 6)):
        esfera(sup, cx, cy, r, humo)


# ---------------------------------------------------------------------- #
#  Cohete y base de lanzamiento
# ---------------------------------------------------------------------- #

def cohete(sup, rect, energia):
    """El cohete sobre su base: cuerpo cilíndrico con luz a la izquierda, punta y aletas rojas, ventana con brillo."""
    x, y, w, h = rect
    cx = x + w // 2
    blanco = [(112, 118, 150), (160, 166, 196), (206, 212, 232), (238, 242, 252), (255, 255, 255)]
    rojo = [(100, 24, 44), (160, 38, 54), (214, 66, 70), (246, 124, 112)]

    def luz(u):                                     # u: 0 (borde izquierdo) a 1 (borde derecho)
        return max(0.0, 1.0 - abs(u - 0.30) / 0.78)

    # Aletas detrás del cuerpo: la izquierda recibe luz, la derecha queda en sombra
    for lado, claro in ((-1, True), (1, False)):
        aleta = [(cx + lado * 10, y + 52), (cx + lado * 22, y + 80), (cx + lado * 10, y + 76)]
        pygame.draw.polygon(sup, rojo[2] if claro else rojo[1], aleta)
        pygame.draw.line(sup, rojo[3] if claro else rojo[2], aleta[0], aleta[1])
        pygame.draw.line(sup, rojo[0], aleta[1], aleta[2])
        pygame.draw.polygon(sup, CONTORNO, aleta, 1)

    # Cuerpo
    for py in range(y + 18, y + 75):
        for px in range(cx - 10, cx + 10):
            sup.set_at((px, py), _elegir(blanco, luz((px - cx + 10) / 19), px, py))
    # Punta: la misma luz, en rojo
    for py in range(y, y + 19):
        mitad = round(10 * (py - y) / 18)
        for px in range(cx - mitad, cx + mitad + 1):
            sup.set_at((px, py), _elegir(rojo, luz((px - cx + 10) / 19) * 1.05, px, py))
    pygame.draw.line(sup, (255, 190, 170), (cx - 1, y + 2), (cx - 3, y + 8))        # brillo de la punta
    # Franjas de unión (una oscura y una clara al lado) y banda roja de arriba
    for ry in (y + 20, y + 46, y + 70):
        pygame.draw.line(sup, (86, 90, 122), (cx - 10, ry), (cx + 9, ry))
        pygame.draw.line(sup, (244, 246, 255), (cx - 10, ry + 1), (cx + 6, ry + 1))
    for py in range(y + 21, y + 25):
        for px in range(cx - 10, cx + 10):
            sup.set_at((px, py), _elegir(rojo, luz((px - cx + 10) / 19) * (0.9 - (py - y - 21) * 0.1), px, py))
    # Remaches
    for ry in (y + 28, y + 40, y + 56):
        for rx in (cx - 8, cx + 7):
            sup.set_at((rx, ry), (250, 252, 255) if rx < cx else (120, 124, 156))

    # Ventana: aro de metal, vidrio esférico y reflejo
    pygame.draw.circle(sup, (74, 78, 104), (cx, y + 32), 6)
    pygame.draw.circle(sup, (156, 162, 190), (cx, y + 32), 6, 1)
    vidrio = ([(20, 40, 96), (40, 86, 170), (84, 160, 230), (176, 236, 255)] if energia
              else [(14, 18, 48), (28, 40, 92), (46, 64, 128), (96, 120, 182)])
    esfera(sup, cx, y + 32, 4, vidrio)
    sup.set_at((cx - 2, y + 30), (255, 255, 255))

    # Medidor de energía en un hueco oscuro (la cuarta barra titila: ver luces_cohete)
    pygame.draw.rect(sup, (28, 30, 44), (cx - 5, y + 48, 10, 19))
    pygame.draw.rect(sup, (110, 114, 144), (cx - 5, y + 48, 10, 19), 1)
    for i in range(4):
        encendida = energia and i < 3
        pygame.draw.rect(sup, (90, 230, 120) if encendida else (52, 54, 68), (cx - 3, y + 62 - i * 4, 6, 3))
        if encendida:
            pygame.draw.line(sup, (190, 255, 200), (cx - 3, y + 62 - i * 4), (cx + 2, y + 62 - i * 4))

    # Contorno del cuerpo y toberas
    pygame.draw.lines(sup, CONTORNO, False, [(cx - 10, y + 74), (cx - 10, y + 18), (cx, y), (cx + 10, y + 18), (cx + 10, y + 74)])
    for py in range(y + 74, y + 81):
        mitad = 6 + (py - y - 74) // 2
        for px in range(cx - mitad, cx + mitad + 1):
            sup.set_at((px, py), _elegir([(40, 40, 56), (80, 82, 104), (126, 130, 154), (170, 174, 196)],
                                        luz((px - cx + mitad) / (2 * mitad)) * 0.9, px, py))
    pygame.draw.ellipse(sup, (20, 18, 28), (cx - 6, y + 77, 12, 4))

    # Base de lanzamiento: placa metálica con cara de arriba clara y frente con franjas amarillas y negras
    pygame.draw.rect(sup, (176, 180, 204), (x, y + 80, w, 3))
    for px in range(x, x + w):
        sup.set_at((px, y + 80), (232, 236, 250))
    for py in range(y + 83, y + 92):
        for px in range(x, x + w):
            t = (py - y - 83) / 8
            sup.set_at((px, py), _elegir([(130, 134, 160), (96, 100, 128), (66, 68, 94)], t * 0.9 + (px - x) / w * 0.2, px, py))
    for py in range(y + 86, y + 91):                                          # franja de peligro
        for px in range(x + 1, x + w - 1):
            amarillo = ((px + py) // 4) % 2 == 0
            sup.set_at((px, py), (240, 200, 52) if amarillo else (34, 30, 44))
    for px in range(x + 3, x + w - 2, 8):
        sup.set_at((px, y + 81), (255, 255, 255))                             # remaches
    pygame.draw.rect(sup, CONTORNO, (x, y + 80, w, 12), 1)
    for lado in (-1, 1):                                                      # puntales que sujetan el cohete
        pygame.draw.line(sup, (150, 154, 180), (cx + lado * 10, y + 66), (cx + lado * 17, y + 80))
        pygame.draw.line(sup, CONTORNO, (cx + lado * 11, y + 66), (cx + lado * 18, y + 80))


# ---------------------------------------------------------------------- #
#  Compuerta de la mina
# ---------------------------------------------------------------------- #

def compuerta(sup, rect, abierta, iluminada):
    """La compuerta blindada de la cueva, con marco biselado, remaches y teclado luminoso."""
    x, y, w, h = rect
    marco = pygame.Rect(x - 4, y - 4, w + 8, h + 4)
    _caja_sombreada(sup, marco, (88, 86, 108))
    pygame.draw.rect(sup, CONTORNO, marco, 1)
    interior = pygame.Rect(x, y, w, h)
    if not abierta:
        mitad = w // 2
        for lado, px in ((0, x), (1, x + mitad)):                              # dos hojas con volumen
            _caja_sombreada(sup, (px, y, mitad, h), (136, 138, 160))
            for ry in (y + 6, y + h // 2):
                pygame.draw.line(sup, (96, 98, 124), (px + 2, ry), (px + mitad - 3, ry))
                pygame.draw.line(sup, (186, 188, 208), (px + 2, ry + 1), (px + mitad - 3, ry + 1))
        pygame.draw.line(sup, CONTORNO, (x + mitad, y), (x + mitad, y + h - 1))
        for rx in (x + 3, x + w - 4, x + mitad - 3, x + mitad + 2):            # remaches
            for ry in (y + 3, y + h - 12):
                sup.set_at((rx, ry), (232, 234, 248))
        for i in range(0, w, 8):                                               # franjas de peligro, abajo
            pygame.draw.rect(sup, (240, 200, 52), (x + i, y + h - 6, 4, 6))
            pygame.draw.rect(sup, (34, 30, 44), (x + i + 4, y + h - 6, 4, 6))
        pygame.draw.line(sup, (250, 226, 120), (x, y + h - 6), (x + w - 1, y + h - 6))
    elif not iluminada:
        for py in range(y, y + h):                                             # oscuridad que se hace más densa adentro
            for px in range(x, x + w):
                sup.set_at((px, py), _mezclar((18, 14, 30), (4, 2, 8), (py - y) / h))
    else:
        for py in range(y, y + h):
            for px in range(x, x + w):
                sup.set_at((px, py), _elegir([(14, 22, 52), (24, 40, 88), (34, 62, 120)], (py - y) / h * 0.9 + 0.1, px, py))
        for cx, base, alto in ((x + 8, y + h, 16), (x + 38, y + h, 20), (x + 24, y + h, 12)):   # cristales
            esfera_cristal(sup, cx, base, alto)
    pygame.draw.rect(sup, CONTORNO, interior, 1)
    # Tablerito a la derecha: chico y simétrico (12 de ancho: pantallita centrada y 3 columnas de teclas)
    teclado = pygame.Rect(x + w + 5, y + 12, 12, 25)
    _caja_sombreada(sup, teclado, (58, 60, 80))
    pygame.draw.rect(sup, CONTORNO, teclado, 1)
    pygame.draw.rect(sup, (10, 14, 20), (teclado.x + 2, teclado.y + 2, 8, 4))            # pantallita
    pygame.draw.rect(sup, (24, 86, 62), (teclado.x + 3, teclado.y + 3, 6, 2))
    for fila in range(4):                                                                  # 12 teclas: 3 columnas de 2 px
        for col in range(3):
            tecla = pygame.Rect(teclado.x + 2 + col * 3, teclado.y + 8 + fila * 4, 2, 3)
            pygame.draw.rect(sup, (170, 176, 210), tecla)
            sup.set_at(tecla.topleft, (236, 240, 255))
            sup.set_at((tecla.x + 1, tecla.bottom - 1), (94, 98, 132))


def esfera_cristal(sup, cx, base, alto):
    """Un cristal celeste con caras claras y oscuras (para el interior iluminado de la cueva)."""
    mitad = 4
    punta = base - alto
    pygame.draw.polygon(sup, (80, 190, 220), [(cx - mitad, base), (cx - mitad, punta + 5), (cx, punta), (cx, base)])
    pygame.draw.polygon(sup, (40, 120, 170), [(cx, base), (cx, punta), (cx + mitad, punta + 5), (cx + mitad, base)])
    pygame.draw.line(sup, (210, 250, 255), (cx - 2, punta + 5), (cx - 2, base - 6))
    sup.set_at((cx, punta), (255, 255, 255))


def consola(sup, rect, encendida):
    """La consola de control del cohete: carcasa inclinada con volumen, pantalla con marco y botones que brillan."""
    x, y, w, h = rect
    carcasa = [(x, y + h), (x + w, y + h), (x + w - 3, y + 8), (x + 3, y + 8)]
    rampa = [(48, 50, 72), (74, 76, 102), (104, 108, 136), (148, 152, 180)]
    for py in range(y + 8, y + h):
        for px in range(x, x + w):
            t = (py - y - 8) / max(1, h - 8)
            sup.set_at((px, py), _elegir(rampa, 0.25 + t * 0.55 - (px - x) / w * 0.2, px, py))
    pygame.draw.polygon(sup, CONTORNO, carcasa, 1)
    _caja_sombreada(sup, (x + 2, y, w - 4, 12), (118, 122, 148))                    # el panel de arriba
    pantalla = pygame.Rect(x + 4, y + 2, w - 8, 8)
    pygame.draw.rect(sup, (10, 14, 20), pantalla.inflate(2, 2))
    pygame.draw.rect(sup, (20, 80, 48) if encendida else (22, 24, 34), pantalla)
    if encendida:
        pygame.draw.line(sup, (40, 130, 80), (pantalla.x, pantalla.y), (pantalla.right - 1, pantalla.y))
    else:
        pygame.draw.line(sup, (44, 48, 66), (pantalla.x + 1, pantalla.y + 1), (pantalla.x + 4, pantalla.y + 1))
    for i, color in enumerate(((230, 60, 60), (240, 200, 60), (90, 200, 240))):
        px = x + 6 + i * 7
        pygame.draw.rect(sup, _tono(color, -0.45) if encendida else (54, 56, 72), (px, y + 15, 5, 4))
        if encendida:
            pygame.draw.rect(sup, color, (px, y + 15, 4, 3))
            sup.set_at((px, y + 15), _tono(color, 0.6))


def cupula(sup, cx, base_y, radio):
    """Una cúpula de la base lejana: esfera de metal con luz y una ventana, mitad tapada por el piso."""
    esfera(sup, cx, base_y, radio, [(52, 56, 84), (84, 88, 120), (128, 134, 164), (180, 186, 210), (226, 230, 244)])
    pygame.draw.circle(sup, CONTORNO, (cx, base_y), radio, 1)
    pygame.draw.rect(sup, (110, 230, 245), (cx - 1, base_y - radio // 2, 3, 2))


def torre(sup, x0, x1, y0, y1):
    """La torre de lanzamiento: dos columnas (la izquierda con luz) unidas por una celosía en X."""
    for y in range(y0, y1, 10):
        pygame.draw.line(sup, (96, 72, 76), (x0, y), (x1, y + 10))
        pygame.draw.line(sup, (96, 72, 76), (x1, y), (x0, y + 10))
        pygame.draw.line(sup, (150, 118, 116), (x0 + 1, y), (x1 + 1, y + 10))
        pygame.draw.line(sup, (140, 108, 108), (x0, y + 10), (x0 + 1, y + 10))
        pygame.draw.line(sup, (120, 90, 92), (x0, y), (x1, y))
    pygame.draw.line(sup, (176, 142, 136), (x0, y0), (x0, y1), 2)
    pygame.draw.line(sup, (84, 62, 70), (x1 + 1, y0), (x1 + 1, y1), 2)
    pygame.draw.line(sup, (230, 196, 182), (x0, y0), (x0, y1))
    pygame.draw.rect(sup, (216, 70, 70), (x0 - 1, y0 - 3, x1 - x0 + 3, 3))                 # luz de aviso arriba
    pygame.draw.line(sup, (255, 150, 130), (x0 - 1, y0 - 3), (x1 + 1, y0 - 3))


# ---------------------------------------------------------------------- #
#  Mercado
# ---------------------------------------------------------------------- #

ANCHO_PUESTO = 72          # todos los puestos del mercado miden lo mismo
Y_MOSTRADOR = 94           # dónde empieza la tapa del mostrador
ALTO_MOSTRADOR = 18


def _toldo(sup, x, ancho, color_a, color_b):
    """El toldo a rayas de un puesto: cada franja con luz arriba y un borde festoneado con sombra."""
    for i, px in enumerate(range(x, x + ancho, 12)):
        color = color_a if i % 2 == 0 else color_b
        franja = min(12, x + ancho - px)
        for py in range(60, 67):
            for qx in range(px, px + franja):
                v = 0.78 - (py - 60) * 0.07 - ((qx - px) / franja) * 0.1
                sup.set_at((qx, py), _elegir(_rampa(color), v, qx, py))
        pygame.draw.ellipse(sup, _tono(color, -0.05), (px, 63, franja, 9))            # festón: media luna abajo
        pygame.draw.arc(sup, CONTORNO, (px, 63, franja, 9), math.pi, 2 * math.pi, 1)
        for qx in range(px + 2, px + franja - 2):
            sup.set_at((qx, 70), _tono(color, -0.3))                                   # sombra de la curva
    pygame.draw.line(sup, (110, 74, 48), (x, 59), (x + ancho - 1, 59))
    for qx in range(x + 2, x + ancho - 1, 3):                                         # sombra que el toldo tira abajo
        if (qx // 3) % 2 == 0:
            sup.set_at((qx, 73), (140, 60, 56))
            sup.set_at((qx + 1, 74), (140, 60, 56))


def _gema(sup, gx, base, color):
    """Un cristal facetado sobre el mostrador (caras claras y oscuras, brillo)."""
    pts = [(gx, base), (gx + 1, base - 5), (gx + 4, base - 7), (gx + 7, base - 5), (gx + 8, base)]
    pygame.draw.polygon(sup, _tono(color, -0.1), pts)
    pygame.draw.polygon(sup, _tono(color, 0.45), [(gx + 1, base - 5), (gx + 4, base - 7), (gx + 4, base)])
    pygame.draw.polygon(sup, _tono(color, -0.45), [(gx + 4, base - 7), (gx + 7, base - 5), (gx + 8, base), (gx + 4, base)])
    pygame.draw.polygon(sup, CONTORNO, pts, 1)
    sup.set_at((gx + 3, base - 5), (255, 255, 255))


def mercaderia_cristales(sup, x, y):
    """Cristales de colores a los costados del mostrador (en el medio queda lugar para quien atiende)."""
    for gx, color in ((x + 6, (110, 230, 245)), (x + 17, (250, 190, 70)), (x + 49, (190, 120, 240)),
                      (x + 60, (110, 230, 245))):
        _gema(sup, gx, y, color)


def mercaderia_frutas(sup, x, y):
    """Dos montoncitos de frutas esféricas con brillo, a los costados."""
    colores = ((230, 70, 90), (90, 150, 240), (250, 190, 70), (130, 210, 110), (190, 120, 240))
    for base_x in (x + 7, x + 46):
        for k in range(4):
            esfera(sup, base_x + k * 6, y - 4 - (k % 2), 3, _rampa(colores[(k + base_x) % 5]))
        for k in range(3):
            esfera(sup, base_x + 3 + k * 6, y - 1, 3, _rampa(colores[(k * 2 + base_x + 1) % 5]))
    sup.set_at((x + 14, y - 8), (255, 255, 255))


def mercaderia_repuestos(sup, x, y):
    """Repuestos y chatarra de nave: un casco, un engranaje, un caño doblado y una cajita."""
    esfera(sup, x + 12, y - 6, 6, [(60, 64, 92), (100, 106, 136), (150, 156, 184), (208, 212, 232)])
    pygame.draw.rect(sup, (18, 26, 70), (x + 13, y - 9, 6, 4))
    pygame.draw.line(sup, (120, 170, 255), (x + 14, y - 9), (x + 16, y - 9))
    cx, cy = x + 34, y - 5
    for k in range(8):                                                                # engranaje
        ang = k * math.pi / 4
        pygame.draw.rect(sup, (170, 176, 200), (cx + round(5 * math.cos(ang)) - 1, cy + round(5 * math.sin(ang)) - 1, 2, 2))
    pygame.draw.circle(sup, (150, 156, 182), (cx, cy), 4)
    pygame.draw.circle(sup, (222, 226, 242), (cx - 1, cy - 1), 2)
    pygame.draw.circle(sup, (40, 36, 52), (cx, cy), 1)
    pygame.draw.lines(sup, CONTORNO, False, [(x + 46, y - 1), (x + 46, y - 8), (x + 55, y - 8)], 4)       # caño
    pygame.draw.lines(sup, (176, 182, 206), False, [(x + 46, y - 1), (x + 46, y - 8), (x + 55, y - 8)], 2)
    _caja_sombreada(sup, (x + 59, y - 7, 9, 7), (150, 104, 60))
    pygame.draw.rect(sup, CONTORNO, (x + 59, y - 7, 9, 7), 1)


def mercaderia_carniceria(sup, x, y):
    """
    Una carnicería: una barra con ganchos de la que cuelgan un jamón, chorizos y un costillar, y sobre el
    mostrador unos bifes, una tabla de cortar con un hacha de carnicero y una bandeja de salchichas.
    """
    # Barra de metal con ganchos (debajo del toldo)
    pygame.draw.rect(sup, CONTORNO, (x + 4, 75, ANCHO_PUESTO - 8, 3))
    pygame.draw.line(sup, (190, 196, 214), (x + 5, 76), (x + ANCHO_PUESTO - 6, 76))

    def gancho(gx, largo):
        pygame.draw.line(sup, (176, 182, 204), (gx, 77), (gx, 77 + largo))
        pygame.draw.line(sup, (176, 182, 204), (gx, 77 + largo), (gx + 2, 78 + largo))
        sup.set_at((gx + 2, 77 + largo), (176, 182, 204))

    # 1) un jamón
    gancho(x + 12, 3)
    esfera(sup, x + 12, 87, 6, [(96, 34, 44), (156, 58, 62), (214, 98, 96), (244, 160, 150)])
    pygame.draw.rect(sup, (236, 232, 216), (x + 11, 81, 3, 2))                            # el hueso
    pygame.draw.circle(sup, CONTORNO, (x + 12, 87), 6, 1)
    pygame.draw.line(sup, (244, 214, 190), (x + 8, 89), (x + 14, 91))                     # vetita de grasa
    # 2) una tira de chorizos
    gancho(x + 21, 2)
    for k in range(2):
        cy = 81 + k * 5
        pygame.draw.ellipse(sup, CONTORNO, (x + 17, cy - 1, 9, 6))
        pygame.draw.ellipse(sup, (166, 58, 46), (x + 18, cy, 7, 4))
        pygame.draw.line(sup, (226, 130, 100), (x + 19, cy + 1), (x + 22, cy + 1))
        pygame.draw.line(sup, (96, 80, 60), (x + 21, cy + 4), (x + 21, cy + 5))        # el piolín
    # 3) un costillar (a la derecha: en el medio queda lugar para quien atiende)
    gancho(x + 57, 3)
    pygame.draw.polygon(sup, CONTORNO, [(x + 51, 81), (x + 64, 81), (x + 66, 93), (x + 50, 93)])
    pygame.draw.polygon(sup, (214, 102, 100), [(x + 52, 82), (x + 63, 82), (x + 64, 92), (x + 52, 92)])
    for ry in (84, 87, 90):
        pygame.draw.line(sup, (246, 232, 214), (x + 53, ry), (x + 63, ry))
    pygame.draw.line(sup, (150, 56, 62), (x + 52, 92), (x + 64, 92))
    # Sobre el mostrador: tres bifes (el último, violeta: un corte de Kepler-7)
    for bx, by, col in ((x + 3, y - 3, (204, 80, 86)), (x + 11, y - 2, (228, 110, 108)), (x + 19, y - 3, (140, 96, 196))):
        pygame.draw.ellipse(sup, CONTORNO, (bx, by - 3, 9, 6))
        pygame.draw.ellipse(sup, col, (bx + 1, by - 2, 7, 4))
        pygame.draw.line(sup, (250, 222, 204) if col[0] > 200 else (214, 190, 244), (bx + 2, by - 1), (bx + 5, by))
    # Tabla de cortar con el hacha
    _caja_sombreada(sup, (x + 30, y - 4, 20, 4), (216, 176, 120))
    pygame.draw.rect(sup, CONTORNO, (x + 30, y - 4, 20, 4), 1)
    # Bandeja de salchichas
    _caja_sombreada(sup, (x + 53, y - 5, 15, 5), (232, 236, 244))
    pygame.draw.rect(sup, CONTORNO, (x + 53, y - 5, 15, 5), 1)
    for k in range(3):
        pygame.draw.line(sup, (190, 90, 74), (x + 55, y - 4 + k), (x + 66, y - 4 + k))
    sup.set_at((x + 56, y - 4), (240, 170, 140))


def puesto(sup, x, color_a, color_b, mercaderia):
    """
    Un puesto del mercado: palos, mostrador de tablones con la mercadería y toldo a rayas.
    Todos los puestos miden lo mismo (ANCHO_PUESTO). 'x' es el borde izquierdo; 'mercaderia' es una de las
    funciones mercaderia_*.
    """
    w = ANCHO_PUESTO
    for px in (x + 1, x + w - 4):                                                      # palos del toldo
        _madera(sup, (px, 62, 3, 36), (110, 74, 48), horizontal=False)
    _madera(sup, (x, Y_MOSTRADOR + 5, w, ALTO_MOSTRADOR - 5), (122, 78, 52), tablones=w // 18)
    pygame.draw.rect(sup, (60, 36, 30), (x, Y_MOSTRADOR + ALTO_MOSTRADOR - 3, w, 3))
    for py in range(Y_MOSTRADOR, Y_MOSTRADOR + 5):                                     # tapa del mostrador
        for px in range(x - 1, x + w + 1):
            sup.set_at((px, py), _elegir(_rampa((176, 120, 76)), 0.85 - (py - Y_MOSTRADOR) * 0.16, px, py, tramar=False))
    pygame.draw.line(sup, (240, 190, 130), (x - 1, Y_MOSTRADOR), (x + w, Y_MOSTRADOR))
    pygame.draw.rect(sup, CONTORNO, (x - 1, Y_MOSTRADOR, w + 2, ALTO_MOSTRADOR), 1)
    mercaderia(sup, x, Y_MOSTRADOR)
    _toldo(sup, x, w, color_a, color_b)


def carpa(sup, x, base_y, ancho, color):
    """Una carpa de otro puesto, a lo lejos: dos lados (uno claro y otro en sombra), rayas y banderín."""
    altura = ancho // 2 - 2
    cx = x + ancho // 2
    pico = base_y - altura
    claro, oscuro = _tono(color, 0.18), _tono(color, -0.4)
    pygame.draw.polygon(sup, claro, [(x, base_y), (cx, pico), (cx, base_y)])
    pygame.draw.polygon(sup, oscuro, [(cx, base_y), (cx, pico), (x + ancho, base_y)])
    for k in range(1, 4):                                                          # rayas de tela
        t = k / 4
        pygame.draw.line(sup, _tono(color, 0.45), (x + int(t * ancho / 2), base_y - int((1 - t) * 0)), (cx, pico))
    pygame.draw.line(sup, _tono(color, 0.5), (x, base_y), (cx, pico))
    pygame.draw.polygon(sup, (46, 28, 40), [(x + 4, base_y), (x + ancho - 4, base_y), (x + ancho - 4, base_y + 8), (x + 4, base_y + 8)])
    pygame.draw.rect(sup, (86, 56, 56), (x + 4, base_y, ancho - 8, 2))
    pygame.draw.line(sup, (120, 84, 60), (cx, pico - 5), (cx, pico))
    pygame.draw.polygon(sup, (250, 210, 80), [(cx, pico - 5), (cx + 5, pico - 4), (cx, pico - 2)])


# ---------------------------------------------------------------------- #
#  Transbordador espacial (en vuelo y estrellado)
# ---------------------------------------------------------------------- #

def _medidas_fuselaje(u, H):
    """Cuánto sube y cuánto baja el fuselaje respecto de su eje en la posición u (0 = cola, 1 = punta)."""
    arriba = abajo = 0.5 * H
    if u < 0.08:                                    # el fondo de la cola se afina un poco
        arriba = abajo = 0.5 * H * (0.78 + 0.22 * u / 0.08)
    if 0.66 < u < 0.86:                             # el techo de la cabina sobresale
        arriba += 0.10 * H * math.sin((u - 0.66) / 0.20 * math.pi)
    if u > 0.84:                                    # la nariz se afina hacia abajo
        s = 1 - (u - 0.84) / 0.16
        arriba = 0.5 * H * s ** 0.8 - 0.18 * H * (1 - s)
        abajo = 0.5 * H * s ** 0.6
    return arriba, abajo


def transbordador(sup, x, y, largo, alto, estrellado=False, inclinacion=0.0):
    """
    Un transbordador espacial visto de costado, con la nariz a la derecha: fuselaje blanco, panza y nariz
    negras (placas térmicas), cabina con ventanas, cola con aleta, ala delta y tres toberas.
    (x, y) es la esquina de arriba a la izquierda de la zona que ocupa el fuselaje con su cola y su ala.
    Con 'estrellado' tiene la aleta y el ala rotas, quemaduras, ventanas rajadas y un agujero con cables.
    'inclinacion' baja la nariz (en píxeles de diferencia entre la cola y la punta).
    """
    L, H = largo, alto
    cy = y + int(1.35 * H)                                   # eje del fuselaje (arriba queda lugar para la aleta)

    def eje(u):
        return cy + inclinacion * (u - 0.5)

    ancho = int(L) + 8
    gran = int(H * 3.6) + 4

    # --- Ala delta, detrás del fuselaje (se ve por debajo) ---
    punta_x = 0.10 if not estrellado else 0.22
    ala = [(x + 0.62 * L, eje(0.62) + 0.40 * H), (x + punta_x * L, eje(punta_x) + 1.05 * H),
           (x + 0.16 * L, eje(0.16) + 0.40 * H)]
    if estrellado:                                           # el ala se quebró: la punta quedó rota y dentada
        ala = [(x + 0.62 * L, eje(0.62) + 0.40 * H), (x + 0.30 * L, eje(0.30) + 0.78 * H),
               (x + 0.27 * L, eje(0.27) + 0.66 * H), (x + 0.22 * L, eje(0.22) + 0.86 * H),
               (x + 0.18 * L, eje(0.18) + 0.62 * H), (x + 0.16 * L, eje(0.16) + 0.40 * H)]
    pygame.draw.polygon(sup, (196, 200, 222), ala)
    pygame.draw.line(sup, (20, 18, 30), ala[0], ala[1], 2)                      # borde de ataque negro
    pygame.draw.line(sup, (236, 240, 252), (ala[0][0] - 2, ala[0][1] - 1), (ala[-1][0] + 2, ala[-1][1] - 1))
    pygame.draw.polygon(sup, CONTORNO, ala, 1)
    if estrellado:
        pygame.draw.line(sup, (30, 26, 38), ala[2], ala[3])                     # el metal roto queda oscuro

    # --- Aleta de cola ---
    arriba_cola, _ = _medidas_fuselaje(0.15, H)
    base_y = eje(0.15) - arriba_cola
    if not estrellado:
        aleta = [(x + 0.27 * L, base_y + 1), (x + 0.03 * L, base_y + 1), (x + 0.10 * L, base_y - 1.05 * H)]
    else:                                                    # aleta quebrada, solo queda un muñón dentado
        aleta = [(x + 0.27 * L, base_y + 1), (x + 0.03 * L, base_y + 1), (x + 0.05 * L, base_y - 0.30 * H),
                 (x + 0.10 * L, base_y - 0.18 * H), (x + 0.13 * L, base_y - 0.45 * H), (x + 0.19 * L, base_y - 0.22 * H)]
    pygame.draw.polygon(sup, (226, 230, 244), aleta)
    pygame.draw.polygon(sup, (160, 166, 194), aleta[:2] + [aleta[2]])                  # el lado en sombra
    if not estrellado:
        pygame.draw.polygon(sup, (60, 90, 190), [(x + 0.085 * L, base_y - 0.65 * H), (x + 0.115 * L, base_y - 0.65 * H),
                                                  (x + 0.14 * L, base_y - 0.18 * H), (x + 0.065 * L, base_y - 0.18 * H)])
    pygame.draw.polygon(sup, CONTORNO, aleta, 1)

    # --- Fuselaje: por columnas, de luz arriba a sombra abajo; panza y nariz de placas negras ---
    puntos_arriba, puntos_abajo = [], []
    casco = set()
    blanco = [(250, 252, 255), (228, 232, 244), (196, 202, 222), (160, 168, 196)]
    negro = [(70, 72, 92), (44, 46, 64), (26, 26, 40)]
    for px in range(int(L)):
        u = px / L
        arriba, abajo = _medidas_fuselaje(u, H)
        top = int(round(eje(u) - arriba))
        bot = int(round(eje(u) + abajo))
        puntos_arriba.append((x + px, top))
        puntos_abajo.append((x + px, bot))
        for py in range(top, bot + 1):
            t = (py - top) / max(1, bot - top)
            casco.add((x + px, py))
            if u > 0.90 or t > 0.62 + (0.06 * (_umbral(px, py) - 0.5)):          # nariz y panza: placas térmicas negras
                color = _elegir(negro, 1.0 - t * 0.9 - 0.1 * (u > 0.9), px, py, tramar=False)
                if px % 5 == 0 or py % 4 == 0:
                    color = _tono(color, 0.18)                                      # junturas entre placas
            else:
                color = _elegir(blanco[::-1], 1.0 - t / 0.62 * 0.85, px, py, tramar=False)
            sup.set_at((x + px, py), color)

    # Bodega de carga: línea de las puertas con marcas
    for px in range(int(0.20 * L), int(0.64 * L)):
        py = int(round(eje(px / L) - 0.5 * H + 0.20 * H))
        sup.set_at((x + px, py), (150, 156, 184))
        if px % 6 == 0:
            sup.set_at((x + px, py + 1), (110, 116, 150))
    # Franja azul
    for px in range(int(0.30 * L), int(0.33 * L)):
        arriba, abajo = _medidas_fuselaje(px / L, H)
        for py in range(int(round(eje(px / L) - arriba)) + 1, int(round(eje(px / L) + 0.12 * H))):
            sup.set_at((x + px, py), (70, 100, 200))

    # Cabina: tres ventanas
    for k in range(3):
        ux = 0.745 + k * 0.045
        px = x + int(ux * L)
        py = int(round(eje(ux) - 0.5 * H + 0.12 * H))
        pygame.draw.rect(sup, (22, 34, 88), (px, py, max(2, int(0.035 * L)), max(2, int(0.18 * H))))
        sup.set_at((px, py), (150, 200, 255))
        if estrellado and k == 1:
            pygame.draw.line(sup, (240, 246, 255), (px, py), (px + 2, py + max(2, int(0.18 * H)) - 1))
        if estrellado and k == 2:
            pygame.draw.rect(sup, (8, 6, 14), (px, py, max(2, int(0.035 * L)), max(2, int(0.18 * H))))

    # Contorno oscuro del fuselaje
    pygame.draw.lines(sup, CONTORNO, False, puntos_arriba, 1)
    pygame.draw.lines(sup, CONTORNO, False, puntos_abajo, 1)
    pygame.draw.line(sup, CONTORNO, puntos_arriba[0], puntos_abajo[0])
    pygame.draw.line(sup, CONTORNO, puntos_arriba[-1], puntos_abajo[-1])

    # --- Toberas en la cola ---
    for k in range(3):
        ty = int(round(eje(0.0) + (k - 1) * 0.28 * H))
        n = max(1, round(H / 12))                                  # las toberas crecen con la nave
        pygame.draw.rect(sup, CONTORNO, (x - 4 * n, ty - 2 * n, 5 * n, 5 * n))
        pygame.draw.rect(sup, (120, 124, 150), (x - 3 * n, ty - n, 3 * n, 3 * n))
        pygame.draw.rect(sup, (210, 214, 232), (x - 3 * n, ty - n, n, n))

    if estrellado:
        # Quemaduras: manchas de hollín tramadas
        for u, v, r in ((0.10, 0.45, 5), (0.52, 0.10, 5), (0.86, 0.40, 6), (0.30, 0.85, 5)):
            r = max(4, int(r * L / 90))
            ccx, ccy = x + u * L, eje(u) + (v - 0.5) * H
            for py in range(int(ccy - r), int(ccy + r) + 1):
                for px in range(int(ccx - r), int(ccx + r) + 1):
                    d = math.hypot(px - ccx, py - ccy) / r
                    if d < 1 and (1 - d) * 1.1 > _umbral(px, py) and (px, py) in casco and 0 <= px < sup.get_width() and 0 <= py < sup.get_height():
                        c = sup.get_at((px, py))
                        sup.set_at((px, py), _mezclar((c.r, c.g, c.b), (40, 34, 46), 0.72))
        # Agujero en el costado con cables y chispas
        hx, hy = x + int(0.50 * L), int(round(eje(0.5) + 0.10 * H))
        pygame.draw.polygon(sup, (18, 14, 24), [(hx, hy), (hx + 7, hy - 2), (hx + 9, hy + 4), (hx + 3, hy + 6)])
        for dx, dy, c in ((2, 1, (240, 200, 60)), (5, 0, (230, 60, 60)), (6, 3, (90, 200, 240)), (3, 4, (240, 200, 60))):
            sup.set_at((hx + dx, hy + dy), c)
        # Grietas en la nariz
        px0 = x + int(0.92 * L)
        pygame.draw.line(sup, (200, 204, 224), (px0, int(round(eje(0.92))) + 1), (px0 + 4, int(round(eje(0.97))) + 3))
        pygame.draw.line(sup, (200, 204, 224), (px0 + 2, int(round(eje(0.94))) - 1), (px0 + 3, int(round(eje(0.94))) + 2))


def transbordador_vuelo():
    """El transbordador de la animación de la caída: una imagen con transparencia, mirando a la derecha."""
    L, H = 160, 28
    sup = pygame.Surface((L + 18, int(H * 3.6) + 10), pygame.SRCALPHA)
    transbordador(sup, 14, 4, L, H)
    return sup


L_NAVE, H_NAVE = 224, 39         # largo y alto del fuselaje de la nave estrellada (la astronauta mide 32)


def nave_estrellada(sup, rect):
    """
    La nave estrellada del sitio del choque: el mismo transbordador de la caída, con la nariz clavada en la
    tierra. Mira hacia la IZQUIERDA (hacia donde venía cayendo en la animación) y tiene la cola a la derecha.
    El humo no está acá: se dibuja aparte con humo_animado, para que se mueva.
    """
    x, y, w, h = rect
    ancho_lienzo = sup.get_width()
    for py in range(y + h - 7, y + h + 4):                       # sombra en el piso, con trama
        for px in range(x - 4, x + w + 6):
            if ((px - (x + w / 2)) / (w / 2 + 6)) ** 2 + ((py - (y + h - 2)) / 6.0) ** 2 < 1 and _umbral(px, py) < 0.65:
                sup.set_at((px, py), (104, 42, 48))
    # El transbordador se dibuja mirando a la derecha en una capa aparte, y después se da vuelta
    der = ancho_lienzo - (x + w)                                  # el margen derecho: en la capa, el rectángulo empieza ahí
    capa = pygame.Surface(sup.get_size(), pygame.SRCALPHA)
    xr = der + 6
    transbordador(capa, xr, y + 6, L_NAVE, H_NAVE, estrellado=True, inclinacion=22.0)
    nariz = xr + L_NAVE
    for py in range(y + h - 26, y + h + 2):                       # tierra levantada alrededor de la nariz
        for px in range(nariz - 40, nariz + 10):
            d = math.hypot((px - (nariz - 6)) / 34, (py - (y + h - 8)) / 16)
            if d < 1 and (1 - d) * 1.5 > _umbral(px, py):
                capa.set_at((px, py), (196, 98, 64) if (px + py) % 3 else (150, 66, 52))
    for dx, dy, ancho in ((24, h - 9, 12), (70, h - 5, 6), (190, h - 8, 9)):     # pedazos del ala y placas térmicas
        pygame.draw.rect(capa, (24, 24, 36), (xr + dx, y + dy, ancho, 2))
        pygame.draw.line(capa, (90, 92, 116), (xr + dx, y + dy), (xr + dx + ancho - 1, y + dy))
    sup.blit(pygame.transform.flip(capa, True, False), (0, 0))


# ---------------------------------------------------------------------- #
#  Caja negra de emergencia (naranja)
# ---------------------------------------------------------------------- #

def caja_negra(sup, rect, abierta=False):
    """
    La caja negra de emergencia: una caja naranja (para encontrarla entre los restos), con banda reflectante,
    etiqueta y asa. Abierta, la tapa queda levantada y se ve el interior oscuro.
    """
    x, y, w, h = rect
    naranja = (246, 116, 24)
    rampa = _rampa(naranja)
    cuerpo = pygame.Rect(x, y + 5, w, h - 5)
    if abierta:                                                                  # el revés de la tapa, levantada
        tapa = [(x + 1, y + 5), (x + 3, y - 3), (x + w - 2, y - 3), (x + w - 1, y + 5)]
        pygame.draw.polygon(sup, (150, 58, 18), tapa)
        pygame.draw.line(sup, (214, 96, 30), (x + 3, y - 2), (x + w - 3, y - 2))
        pygame.draw.polygon(sup, CONTORNO, tapa, 1)
    pygame.draw.rect(sup, CONTORNO, cuerpo.inflate(2, 2))
    for py in range(cuerpo.y, cuerpo.bottom):
        for px in range(cuerpo.x, cuerpo.right):
            v = 0.86 - (py - cuerpo.y) / max(1, cuerpo.h - 1) * 0.5 - (px - x) / w * 0.18
            sup.set_at((px, py), _elegir(rampa, v, px, py, tramar=False))
    for px in range(x + 3, x + w - 3):                                          # junta de la tapa
        sup.set_at((px, y + 7), _tono(naranja, -0.45))
    # Banda reflectante con rayas
    for px in range(x + 3, x + 7):
        for py in range(y + 8, y + h - 1):
            sup.set_at((px, py), (240, 242, 250) if (py // 2) % 2 == 0 else (34, 30, 44))
    # Etiqueta blanca con rayitas de texto
    pygame.draw.rect(sup, (244, 246, 252), (x + 9, y + 9, 8, 4))
    for px in range(x + 10, x + 16, 2):
        sup.set_at((px, y + 10), (40, 36, 52))
        sup.set_at((px, y + 12), (40, 36, 52))
    # Tornillos y brillo
    for px, py in ((x + 1, y + 6), (x + w - 2, y + 6), (x + 1, y + h - 2), (x + w - 2, y + h - 2)):
        sup.set_at((px, py), (232, 234, 248))
    if abierta:
        pygame.draw.rect(sup, (26, 14, 10), (x + 2, y + 5, w - 4, 3))            # interior
    else:
        pygame.draw.rect(sup, CONTORNO, (x + 6, y + 3, 8, 3))                    # asa
        pygame.draw.rect(sup, (86, 80, 100), (x + 7, y + 4, 6, 1))
        for px in range(x + 1, x + w - 1):
            sup.set_at((px, y + 5), _tono(naranja, 0.45))                        # reborde de luz arriba


# ---------------------------------------------------------------------- #
#  Cosas del interior de la nave
# ---------------------------------------------------------------------- #

def asiento(sup, x, y, w=28, h=40):
    """Un asiento de la cabina visto de frente: respaldo y apoyacabezas acolchados, arnés y base con rieles."""
    azul = (52, 78, 156)
    _caja_sombreada(sup, (x + 1, y + h - 5, w - 2, 5), (96, 100, 126))                 # rieles
    pygame.draw.rect(sup, CONTORNO, (x + 1, y + h - 5, w - 2, 5), 1)
    for px in (x + 1, x + w - 3):                                                       # estructura de los costados
        _caja_sombreada(sup, (px, y + 12, 2, h - 17), (120, 124, 150))
    respaldo = pygame.Rect(x + 3, y + 10, w - 6, h - 20)
    pygame.draw.rect(sup, CONTORNO, respaldo.inflate(2, 2))
    _caja_sombreada(sup, respaldo, azul)
    apoya = pygame.Rect(x + 7, y, w - 14, 11)
    pygame.draw.rect(sup, CONTORNO, apoya.inflate(2, 2))
    _caja_sombreada(sup, apoya, _tono(azul, 0.08))
    for py in (y + h // 2 - 2, y + h // 2 + 4):                                         # costuras del acolchado
        pygame.draw.line(sup, _tono(azul, -0.4), (x + 5, py), (x + w - 6, py))
    cojin = pygame.Rect(x + 2, y + h - 13, w - 4, 8)
    pygame.draw.rect(sup, CONTORNO, cojin.inflate(2, 2))
    _caja_sombreada(sup, cojin, _tono(azul, 0.12))
    for px in (x + 9, x + w - 11):                                                      # arnés
        pygame.draw.rect(sup, (222, 74, 52), (px, y + 11, 2, h - 26))
        pygame.draw.line(sup, (255, 150, 110), (px, y + 11), (px, y + h - 16))
    pygame.draw.rect(sup, (240, 204, 60), (x + w // 2 - 2, y + h - 19, 4, 4))            # hebilla
    pygame.draw.rect(sup, CONTORNO, (x + w // 2 - 2, y + h - 19, 4, 4), 1)


def casilleros(sup, x, y, columnas, filas, ancho=20, alto=24, deformado=None):
    """Una pared de casilleros metálicos con rejillas, manijas y etiquetas de colores."""
    total = pygame.Rect(x - 2, y - 2, columnas * (ancho + 2) + 2, filas * (alto + 2) + 2)
    pygame.draw.rect(sup, CONTORNO, total)
    etiquetas = ((230, 80, 80), (240, 200, 70), (90, 200, 240), (120, 220, 130), (200, 130, 240), (250, 150, 60))
    for f in range(filas):
        for c in range(columnas):
            px, py = x + c * (ancho + 2), y + f * (alto + 2)
            color = (112, 122, 152) if (c, f) != deformado else (96, 98, 122)
            _caja_sombreada(sup, (px, py, ancho, alto), color)
            for k in range(3):                                                            # rejilla de ventilación
                pygame.draw.line(sup, _tono(color, -0.45), (px + 3, py + 3 + k * 2), (px + ancho - 4, py + 3 + k * 2))
                pygame.draw.line(sup, _tono(color, 0.3), (px + 3, py + 4 + k * 2), (px + ancho - 4, py + 4 + k * 2))
            pygame.draw.rect(sup, (214, 218, 236), (px + ancho - 5, py + alto // 2, 2, 5))   # manija
            pygame.draw.rect(sup, etiquetas[(c + f * columnas) % len(etiquetas)], (px + 3, py + alto - 8, 6, 4))
            if (c, f) == deformado:                                                       # puerta abollada
                pygame.draw.line(sup, (46, 48, 70), (px + 4, py + alto - 3), (px + ancho - 3, py + 11))
                pygame.draw.line(sup, (156, 160, 186), (px + 5, py + alto - 3), (px + ancho - 2, py + 12))


def botiquin(sup, x, y):
    """Un botiquín de pared: caja blanca con cruz roja."""
    _caja_sombreada(sup, (x, y, 16, 16), (234, 238, 246))
    pygame.draw.rect(sup, CONTORNO, (x, y, 16, 16), 1)
    pygame.draw.rect(sup, (214, 40, 52), (x + 6, y + 3, 4, 10))
    pygame.draw.rect(sup, (214, 40, 52), (x + 3, y + 6, 10, 4))
    pygame.draw.line(sup, (255, 130, 120), (x + 6, y + 3), (x + 9, y + 3))
    pygame.draw.rect(sup, (150, 154, 176), (x + 7, y + 14, 2, 1))


def extintor(sup, x, y):
    """Un extintor rojo con válvula negra, manija, manguera y etiqueta."""
    rampa = [(110, 20, 32), (170, 32, 44), (222, 56, 62), (250, 120, 108)]
    for py in range(y + 7, y + 30):
        for px in range(x, x + 9):
            sup.set_at((px, py), _elegir(rampa, 1.0 - abs((px - x) / 8 - 0.28) * 1.25, px, py, tramar=False))
    pygame.draw.rect(sup, CONTORNO, (x - 1, y + 6, 11, 25), 1)
    pygame.draw.rect(sup, (30, 28, 40), (x + 2, y + 2, 5, 6))                            # válvula
    pygame.draw.rect(sup, (150, 154, 176), (x + 5, y, 7, 2))                             # manija
    pygame.draw.line(sup, (30, 28, 40), (x + 7, y + 4), (x + 12, y + 10))                # manguera
    pygame.draw.line(sup, (30, 28, 40), (x + 12, y + 10), (x + 12, y + 18))
    pygame.draw.rect(sup, (244, 246, 252), (x + 1, y + 14, 7, 7))                        # etiqueta
    for py in (y + 16, y + 18):
        pygame.draw.line(sup, (40, 36, 52), (x + 2, py), (x + 6, py))


def mate(sup, x, y):
    """Un termo plateado y un mate con bombilla."""
    _caja_sombreada(sup, (x, y + 1, 6, 12), (176, 182, 204))
    pygame.draw.rect(sup, CONTORNO, (x, y + 1, 6, 12), 1)
    pygame.draw.rect(sup, (36, 34, 48), (x, y - 1, 6, 3))
    pygame.draw.rect(sup, (120, 78, 48), (x + 8, y + 6, 8, 7))                           # el mate
    pygame.draw.rect(sup, (170, 116, 70), (x + 8, y + 6, 8, 2))
    pygame.draw.rect(sup, (80, 52, 34), (x + 9, y + 11, 6, 2))
    pygame.draw.rect(sup, CONTORNO, (x + 8, y + 6, 8, 7), 1)
    pygame.draw.line(sup, (214, 218, 236), (x + 12, y + 6), (x + 14, y + 0))             # bombilla


def foto(sup, x, y):
    """Una foto pegada en la pared: un atardecer y la silueta de un gato."""
    pygame.draw.rect(sup, (244, 238, 220), (x, y, 14, 12))
    pygame.draw.rect(sup, CONTORNO, (x, y, 14, 12), 1)
    for py in range(y + 2, y + 10):
        t = (py - y - 2) / 7
        pygame.draw.line(sup, _mezclar((60, 50, 120), (244, 150, 96), t), (x + 2, py), (x + 11, py))
    pygame.draw.ellipse(sup, (20, 16, 28), (x + 4, y + 6, 6, 4))                         # cuerpo del gato
    pygame.draw.polygon(sup, (20, 16, 28), [(x + 4, y + 6), (x + 5, y + 4), (x + 6, y + 6)])
    pygame.draw.polygon(sup, (20, 16, 28), [(x + 7, y + 6), (x + 8, y + 4), (x + 9, y + 6)])
    pygame.draw.circle(sup, (230, 60, 60), (x + 7, y + 1), 1)                            # la chinche


CABLES = ((0, 22, (230, 70, 70)), (5, 30, (240, 200, 70)), (10, 16, (90, 170, 240)))     # (corrimiento, largo, color)


def puntas_cables(x, y):
    """Dónde terminan (las puntas peladas) los cables que dibuja cables(x, y)."""
    return [(x + dx + int(2 * math.sin((largo - 1) / 5.0 + dx)), y + largo - 1) for dx, largo, _ in CABLES]


def cables(sup, x, y):
    """Tres cables que cuelgan del techo, con las puntas peladas."""
    for dx, largo, color in CABLES:
        puntos = [(x + dx + int(2 * math.sin(i / 5.0 + dx)), y + i) for i in range(largo)]
        pygame.draw.lines(sup, CONTORNO, False, [(px + 1, py) for px, py in puntos], 1)
        pygame.draw.lines(sup, color, False, puntos, 1)
        sup.set_at(puntos[-1], (240, 160, 60))                                           # el cobre
        sup.set_at((puntos[-1][0], puntos[-1][1] + 1), (255, 220, 120))


# ---------------------------------------------------------------------- #
#  Humo animado, cartel de peligro, mercado y cabina de la nave
# ---------------------------------------------------------------------- #

RECT_NAVE = (6, 24, 240, 92)          # dónde se dibuja la nave estrellada del sitio del choque (ocupa casi toda la pantalla)
RECT_CLIC_NAVE = (12, 26, 234, 78)    # la zona donde se le puede hacer clic (no baja hasta el piso, para poder caminar)
ORIGEN_HUMO_NAVE = (71, 63)           # de dónde sale el humo (la cabina de la nave estrellada)


def disco_tramado(sup, cx, cy, radio, color, hueco=0.0):
    """Un disco de píxeles enteros. 'hueco' (0 a 1) es la fracción de puntitos que se dejan sin pintar (trama)."""
    ancho, alto = sup.get_size()
    for py in range(cy - radio, cy + radio + 1):
        for px in range(cx - radio, cx + radio + 1):
            if (px - cx) ** 2 + (py - cy) ** 2 <= radio * radio and _umbral(px, py) >= hueco:
                if 0 <= px < ancho and 0 <= py < alto:
                    sup.set_at((px, py), color)


def humo_animado(sup, ox, oy, t, bolas=8, altura=40, escala=1.0):
    """
    Una columna de humo que sube, se ensancha, se aclara y se deshace en puntitos mientras el viento la
    corre. Se dibuja según el tiempo 't': cada bola está en otro momento de su vida.
    """
    ciclo = 3.2
    for i in range(bolas):
        fase = ((t / ciclo) + i / bolas) % 1.0                        # 0 = recién nacida, 1 = ya se fue
        x = ox + int((math.sin(fase * 6.0 + i * 1.7) * 3 + fase * 9) * escala)
        y = oy - int(fase * altura * escala)
        radio = int((3 + fase * 6.5) * escala)
        color = _mezclar((54, 50, 62), (150, 142, 158), min(1.0, fase * 1.2))
        disco_tramado(sup, x, y, radio, color, hueco=max(0.0, fase * 0.85 - 0.25))
        if radio >= 3:                                                  # un brillo arriba a la izquierda
            disco_tramado(sup, x - 1, y - 1, radio - 2, _tono(color, 0.28), hueco=0.4 + fase * 0.5)


def cartel_peligro(sup, rect):
    """
    Una señal de peligro clavada en el piso: triángulo amarillo con borde negro y un signo de exclamación,
    sobre un poste de metal que llega hasta el suelo (con su sombra).
    """
    x, y, w, h = rect
    cx = x + w // 2
    base = y + h + 11                                                  # donde el poste toca el piso
    for py in range(base - 1, base + 3):                               # sombra en el piso
        for px in range(cx - 8, cx + 9):
            if ((px - cx) / 8) ** 2 + ((py - base) / 2.0) ** 2 < 1 and _umbral(px, py) < 0.7:
                sup.set_at((px, py), (104, 42, 48))
    pygame.draw.rect(sup, CONTORNO, (cx - 2, y + h - 6, 5, base - (y + h - 6) + 1))      # poste
    for py in range(y + h - 5, base + 1):
        sup.set_at((cx - 1, py), (196, 200, 220))
        sup.set_at((cx, py), (142, 146, 172))
        sup.set_at((cx + 1, py), (98, 102, 130))
    pygame.draw.rect(sup, CONTORNO, (cx - 4, base - 1, 9, 2))                              # base apoyada en el suelo
    pygame.draw.line(sup, (150, 154, 180), (cx - 3, base - 1), (cx + 3, base - 1))
    alto = h - 3
    pygame.draw.polygon(sup, (22, 18, 30), [(cx, y), (x + w - 1, y + alto), (x, y + alto)])               # borde negro
    interior = [(cx, y + 4), (x + w - 5, y + alto - 2), (x + 4, y + alto - 2)]
    pygame.draw.polygon(sup, (252, 210, 44), interior)
    pygame.draw.polygon(sup, (226, 170, 30), [(cx, y + 4), (x + w - 5, y + alto - 2), (cx, y + alto - 2)])  # mitad en sombra
    pygame.draw.line(sup, (255, 238, 140), interior[0], interior[2])                                   # luz del borde izquierdo
    pygame.draw.rect(sup, (22, 18, 30), (cx - 1, y + 7, 2, 5))                                         # signo de exclamación
    pygame.draw.rect(sup, (22, 18, 30), (cx - 1, y + 13, 2, 2))
    for px, py in ((cx - 5, y + alto - 4), (cx + 5, y + alto - 4)):                                  # tornillos
        sup.set_at((px, py), (120, 90, 20))


def poste_madera(sup, x, y0, y1):
    """Un poste de madera (3 píxeles de ancho, luz a la izquierda) con una pequeña base."""
    pygame.draw.rect(sup, CONTORNO, (x - 1, y0 - 1, 5, y1 - y0 + 2))
    for py in range(y0, y1 + 1):
        sup.set_at((x, py), (176, 120, 78))
        sup.set_at((x + 1, py), (130, 84, 56))
        sup.set_at((x + 2, py), (92, 58, 42))
    pygame.draw.rect(sup, CONTORNO, (x - 2, y1 - 1, 7, 3))
    pygame.draw.line(sup, (150, 100, 66), (x - 1, y1 - 1), (x + 3, y1 - 1))


def guirnalda(sup, xs, y_poste, colores):
    """
    Una guirnalda de banderines que cuelga de una soga entre postes (xs son los x de los postes).
    La soga hace una curva y los banderines cuelgan de ella, con una mitad clara y otra en sombra.
    """
    k = 0
    for x0, x1 in zip(xs, xs[1:]):
        puntos = []
        for px in range(x0, x1 + 1):
            s = (px - x0) / (x1 - x0)
            puntos.append((px, y_poste + int(round(7 * math.sin(math.pi * s)))))
        for px, py in puntos:
            sup.set_at((px, py), (236, 200, 120))
            sup.set_at((px, py - 1), (150, 110, 70))
        for i in range(6, len(puntos) - 4, 10):                         # banderines colgando de la soga
            px, py = puntos[i]
            color = colores[k % len(colores)]
            k += 1
            pygame.draw.polygon(sup, _tono(color, 0.3), [(px, py + 1), (px + 3, py + 1), (px + 3, py + 8)])
            pygame.draw.polygon(sup, _tono(color, -0.3), [(px + 3, py + 1), (px + 6, py + 1), (px + 3, py + 8)])
            sup.set_at((px + 3, py + 8), CONTORNO)


# ---- Cabina de la nave ----

def techo(sup, ancho=320, alto=30):
    """El techo bajo de la cabina: vigas, conductos, tuberías, una rejilla de ventilación y la lámpara."""
    rampa = [(26, 28, 42), (38, 42, 60), (52, 56, 78), (70, 74, 98)]
    for py in range(alto):
        for px in range(ancho):
            sup.set_at((px, py), _elegir(rampa, py / alto * 0.9 + 0.05, px, py, tramar=False))
    for x in range(0, ancho, 40):                                                   # vigas
        _caja_sombreada(sup, (x, 0, 6, alto), (64, 68, 92))
    _caja_sombreada(sup, (0, 8, ancho, 4), (104, 108, 138))                         # conducto grande
    _caja_sombreada(sup, (0, 15, ancho, 3), (138, 82, 62))                          # tubería de cobre
    for x in range(0, ancho, 40):                                                   # abrazaderas
        pygame.draw.rect(sup, (40, 42, 58), (x - 1, 7, 8, 6))
        pygame.draw.rect(sup, (150, 154, 180), (x + 1, 8, 4, 1))
        pygame.draw.rect(sup, (40, 42, 58), (x - 1, 14, 8, 5))
    for py in range(3, 23, 3):                                                      # rejilla de ventilación
        pygame.draw.line(sup, (20, 22, 34), (246, py), (292, py))
        pygame.draw.line(sup, (90, 94, 122), (246, py + 1), (292, py + 1))
    _caja_sombreada(sup, (144, 19, 32, 7), (214, 218, 236))                        # lámpara
    pygame.draw.rect(sup, (230, 80, 70), (144, 19, 6, 7))
    pygame.draw.rect(sup, CONTORNO, (144, 19, 32, 7), 1)
    pygame.draw.line(sup, (20, 22, 34), (0, alto - 1), (ancho, alto - 1))
    pygame.draw.line(sup, (112, 116, 144), (0, alto - 2), (ancho, alto - 2))


def luces_techo(sup, t):
    """Una hilera de lucecitas en el borde del techo, con una luz que corre de un lado a otro."""
    colores = ((255, 90, 80), (255, 214, 80), (96, 234, 140), (110, 204, 255))
    for i in range(36):
        x = 14 + i * 8
        corre = (i + int(t * 5)) % 7 == 0
        base = colores[i % 4]
        color = base if corre else _tono(base, -0.7)
        pygame.draw.rect(sup, (16, 16, 26), (x - 1, 24, 5, 4))
        pygame.draw.rect(sup, color, (x, 25, 3, 2))
        if corre:
            sup.set_at((x, 25), _tono(base, 0.7))


def consola_principal(sup, x, y, t):
    """
    La consola de la cabina (54 x 40): una pantalla de radar con un haz que gira, una pantalla con
    símbolos alienígenas que se desplazan, filas de botones con luces que titilan y deslizadores.
    """
    _caja_sombreada(sup, (x, y, 54, 40), (42, 46, 68))
    pygame.draw.rect(sup, CONTORNO, (x, y, 54, 40), 1)
    # Radar
    radar = pygame.Rect(x + 3, y + 3, 22, 16)
    pygame.draw.rect(sup, (6, 26, 20), radar)
    cx, cy = radar.center
    sup.set_clip(radar)
    for r in (3, 6):
        pygame.draw.circle(sup, (24, 96, 62), (cx, cy), r, 1)
    pygame.draw.line(sup, (24, 96, 62), (radar.x, cy), (radar.right, cy))
    pygame.draw.line(sup, (24, 96, 62), (cx, radar.y), (cx, radar.bottom))
    ang = t * 2.2
    for k, color in enumerate(((50, 150, 96), (88, 210, 140), (150, 255, 190))):      # el haz y su estela
        a = ang - (2 - k) * 0.25
        pygame.draw.line(sup, color, (cx, cy), (cx + int(math.cos(a) * 9), cy + int(math.sin(a) * 9)))
    for bx, by, fase in ((-5, -3, 0.0), (4, 2, 1.3), (2, -5, 2.4)):                  # puntitos que parpadean
        if math.sin(t * 3 + fase) > 0.2:
            sup.set_at((cx + bx, cy + by), (210, 255, 220))
    sup.set_clip(None)
    pygame.draw.rect(sup, (90, 98, 130), radar, 1)
    # Pantalla de signos vitales: un electrocardiograma que se va dibujando de izquierda a derecha
    texto = pygame.Rect(x + 29, y + 3, 22, 16)
    pygame.draw.rect(sup, (8, 14, 42), texto)
    for gx in range(texto.x + 3, texto.right - 1, 4):                                    # cuadrícula
        pygame.draw.line(sup, (20, 34, 70), (gx, texto.y + 1), (gx, texto.bottom - 2))
    pygame.draw.line(sup, (20, 34, 70), (texto.x + 1, texto.centery), (texto.right - 2, texto.centery))
    onda = (0, 0, 0, -1, 0, 0, 0, 0, 3, -5, 4, 0, 0, 1, 2, 1, 0, 0, 0, 0)               # un latido
    barrido = int(t * 14) % 20
    for i in range(20):
        px = texto.x + 1 + i
        if px >= texto.right - 1:
            break
        if (barrido - i) % 20 < 14:                                                      # lo dibujado se va apagando
            sup.set_at((px, texto.centery + onda[i]), (96, 255, 150) if (barrido - i) % 20 < 3 else (46, 170, 100))
    pygame.draw.rect(sup, (90, 98, 130), texto, 1)
    # Botones con luces
    colores = ((236, 70, 62), (250, 190, 60), (88, 220, 130), (96, 200, 250))
    for fila in range(4):
        for col in range(12):
            estado = (col * 7 + fila * 3 + int(t * 2 + col * 0.3)) % 6
            if estado < 2:
                color = (36, 38, 54)
            else:
                color = colores[(col + fila) % 4] if estado < 4 else _tono(colores[(col + fila) % 4], -0.55)
            pygame.draw.rect(sup, color, (x + 3 + col * 4, y + 22 + fila * 3, 3, 2))
    # Deslizadores
    for k in range(3):
        sx = x + 4 + k * 17
        pygame.draw.line(sup, (20, 22, 34), (sx, y + 36), (sx + 12, y + 36))
        pygame.draw.rect(sup, (214, 218, 238), (sx + int((math.sin(t * 0.7 + k) + 1) * 5), y + 35, 3, 3))


def medidores(sup, x, y, t):
    """Un conjunto de tres relojes con aguja, uno con zona roja (las agujas tiemblan un poco)."""
    _caja_sombreada(sup, (x, y, 24, 28), (46, 50, 72))
    pygame.draw.rect(sup, CONTORNO, (x, y, 24, 28), 1)
    for i, (cx, cy, ang) in enumerate(((x + 7, y + 8, -0.8), (x + 17, y + 8, 0.4), (x + 12, y + 20, -0.2))):
        pygame.draw.circle(sup, (14, 16, 26), (cx, cy), 5)
        pygame.draw.circle(sup, (156, 160, 188), (cx, cy), 5, 1)
        for k in range(5):                                                               # marcas
            a = -2.5 + k * 0.55
            sup.set_at((cx + int(math.cos(a) * 4), cy + int(math.sin(a) * 4)), (220, 224, 240))
        sup.set_at((cx + 3, cy + 1), (240, 70, 70))                                      # zona roja
        sup.set_at((cx + 3, cy + 2), (240, 70, 70))
        a = ang + math.sin(t * 2.7 + i) * 0.12 - 1.2
        pygame.draw.line(sup, (250, 232, 120), (cx, cy), (cx + int(math.cos(a) * 4), cy + int(math.sin(a) * 4)))
        sup.set_at((cx, cy), (250, 250, 255))


def telemetria(sup, x, y, t):
    """Una pantalla de telemetría de 36 x 14 con barritas que suben y bajan (colores de verde a rojo)."""
    pantalla = pygame.Rect(x, y, 36, 14)
    pygame.draw.rect(sup, (8, 12, 24), pantalla)
    pygame.draw.rect(sup, (96, 104, 138), pantalla, 1)
    for i in range(9):
        alto = 1 + int((math.sin(t * 3 + i * 1.3) + 1) * 3.2 + (i % 3))
        for k in range(alto):
            color = (90, 230, 130) if k < 3 else (250, 210, 80) if k < 5 else (240, 80, 70)
            pygame.draw.rect(sup, color, (x + 3 + i * 3, y + 11 - k, 2, 1))
    pygame.draw.line(sup, (40, 60, 90), (x + 2, y + 12), (x + 33, y + 12))


_DIGITOS = {"0": "111101101101111", "3": "111001111001111", "4": "101101111001001", "7": "111001001001001"}


def reloj_digital(sup, x, y, t):
    """Un reloj digital de pared (18 x 9) con la hora de la misión: 03:47, con los dos puntos titilando."""
    _caja_sombreada(sup, (x, y, 18, 9), (36, 38, 54))
    pygame.draw.rect(sup, CONTORNO, (x, y, 18, 9), 1)
    for pos, d in ((1, "0"), (5, "3"), (10, "4"), (14, "7")):
        for i, bit in enumerate(_DIGITOS[d]):
            if bit == "1":
                sup.set_at((x + pos + i % 3, y + 2 + i // 3), (255, 96, 80))
    if int(t * 2) % 2 == 0:
        sup.set_at((x + 8, y + 3), (255, 96, 80))
        sup.set_at((x + 8, y + 5), (255, 96, 80))


def parche_mision(sup, x, y):
    """El parche de la misión, cosido en la pared: un planeta azul con aro rojo y una estrella (12 x 12)."""
    cx, cy = x + 6, y + 6
    pygame.draw.circle(sup, CONTORNO, (cx, cy), 6)
    pygame.draw.circle(sup, (204, 52, 60), (cx, cy), 5)
    pygame.draw.circle(sup, (244, 240, 230), (cx, cy), 4)
    pygame.draw.circle(sup, (40, 92, 190), (cx, cy), 3)
    sup.set_at((cx - 1, cy), (84, 176, 96))
    sup.set_at((cx, cy + 1), (84, 176, 96))
    sup.set_at((cx + 1, cy - 1), (140, 200, 250))
    sup.set_at((cx + 3, cy - 4), (255, 240, 140))


def mapa_ruta(sup, x, y):
    """Una hoja pegada con el mapa de la ruta del vuelo: una línea punteada y una cruz roja (14 x 9)."""
    pygame.draw.rect(sup, (236, 232, 214), (x, y, 14, 9))
    pygame.draw.rect(sup, CONTORNO, (x, y, 14, 9), 1)
    for k, (dx, dy) in enumerate(((2, 6), (4, 5), (6, 5), (8, 4), (10, 3))):
        sup.set_at((x + dx, y + dy), (70, 90, 170))
    sup.set_at((x + 11, y + 2), (220, 60, 60))
    sup.set_at((x + 3, y + 2), (150, 150, 150))
    sup.set_at((x + 2, y + 2), (150, 150, 150))
    sup.set_at((x - 1, y), (230, 80, 80))                                           # chincheta


def tubo_vertical(sup, x, y, alto):
    """Un caño vertical con bridas y una válvula de rueda roja."""
    _caja_sombreada(sup, (x, y, 5, alto), (118, 122, 150))
    for py in range(y + 6, y + alto - 4, 16):
        _caja_sombreada(sup, (x - 1, py, 7, 3), (150, 154, 180))
    vy = y + alto // 2
    pygame.draw.circle(sup, CONTORNO, (x + 2, vy), 5)
    pygame.draw.circle(sup, (214, 66, 60), (x + 2, vy), 4, 1)
    pygame.draw.line(sup, (214, 66, 60), (x - 2, vy), (x + 6, vy))
    pygame.draw.line(sup, (214, 66, 60), (x + 2, vy - 4), (x + 2, vy + 4))


def base_consola(sup, x, y, ancho, alto):
    """El pie de la consola: un gabinete con rejilla de ventilación y una lucecita."""
    _caja_sombreada(sup, (x, y, ancho, alto), (50, 54, 76))
    pygame.draw.rect(sup, CONTORNO, (x, y, ancho, alto), 1)
    for k in range(max(1, (alto - 3) // 3)):
        pygame.draw.line(sup, (20, 22, 34), (x + 4, y + 2 + k * 3), (x + ancho // 2, y + 2 + k * 3))
    pygame.draw.rect(sup, (96, 220, 130), (x + ancho - 8, y + 2, 3, 2))
    if alto >= 12:
        pygame.draw.rect(sup, (250, 190, 60), (x + ancho - 8, y + 8, 3, 2))


def cableado(sup, x, y0, y1, colores):
    """Un manojo de cables que bajan en paralelo por la pared, con abrazaderas cada tanto."""
    for k, color in enumerate(colores):
        for py in range(y0, y1):
            px = x + k * 2 + int(round(1.2 * math.sin(py / 9 + k)))
            sup.set_at((px, py), color)
            sup.set_at((px + 1, py), _tono(color, -0.45))
    for py in range(y0 + 8, y1, 20):
        ancho = len(colores) * 2 + 2
        pygame.draw.rect(sup, (30, 32, 46), (x - 1, py, ancho, 3))
        pygame.draw.line(sup, (150, 154, 180), (x - 1, py), (x + ancho - 2, py))


def estante_mate(sup, x, y):
    """Un estante chiquito en la pared, con el termo y el mate encima (y = donde apoyan)."""
    mate(sup, x, y - 14)
    _caja_sombreada(sup, (x - 1, y, 18, 3), (122, 126, 152))
    pygame.draw.rect(sup, CONTORNO, (x - 1, y, 18, 3), 1)
    for px in (x + 1, x + 13):
        pygame.draw.line(sup, (90, 94, 120), (px, y + 3), (px, y + 6))


# ---------------------------------------------------------------------- #
#  Pared "estación espacial": todo cubierto de equipos, bolsas y cables
# ---------------------------------------------------------------------- #

def pared_densa(sup, x0, y0, x1, y1, semilla=11):
    """
    Rellena una pared con un mosaico de equipos (paneles, cajas, bolsas de carga, conectores, rejillas, interruptores),
    con etiquetas amarillas, manijas y cintas naranjas, como el interior de una estación espacial.
    Los colores son algo apagados para que los muebles que se dibujan encima se lean bien.
    """
    import random
    azar = random.Random(semilla)
    pygame.draw.rect(sup, (30, 34, 48), (x0, y0, x1 - x0, y1 - y0))
    colores = [(88, 92, 116), (104, 108, 130), (120, 122, 140), (178, 172, 156), (150, 146, 134), (52, 78, 138), (70, 74, 96),
               (96, 70, 56)]
    x = x0
    while x < x1:
        ancho = azar.randint(14, 30)
        ancho = min(ancho, x1 - x)
        y = y0
        while y < y1:
            alto = azar.randint(9, 20)
            alto = min(alto, y1 - y)
            if alto < 5:
                break
            celda = pygame.Rect(x, y, ancho, alto)
            tipo = azar.choice(("panel", "panel", "caja", "bolsa", "conectores", "rejilla", "interruptores", "azul"))
            base = azar.choice(colores)
            if tipo == "rejilla":
                _caja_sombreada(sup, celda, (50, 54, 74))
                for gy in range(celda.y + 2, celda.bottom - 1, 2):
                    pygame.draw.line(sup, (18, 20, 30), (celda.x + 2, gy), (celda.right - 3, gy))
            elif tipo == "bolsa":
                _caja_sombreada(sup, celda, (196, 192, 180))
                pygame.draw.line(sup, (120, 116, 108), (celda.x + 2, celda.centery), (celda.right - 3, celda.centery))
                pygame.draw.line(sup, (120, 116, 108), (celda.centerx, celda.y + 1), (celda.centerx, celda.bottom - 2))
                sup.set_at((celda.centerx, celda.centery), (236, 80, 60))
            elif tipo == "conectores":
                _caja_sombreada(sup, celda, (46, 50, 70))
                for cx in range(celda.x + 3, celda.right - 2, 5):
                    for cy in range(celda.y + 3, celda.bottom - 2, 5):
                        pygame.draw.circle(sup, (14, 16, 26), (cx, cy), 2)
                        sup.set_at((cx, cy), azar.choice(((210, 90, 70), (120, 130, 160), (230, 200, 80))))
            elif tipo == "interruptores":
                _caja_sombreada(sup, celda, (62, 66, 88))
                for cx in range(celda.x + 2, celda.right - 2, 3):
                    pygame.draw.line(sup, (14, 16, 26), (cx, celda.y + 2), (cx, celda.y + 5))
                    sup.set_at((cx, celda.y + 2 + azar.randint(0, 2)), (240, 230, 220))
                    sup.set_at((cx, celda.bottom - 3), azar.choice(((96, 230, 130), (240, 80, 70), (250, 200, 70))))
            else:
                _caja_sombreada(sup, celda, (52, 78, 138) if tipo == "azul" else base)
                for rx, ry in ((celda.x + 1, celda.y + 1), (celda.right - 2, celda.y + 1),
                               (celda.x + 1, celda.bottom - 2), (celda.right - 2, celda.bottom - 2)):
                    sup.set_at((rx, ry), (214, 218, 232))
                if tipo == "caja" and ancho > 12 and alto > 10:               # asa de la caja
                    pygame.draw.rect(sup, (30, 32, 44), (celda.centerx - 3, celda.centery - 1, 6, 3), 1)
            pygame.draw.rect(sup, (20, 22, 34), celda, 1)
            if azar.random() < 0.45 and ancho > 8 and alto > 7:                 # etiqueta amarilla
                sup.set_at((celda.x + 3, celda.y + 3), (250, 210, 60))
                sup.set_at((celda.x + 4, celda.y + 3), (250, 210, 60))
                sup.set_at((celda.x + 3, celda.y + 4), (60, 50, 20))
            if azar.random() < 0.12:                                             # cinta naranja
                pygame.draw.rect(sup, (240, 130, 40), (celda.x, celda.bottom - 4, celda.w, 2))
            y += alto
        x += ancho


def cables_colgantes(sup, x0, x1, y_base, cantidad, semilla=5, caida=14):
    """Cables que cuelgan en curvas (festones) entre dos puntos de una franja, de colores variados, con enchufes en las puntas."""
    import random
    azar = random.Random(semilla)
    colores = [(236, 236, 240), (30, 32, 40), (60, 100, 200), (240, 150, 50), (230, 70, 70), (230, 220, 90), (96, 210, 130)]
    for _ in range(cantidad):
        ax = azar.randint(x0, x1 - 20)
        bx = min(x1, ax + azar.randint(18, 70))
        ay = y_base + azar.randint(-2, 6)
        by = y_base + azar.randint(-2, 8)
        sag = azar.randint(4, caida)
        color = azar.choice(colores)
        previo = None
        for i in range(0, 25):
            u = i / 24
            px = int(ax + (bx - ax) * u)
            py = int(ay + (by - ay) * u + math.sin(u * math.pi) * sag)
            if previo:
                pygame.draw.line(sup, (14, 14, 22), (previo[0], previo[1] + 1), (px, py + 1))
                pygame.draw.line(sup, color, previo, (px, py))
            previo = (px, py)
        for ex, ey in ((ax, ay), (bx, by)):                                       # conectores
            pygame.draw.rect(sup, (24, 26, 38), (ex - 1, ey - 1, 3, 3))
            sup.set_at((ex, ey), (200, 204, 220))


# ---------------------------------------------------------------------- #
#  Desastre en la cabina: la nave acaba de estrellarse
# ---------------------------------------------------------------------- #

def escombros(sup):
    """Cosas tiradas por el piso de la cabina: papeles, una placa del techo caída, un cable pelado, una caja de herramientas volcada..."""
    # Hollín alrededor del cable que echa chispas (trama de puntitos)
    for py in range(114, 136):
        for px in range(160, 200):
            d = math.hypot((px - 180) / 20, (py - 126) / 9)
            if d < 1 and (px + py) % 2 == 0:
                sup.set_at((px, py), (30, 30, 42))
    # Placa del techo caída, apoyada torcida (con el relleno aislante asomando)
    placa = [(112, 128), (146, 121), (156, 131), (122, 135)]
    pygame.draw.polygon(sup, (20, 22, 34), [(x, y + 1) for x, y in placa])
    pygame.draw.polygon(sup, (110, 114, 140), placa)
    pygame.draw.line(sup, (170, 174, 198), placa[0], placa[1])
    pygame.draw.line(sup, (72, 76, 100), placa[3], placa[2])
    pygame.draw.polygon(sup, (216, 170, 70), [(128, 127), (138, 125), (141, 129), (131, 131)])     # aislante
    for k in range(0, 8, 2):
        sup.set_at((129 + k, 129 - k // 3), (150, 108, 40))
    # Papeles sueltos
    for pts in (((38, 121), (50, 118), (53, 124), (41, 127)), ((84, 130), (95, 129), (96, 134), (85, 135)),
                ((232, 120), (243, 122), (241, 128), (230, 126)), ((262, 131), (273, 129), (275, 134), (264, 135)),
                ((196, 115), (205, 114), (206, 118), (197, 119))):
        pygame.draw.polygon(sup, (40, 42, 58), [(x, y + 1) for x, y in pts])
        pygame.draw.polygon(sup, (232, 228, 214), pts)
        for k in (1, 3):
            pygame.draw.line(sup, (150, 150, 160), (pts[0][0] + 2, pts[0][1] + k + 1), (pts[1][0] - 2, pts[1][1] + k + 1))
    # Cable arrancado en el piso, con la punta pelada
    puntos = [(212, 112), (204, 118), (198, 117), (190, 122), (184, 121), (178, 126)]
    pygame.draw.lines(sup, (14, 14, 22), False, [(x, y + 1) for x, y in puntos], 2)
    pygame.draw.lines(sup, (200, 60, 56), False, puntos, 1)
    sup.set_at((178, 126), (255, 220, 120))
    sup.set_at((177, 127), (240, 160, 60))
    # Herramientas y tornillos
    pygame.draw.line(sup, (150, 154, 178), (66, 123), (76, 128), 2)                    # llave inglesa
    pygame.draw.circle(sup, (150, 154, 178), (65, 122), 2, 1)
    pygame.draw.circle(sup, (150, 154, 178), (77, 129), 2, 1)
    for x, y in ((58, 131), (104, 124), (166, 133), (226, 132), (248, 124), (286, 124), (300, 129), (24, 130), (212, 128)):
        sup.set_at((x, y), (190, 194, 214))
        sup.set_at((x + 1, y), (90, 94, 118))
    # Caja de herramientas volcada (roja, con la tapa abierta)
    pygame.draw.rect(sup, (20, 22, 34), (276, 124, 16, 9))
    pygame.draw.rect(sup, (200, 56, 52), (277, 125, 14, 7))
    pygame.draw.rect(sup, (240, 110, 96), (277, 125, 14, 1))
    pygame.draw.rect(sup, (120, 30, 32), (277, 131, 14, 1))
    pygame.draw.polygon(sup, (170, 40, 40), [(277, 125), (291, 125), (294, 121), (280, 121)])
    pygame.draw.line(sup, (232, 232, 240), (281, 129), (287, 129))                      # asa
    # Una taza rodada y un charco de líquido
    pygame.draw.rect(sup, (230, 230, 240), (46, 132, 6, 4))
    pygame.draw.rect(sup, (150, 150, 170), (46, 135, 6, 1))
    for py in range(130, 136):
        for px in range(52, 66):
            if math.hypot((px - 59) / 7, (py - 133) / 2.5) < 1 and (px + py) % 3:
                sup.set_at((px, py), (96, 70, 56))


def chispas(sup, x, y, t, fase=0.0, periodo=1.3, n=6):
    """Un ráfaga de chispas que salta de un punto cada tanto: destello blanco y brasas que caen (píxeles enteros)."""
    u = ((t + fase) % periodo) / periodo
    if u > 0.45:
        return
    if u < 0.09:
        for dx, dy in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
            sup.set_at((x + dx, y + dy), (255, 255, 235))
    for k in range(n):
        ang = -math.pi / 2 + (k - n / 2) * 0.55 + math.sin(fase * 3 + k) * 0.25
        v = 34 + (k * 7) % 13
        px = x + int(math.cos(ang) * v * u)
        py = y + int(math.sin(ang) * v * u + 120 * u * u)
        color = (255, 250, 180) if u < 0.14 else (255, 190, 80) if u < 0.28 else (230, 90, 50)
        sup.set_at((px, py), color)
        if u < 0.28:
            sup.set_at((px + 1, py), color)
