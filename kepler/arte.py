"""
kepler/arte.py
Dibujos de los objetos grandes de los escenarios, hechos con figuras de pygame.

Como todo se dibuja a 320x200 y después se agranda sin suavizar, las
figuras (rectángulos, polígonos, círculos) ya quedan con aspecto pixelado.

Estas funciones dibujan la parte FIJA de cada objeto. Con ellas se arma la
hoja de sprites (python -m kepler.generar_hoja); el juego después usa los
sprites de la hoja. Lo que se ANIMA (luces que titilan, la pantalla de la
consola) está en funciones aparte que se dibujan encima en cada cuadro.
"""

import math
import random

import pygame


def estrellas(sup, area, cantidad, semilla, tiempo=None):
    """Estrellas al azar dentro de 'area'. Si se pasa 'tiempo', titilan."""
    x0, y0, ancho, alto = area
    azar = random.Random(semilla)   # semilla fija: siempre en el mismo lugar
    for i in range(cantidad):
        x = x0 + azar.randrange(ancho)
        y = y0 + azar.randrange(alto)
        brillo = azar.choice((120, 170, 230))
        if tiempo is not None and int(tiempo * 2 + i) % 5 == 0:
            brillo = 255
        sup.set_at((x, y), (brillo, brillo, min(255, brillo + 20)))


def planeta(sup, centro, radio, color, sombra, franja=None, anillo=None):
    """Planeta dibujado línea por línea: luz a la izquierda, sombra a la derecha."""
    cx, cy = centro
    if anillo:   # parte de atrás del anillo
        pygame.draw.ellipse(sup, anillo, (cx - radio * 1.7, cy - radio * 0.35, radio * 3.4, radio * 0.7), 1)
    for dy in range(-radio, radio + 1):
        mitad = int(math.sqrt(radio * radio - dy * dy))
        y = cy + dy
        base = franja if (franja and (dy // 4) % 3 == 0) else color
        pygame.draw.line(sup, base, (cx - mitad, y), (cx + mitad, y))
        pygame.draw.line(sup, sombra, (cx + int(mitad * 0.35), y), (cx + mitad, y))
    if anillo:   # parte de adelante del anillo (solo la mitad de abajo)
        rect = pygame.Rect(cx - radio * 1.7, cy - radio * 0.35, radio * 3.4, radio * 0.7)
        pygame.draw.arc(sup, anillo, rect, math.pi, 2 * math.pi, 2)


def capsula(sup, rect):
    """La cápsula de escape estrellada, con humo."""
    x, y, w, h = rect
    cuerpo = [(x + 4, y + h - 4), (x + 10, y + 10), (x + 44, y + 4), (x + 60, y + 18), (x + 56, y + h - 2)]
    pygame.draw.polygon(sup, (150, 150, 168), cuerpo)
    pygame.draw.line(sup, (196, 196, 210), (x + 11, y + 11), (x + 43, y + 5))      # brillo
    pygame.draw.line(sup, (200, 80, 60), (x + 8, y + 22), (x + 57, y + 16), 2)      # franja
    pygame.draw.polygon(sup, (40, 36, 52), cuerpo, 1)
    pygame.draw.ellipse(sup, (40, 56, 120), (x + 24, y + 10, 12, 9))                # ventanilla
    pygame.draw.rect(sup, (150, 220, 255), (x + 26, y + 12, 3, 2))
    for cx, cy in ((x + 16, y + 26), (x + 44, y + 25), (x + 50, y + 30)):           # quemaduras
        pygame.draw.circle(sup, (70, 58, 62), (cx, cy), 3)
    pygame.draw.polygon(sup, (110, 110, 128), [(x + 56, y + h - 2), (x + 64, y + h - 10), (x + 62, y + h)])
    for cx, cy, r in ((x + 46, y - 2, 4), (x + 51, y - 10, 5), (x + 47, y - 20, 6)):  # humo
        pygame.draw.circle(sup, (96, 84, 100), (cx, cy), r)
        pygame.draw.circle(sup, (124, 110, 126), (cx - 1, cy - 1), r - 2)


def caja(sup, rect, abierta):
    """Caja de suministros. Abierta muestra la tapa levantada."""
    x, y, w, h = rect
    madera, oscura, metal = (150, 104, 60), (92, 60, 34), (110, 110, 128)
    if abierta:
        pygame.draw.polygon(sup, oscura, [(x + 1, y + 4), (x + 6, y - 6), (x + w + 2, y - 6), (x + w - 1, y + 4)])
        pygame.draw.polygon(sup, madera, [(x + 2, y + 3), (x + 6, y - 5), (x + w + 1, y - 5), (x + w - 2, y + 3)])
    pygame.draw.rect(sup, madera, (x, y + 4, w, h - 4))
    pygame.draw.rect(sup, oscura, (x, y + 4, w, h - 4), 1)
    pygame.draw.line(sup, oscura, (x + 1, y + 5), (x + w - 2, y + h - 2))
    pygame.draw.line(sup, oscura, (x + w - 2, y + 5), (x + 1, y + h - 2))
    pygame.draw.rect(sup, metal, (x + w // 2 - 2, y + 4, 4, 3))
    if abierta:
        pygame.draw.rect(sup, (40, 26, 18), (x + 2, y + 4, w - 4, 2))   # interior oscuro


def compuerta(sup, rect, abierta, iluminada):
    """Compuerta blindada de la cueva, con teclado. Abierta se ve el interior."""
    x, y, w, h = rect
    marco = pygame.Rect(x - 4, y - 4, w + 8, h + 4)
    pygame.draw.rect(sup, (64, 60, 76), marco)
    pygame.draw.rect(sup, (30, 26, 40), marco, 1)
    if not abierta:
        pygame.draw.rect(sup, (128, 128, 146), (x, y, w, h))
        pygame.draw.line(sup, (80, 80, 98), (x + w // 2, y), (x + w // 2, y + h - 1))
        for i in range(0, w, 8):   # franjas de peligro abajo
            pygame.draw.rect(sup, (230, 190, 40), (x + i, y + h - 6, 4, 6))
            pygame.draw.rect(sup, (30, 26, 30), (x + i + 4, y + h - 6, 4, 6))
    elif not iluminada:
        pygame.draw.rect(sup, (6, 4, 10), (x, y, w, h))
    else:
        pygame.draw.rect(sup, (20, 30, 60), (x, y, w, h))
        for cx, cy, alto in ((x + 8, y + h, 14), (x + 38, y + h, 18), (x + 30, y + 14, -10), (x + 12, y + 8, -8)):
            punta = cy - alto
            pygame.draw.polygon(sup, (70, 180, 210), [(cx - 3, cy), (cx + 3, cy), (cx, punta)])
    # Teclado numérico a la derecha
    teclado = pygame.Rect(x + w + 6, y + 18, 9, 13)
    pygame.draw.rect(sup, (50, 50, 64), teclado)
    for fila in range(3):
        for col in range(2):
            sup.set_at((teclado.x + 2 + col * 4, teclado.y + 2 + fila * 3), (200, 200, 220))


def luz_compuerta(sup, rect, abierta, tiempo):
    """ANIMADO: luz del teclado. Roja titilando si está cerrada, verde si está abierta."""
    x, y, w, h = rect
    luz = (90, 230, 120) if abierta else ((230, 60, 60) if int(tiempo * 2) % 2 else (120, 30, 30))
    pygame.draw.rect(sup, luz, (x + w + 9, y + 8, 4, 2))


def cartel(sup, rect):
    """Cartel de advertencia clavado en la roca."""
    x, y, w, h = rect
    pygame.draw.rect(sup, (90, 62, 40), (x + w // 2 - 1, y + h - 2, 3, 12))
    pygame.draw.rect(sup, (230, 190, 40), (x, y, w, h - 2))
    pygame.draw.rect(sup, (40, 30, 20), (x, y, w, h - 2), 1)
    pygame.draw.polygon(sup, (40, 30, 20), [(x + w // 2, y + 3), (x + w // 2 + 5, y + h - 6), (x + w // 2 - 5, y + h - 6)], 1)
    pygame.draw.line(sup, (40, 30, 20), (x + w // 2, y + 7), (x + w // 2, y + 9))


def cohete(sup, rect, energia):
    """El cohete abandonado sobre su base de lanzamiento."""
    x, y, w, h = rect
    cx = x + w // 2
    blanco, gris, rojo = (226, 226, 236), (150, 150, 170), (200, 56, 56)
    pygame.draw.polygon(sup, rojo, [(cx - 10, y + 18), (cx + 10, y + 18), (cx, y)])                 # punta
    pygame.draw.rect(sup, blanco, (cx - 10, y + 18, 20, 56))                                         # cuerpo
    pygame.draw.rect(sup, gris, (cx + 4, y + 18, 6, 56))                                             # sombra
    pygame.draw.polygon(sup, rojo, [(cx - 10, y + 56), (cx - 20, y + 78), (cx - 10, y + 74)])        # aletas
    pygame.draw.polygon(sup, rojo, [(cx + 10, y + 56), (cx + 20, y + 78), (cx + 10, y + 74)])
    pygame.draw.rect(sup, (70, 70, 86), (cx - 6, y + 74, 12, 6))                                     # tobera
    ventana = (110, 230, 250) if energia else (40, 56, 120)
    pygame.draw.circle(sup, (60, 60, 76), (cx, y + 32), 5)
    pygame.draw.circle(sup, ventana, (cx, y + 32), 4)
    for i in range(4):   # medidor de energía (la cuarta barra titila: ver luces_cohete)
        encendida = energia and i < 3
        pygame.draw.rect(sup, (90, 230, 120) if encendida else (50, 50, 62), (cx - 3, y + 62 - i * 4, 6, 3))
    pygame.draw.polygon(sup, (40, 36, 52), [(cx - 10, y + 18), (cx, y), (cx + 10, y + 18),
                                            (cx + 10, y + 74), (cx - 10, y + 74)], 1)
    # Base de lanzamiento
    base = pygame.Rect(x, y + 80, w, 12)
    pygame.draw.rect(sup, (96, 98, 116), base)
    for i in range(0, w, 6):
        pygame.draw.rect(sup, (230, 190, 40), (x + i, y + 80, 3, 3))
    pygame.draw.rect(sup, (40, 36, 52), base, 1)


def luces_cohete(sup, rect, energia, tiempo):
    """ANIMADO: con energía, titilan la cuarta barra del medidor y la luz de la punta."""
    if not energia:
        return
    x, y, w, h = rect
    cx = x + w // 2
    if int(tiempo * 3) % 2:
        pygame.draw.rect(sup, (90, 230, 120), (cx - 3, y + 50, 6, 3))
    if int(tiempo * 2) % 2:
        pygame.draw.rect(sup, (255, 90, 90), (cx - 1, y - 3, 2, 2))


def consola(sup, rect, encendida):
    """Consola de control del cohete."""
    x, y, w, h = rect
    pygame.draw.polygon(sup, (80, 82, 100), [(x, y + h), (x + w, y + h), (x + w - 3, y + 8), (x + 3, y + 8)])
    pygame.draw.rect(sup, (110, 112, 132), (x + 2, y, w - 4, 12))
    pantalla = pygame.Rect(x + 4, y + 2, w - 8, 8)
    pygame.draw.rect(sup, (20, 70, 40) if encendida else (24, 24, 32), pantalla)
    for i, color in enumerate(((230, 60, 60), (240, 200, 60), (90, 200, 240))):
        pygame.draw.rect(sup, color if encendida else (60, 60, 72), (x + 6 + i * 7, y + 16, 4, 3))
    pygame.draw.rect(sup, (40, 36, 52), (x, y, w, h), 1)


def pantalla_consola(sup, rect, encendida, tiempo):
    """ANIMADO: líneas de texto que corren en la pantalla de la consola encendida."""
    if not encendida:
        return
    x, y, w, h = rect
    for i in range(3):
        largo = 6 + (i * 5 + int(tiempo * 4)) % 10
        pygame.draw.line(sup, (110, 240, 140), (x + 6, y + 4 + i * 2), (x + 6 + largo, y + 4 + i * 2))


def heladera(sup, rect, abierta):
    """La heladera de la cápsula. Abierta se ve el interior con estantes y la puerta de canto."""
    x, y, w, h = rect
    contorno = (14, 10, 24)
    pygame.draw.rect(sup, (226, 228, 236), (x, y, w, h))
    pygame.draw.rect(sup, (60, 60, 76), (x + 2, y + h, w - 4, 2))                 # patas
    if abierta:
        pygame.draw.rect(sup, (190, 226, 240), (x + 3, y + 3, w - 6, h - 6))      # interior
        for estante in (y + h // 3, y + 2 * h // 3):
            pygame.draw.line(sup, (120, 150, 170), (x + 3, estante), (x + w - 4, estante))
        puerta = [(x + w, y), (x + w + 8, y + 4), (x + w + 8, y + h - 2), (x + w, y + h)]
        pygame.draw.polygon(sup, (196, 198, 212), puerta)
        pygame.draw.polygon(sup, contorno, puerta, 1)
    else:
        pygame.draw.line(sup, (170, 174, 190), (x + 1, y + h // 3), (x + w - 2, y + h // 3))   # división del freezer
        pygame.draw.rect(sup, (150, 154, 170), (x + w - 6, y + 8, 2, 12))                      # manija
        pygame.draw.rect(sup, (230, 80, 80), (x + 5, y + h // 3 + 6, 4, 4))                    # imán
    pygame.draw.rect(sup, contorno, (x, y, w, h), 1)


def cristal_grande(sup, rect):
    """El cristal de energía enorme del fondo de la cueva: un racimo de tres prismas."""
    x, y, w, h = rect
    base = y + h
    contorno = (14, 10, 24)
    # (centro x, ancho, alto, color claro, color oscuro): primero los de atrás
    racimo = [
        (x + 8, 12, int(h * 0.55), (90, 210, 235), (40, 130, 175)),
        (x + w - 9, 12, int(h * 0.45), (90, 210, 235), (40, 130, 175)),
        (x + w // 2, 20, h, (110, 230, 245), (50, 150, 190)),
    ]
    for cx, ancho, alto, claro, oscuro in racimo:
        mitad = ancho // 2
        punta = base - alto
        hombro = punta + mitad + 2
        pygame.draw.polygon(sup, claro, [(cx - mitad, base), (cx - mitad, hombro), (cx, punta), (cx, base)])
        pygame.draw.polygon(sup, oscuro, [(cx, base), (cx, punta), (cx + mitad, hombro), (cx + mitad, base)])
        pygame.draw.polygon(sup, (200, 250, 255), [(cx - mitad, hombro), (cx, punta), (cx, hombro)])   # faceta de la punta
        pygame.draw.line(sup, (240, 255, 255), (cx - mitad // 2, hombro + 3), (cx - mitad // 2, base - 8))
        pygame.draw.polygon(sup, contorno, [(cx - mitad, base), (cx - mitad, hombro), (cx, punta),
                                            (cx + mitad, hombro), (cx + mitad, base)], 1)


def _tono(c, k):
    """Aclara (k > 0, hacia un tono cálido) u oscurece (k < 0, hacia un tono frío) un color."""
    if k >= 0:
        return (min(255, int(c[0] + (255 - c[0]) * k + 6 * k)), min(255, int(c[1] + (255 - c[1]) * k)),
                min(255, int(c[2] + (255 - c[2]) * k * 0.8)))
    k = -k
    return (int(c[0] * (1 - k) * 0.96), int(c[1] * (1 - k) * 0.92), min(255, int(c[2] * (1 - k) * 0.92 + 16 * k)))


def _caja_sombreada(sup, rect, color):
    """Un rectángulo con volumen: luz arriba y a la izquierda, sombra abajo y a la derecha."""
    x, y, w, h = rect
    pygame.draw.rect(sup, color, rect)
    if w > 2 and h > 2:
        pygame.draw.line(sup, _tono(color, 0.32), (x, y), (x + w - 2, y))
        pygame.draw.line(sup, _tono(color, 0.32), (x, y), (x, y + h - 2))
        pygame.draw.line(sup, _tono(color, -0.32), (x, y + h - 1), (x + w - 1, y + h - 1))
        pygame.draw.line(sup, _tono(color, -0.32), (x + w - 1, y), (x + w - 1, y + h - 1))


def _cabeza_alien(sup, cx, y, piel):
    """Cabeza en forma de huevo (ancha arriba, con el mentón fino), sombreada como una esfera."""
    rampa = [_tono(piel, -0.5), _tono(piel, -0.28), piel, _tono(piel, 0.28), _tono(piel, 0.55)]
    forma = ((cx, y + 6.5, 7.0, 6.2), (cx, y + 10.0, 4.4, 4.2))       # (centro x, centro y, radio x, radio y)
    for py in range(y, y + 15):
        for px in range(cx - 8, cx + 9):
            dentro = False
            for ex, ey, rx, ry in forma:
                if ((px + 0.5 - ex) / rx) ** 2 + ((py + 0.5 - ey) / ry) ** 2 <= 1:
                    dentro = True
            if not dentro:
                continue
            # La luz se calcula con UN solo huevo para toda la cabeza (así el mentón no queda con costuras)
            nx, ny = (px + 0.5 - cx) / 7.6, (py + 0.5 - (y + 7.0)) / 8.4
            nz = max(0.0, 1 - nx * nx - ny * ny) ** 0.5
            luz = max(0.0, min(0.999, 0.1 + (-0.55 * nx - 0.5 * ny) * 0.6 + 0.5 * nz))
            sup.set_at((px, py), rampa[int(luz * len(rampa))])


def _silla(sup, cx, y):
    """Una mecedora de respaldo alto vista de frente: parantes con remates, travesaño, asiento, patas
    y patines curvos. 'cx' es el centro y 'y' el borde de arriba del dibujo."""
    contorno = (14, 10, 24)
    madera = (150, 98, 56)
    patin = [(cx - 11, y + 27), (cx - 8, y + 29), (cx + 7, y + 29), (cx + 10, y + 27)]
    cajas = [((cx - 11, y + 4, 2, 23), madera), ((cx + 9, y + 4, 2, 23), madera),           # parantes del respaldo
             ((cx - 11, y + 3, 2, 2), _tono(madera, 0.35)), ((cx + 9, y + 3, 2, 2), _tono(madera, 0.35)),   # remates
             ((cx - 10, y + 15, 20, 2), _tono(madera, 0.12)),                               # travesaño
             ((cx - 11, y + 25, 22, 2), _tono(madera, 0.25)),                               # asiento, más ancho que el alien
             ((cx - 10, y + 27, 2, 2), madera), ((cx + 8, y + 27, 2, 2), madera)]           # patas
    pygame.draw.lines(sup, contorno, False, patin, 3)
    for r, _ in cajas:
        pygame.draw.rect(sup, contorno, pygame.Rect(r).inflate(2, 2))
    pygame.draw.lines(sup, madera, False, patin, 1)
    pygame.draw.line(sup, _tono(madera, 0.3), (cx - 7, y + 29), (cx + 6, y + 29))
    for r, color in cajas:
        _caja_sombreada(sup, r, color)


def minero_mecedora(sup, rect, grados):
    """
    El minero sentado en su mecedora, inclinado 'grados' (positivo = hacia la derecha). La silla se gira
    entera alrededor del patín; el alien, que tiene detalles chiquitos (ojos, antenas), no se gira:
    se corre unos píxeles según la inclinación, así su cara queda siempre nítida.
    """
    x, y, w, h = rect
    capa = pygame.Surface(sup.get_size(), pygame.SRCALPHA)
    _silla(capa, x + w // 2, y)
    rotar_pixel(capa, grados)
    sup.blit(capa, (0, 0))
    seno = math.sin(math.radians(grados))
    minero(sup, rect, True, silla=False, dx_cuerpo=round(11 * seno), dx_cabeza=round(7 * seno))


def _termo(sup, cx, cy, inclinado=False):
    """
    Un termo plateado con tapa negra, centrado en (cx, cy): 6 de ancho y 12 de alto. 'inclinado' lo gira de modo
    que la tapa (por donde sirve) apunta hacia abajo y a la izquierda.
    """
    contorno = (14, 10, 24)
    plata = ((236, 240, 250), (190, 196, 218), (150, 156, 182), (104, 110, 140))
    if not inclinado:
        x0, y0 = cx - 3, cy - 6
        pygame.draw.rect(sup, contorno, (x0 - 1, y0 - 4, 8, 18))
        for i, color in enumerate((plata[0], plata[1], plata[1], plata[2], plata[2], plata[3])):
            pygame.draw.line(sup, color, (x0 + i, y0), (x0 + i, y0 + 11))
        pygame.draw.rect(sup, (30, 32, 44), (x0, y0 - 3, 6, 3))                      # la tapa
        pygame.draw.line(sup, (90, 94, 120), (x0, y0 - 3), (x0 + 5, y0 - 3))
        pygame.draw.rect(sup, (46, 50, 72), (x0, y0 + 3, 6, 2))                      # la faja del medio
        return
    ang = math.radians(225)
    seno, coseno = math.sin(ang), math.cos(ang)

    def girar(px, py):
        return (cx + px * coseno - py * seno, cy + px * seno + py * coseno)

    cuerpo = [girar(-3, -6), girar(3, -6), girar(3, 6), girar(-3, 6)]
    tapa = [girar(-3, -9), girar(3, -9), girar(3, -6), girar(-3, -6)]
    pygame.draw.polygon(sup, contorno, [girar(-4, -10), girar(4, -10), girar(4, 7), girar(-4, 7)])
    pygame.draw.polygon(sup, plata[1], cuerpo)
    pygame.draw.polygon(sup, plata[0], [girar(-3, -6), girar(-1, -6), girar(-1, 6), girar(-3, 6)])
    pygame.draw.polygon(sup, plata[3], [girar(2, -6), girar(3, -6), girar(3, 6), girar(2, 6)])
    pygame.draw.polygon(sup, (30, 32, 44), tapa)


def minero(sup, rect, sentado=False, piel=(86, 176, 76), traje=(34, 48, 120), detalle=(116, 64, 176),
           gema=(255, 170, 40), antena=(240, 130, 40), dy_cabeza=0, mov_antena=0, parpadeo=False,
           silla=True, dx_cuerpo=0, dx_cabeza=0, enojado=False, bigote=False, mate=-1, asustado=False,
           brazo=None, hacha=False):
    """Un alien verde de ojos enormes, sin casco, con antenas, traje azul oscuro, hombreras violetas y
    botas. Con otros colores sirve para la mercader.
      - sentado: sentado en una silla mecedora (el minero de la entrada de la cueva). Con silla=False
        no se dibuja la silla (se dibuja aparte, para poder girarla). dx_cuerpo y dx_cabeza corren
        el cuerpo y la cabeza hacia un lado (así sigue el vaivén de la silla sin deformarse).
      - enojado: cejas fruncidas y la boca hacia abajo (el frutero).
      - asustado: cejas levantadas y preocupadas, la boca abierta en una 'o' y una gota de sudor (la mercader acorralada).
      - bigote: un bigote enorme con las puntas para arriba (el boletero).
      - mate: cebar y tomar mate (el boletero). Cada número es un momento: 0 = el termo y el mate están sobre el
        mostrador, 1 = levanta el termo, 2 y 3 = sirve agua (la corriente cambia), 4 = agarra el mate, 5 = sorbe
        de la bombilla (-1 = nada).
      - brazo: el brazo derecho se mueve. 'arriba' (levantado), 'abajo' (apoyado sobre el mostrador) o 'lado_a' /
        'lado_b' (agita la mano de un lado al otro). Con hacha=True lleva un hacha de carnicero en la mano.
      - dy_cabeza (0 o -1), mov_antena (-1, 0 o 1) y parpadeo: pequeños movimientos para animarlo
        (la cabeza sube y baja, las antenas se mecen, cierra los ojos)."""
    x, y, w, h = rect
    cx = x + w // 2
    if sentado and silla:
        _silla(sup, cx, y)                                  # la silla va detrás del alien
    cx += dx_cuerpo                                         # el alien puede correrse con el vaivén de la silla
    cxh = cx + dx_cabeza                                    # y la cabeza, un poco más
    yh = y + dy_cabeza                                      # la altura de la cabeza (puede subir 1 píxel)
    contorno = (14, 10, 24)
    tostado, hebilla = (214, 150, 60), (190, 194, 210)

    cajas = []
    if sentado:
        piernas = [((cx - 5, y + 22, 4, 4), traje), ((cx + 1, y + 22, 4, 4), traje)]      # muslos, sobre el asiento
        botas = [((cx - 6, y + 26, 5, 3), detalle), ((cx + 1, y + 26, 5, 3), detalle)]    # las botas cuelgan
    else:
        piernas = [((cx - 5, y + 21, 4, 7), traje), ((cx + 1, y + 21, 4, 7), traje)]
        botas = [((cx - 6, y + 27, 5, 3), detalle), ((cx + 1, y + 27, 5, 3), detalle)]
    cajas += botas + piernas + [
        ((cx - 8, y + 15, 3, 8), traje),                   # brazos
        ((cx + 6, y + 15, 3, 8), traje),
        ((cx - 5, y + 14, 10, 8), traje),                  # torso
        ((cx - 8, y + 13, 4, 3), detalle),                 # hombreras
        ((cx + 4, y + 13, 4, 3), detalle),
        ((cx - 3, y + 13, 6, 2), detalle),                 # cuello del traje
        ((cx - 8, y + 19, 3, 2), detalle),                 # puños
        ((cx + 6, y + 19, 3, 2), detalle),
    ]
    manos = [(cx - 9, y + 22, 4, 3), (cx + 6, y + 22, 4, 3)]
    if mate >= 1:                                           # el brazo derecho se mueve (sirve y toma): se dibuja aparte
        cajas = [c for c in cajas if c[0] not in ((cx + 6, y + 15, 3, 8), (cx + 6, y + 19, 3, 2))]
        manos = manos[:1]
    if brazo:                                               # el brazo derecho se dibuja aparte (mueve la mano)
        cajas = [c for c in cajas if c[0] not in ((cx + 6, y + 15, 3, 8), (cx + 6, y + 19, 3, 2))]
        manos = manos[:1]
    ax = mov_antena                                         # cuánto se mecen las puntas de las antenas

    # --- contorno de toda la silueta ---
    for r, _ in cajas:
        pygame.draw.rect(sup, contorno, pygame.Rect(r).inflate(2, 2))
    for r in manos:
        pygame.draw.rect(sup, contorno, pygame.Rect(r).inflate(2, 2))
    pygame.draw.ellipse(sup, contorno, (cxh - 8, yh, 16, 14))
    pygame.draw.ellipse(sup, contorno, (cxh - 5, yh + 7, 10, 8))
    for lado in (-1, 1):
        pygame.draw.line(sup, contorno, (cxh + lado * 3, yh + 3), (cxh + lado * 6 + ax, yh - 2), 3)
        pygame.draw.circle(sup, contorno, (cxh + lado * 6 + ax, yh - 3), 3)

    # --- relleno ---
    for r, color in cajas:
        _caja_sombreada(sup, r, color)
    for r in manos:
        _caja_sombreada(sup, r, piel)
        sup.set_at((r[0] + 1, r[1] + 2), _tono(piel, -0.5))                          # separación de dedos
        sup.set_at((r[0] + 2, r[1] + 2), _tono(piel, -0.5))
    _cabeza_alien(sup, cxh, yh + 1, piel)
    for lado in (-1, 1):                                    # antenas con bolita brillante
        pygame.draw.line(sup, antena, (cxh + lado * 3, yh + 3), (cxh + lado * 6 + ax, yh - 2))
        pygame.draw.circle(sup, _tono(antena, 0.25), (cxh + lado * 6 + ax, yh - 3), 2)
        sup.set_at((cxh + lado * 6 + ax - 1, yh - 4), _tono(antena, 0.8))

    ojo = (12, 8, 34)
    if parpadeo:                                            # ojos cerrados: una rayita
        pygame.draw.line(sup, ojo, (cxh - 5, yh + 8), (cxh - 2, yh + 8))
        pygame.draw.line(sup, ojo, (cxh + 3, yh + 8), (cxh + 6, yh + 8))
        pygame.draw.line(sup, ojo, (cxh - 4, yh + 9), (cxh - 2, yh + 9))
        pygame.draw.line(sup, ojo, (cxh + 3, yh + 9), (cxh + 5, yh + 9))
    else:                                                   # ojos grandes, negros, inclinados, con reflejos
        for lado in (-1, 1):
            base = [(5, 5), (4, 4), (2, 5), (1, 7), (1, 9), (3, 10), (4, 10), (5, 8), (5, 6)]
            puntos = [(cxh + lado * ax_ + (0 if lado < 0 else 1), yh + ay) for ax_, ay in base]
            pygame.draw.polygon(sup, ojo, puntos)
            corr = (0 if lado < 0 else 1) + (-1 if lado < 0 else 0)
            sup.set_at((cxh + lado * 4 + corr, yh + 5), (255, 255, 255))              # reflejo grande
            sup.set_at((cxh + lado * 3 + corr, yh + 9), (96, 110, 226))               # reflejo azul abajo
    boca = _tono(piel, -0.62)
    pygame.draw.line(sup, boca, (cxh - 1, yh + 12), (cxh + 1, yh + 12))
    if enojado:                                             # cejas hacia abajo, hacia la nariz, y boca de disgusto
        ceja = _tono(piel, -0.75)
        for dx, dy in ((6, 3), (5, 3), (4, 4), (3, 4), (2, 5), (1, 5)):
            sup.set_at((cxh - dx, yh + dy), ceja)
            sup.set_at((cxh + dx, yh + dy), ceja)
        sup.set_at((cxh - 2, yh + 13), boca)
        sup.set_at((cxh + 2, yh + 13), boca)
    elif asustado:                                          # cejas preocupadas (las puntas de adentro, arriba), boca en 'o', sudor
        ceja = _tono(piel, -0.75)
        for dx, dy in ((6, 4), (5, 3), (4, 3), (3, 2), (2, 2), (1, 1)):
            sup.set_at((cxh - dx, yh + dy), ceja)
            sup.set_at((cxh + dx, yh + dy), ceja)
        pygame.draw.rect(sup, (34, 12, 36), (cxh - 1, yh + 11, 3, 3))
        sup.set_at((cxh, yh + 12), (120, 36, 70))
        for sx, sy in ((cxh + 8, yh + 4), (cxh + 8, yh + 5), (cxh + 7, yh + 6), (cxh + 8, yh + 6)):
            sup.set_at((sx, sy), (150, 214, 252))
        sup.set_at((cxh + 8, yh + 4), (230, 248, 255))
    else:                                                   # sonriente
        sup.set_at((cxh - 2, yh + 11), boca)
        sup.set_at((cxh + 2, yh + 11), boca)

    if bigote:                                              # bigote grande, con las puntas enroscadas hacia arriba
        pelo, brillo = (104, 66, 40), (170, 120, 76)
        for dx in range(1, 7):
            for lado in (-1, 1):
                sup.set_at((cxh + lado * dx, yh + 12), pelo)
                if dx >= 2:
                    sup.set_at((cxh + lado * dx, yh + 11), pelo)
        for lado in (-1, 1):
            for dx, dy in ((7, 11), (7, 10), (8, 10), (8, 9)):
                sup.set_at((cxh + lado * dx, yh + dy), pelo)
            sup.set_at((cxh + lado * 3, yh + 11), brillo)
            sup.set_at((cxh + lado * 5, yh + 11), brillo)
        sup.set_at((cxh, yh + 11), pelo)
        sup.set_at((cxh, yh + 12), pelo)

    # Traje: gema en el pecho, luces y cinturón con bolsitas
    pygame.draw.rect(sup, _tono(gema, -0.35), (cx - 2, y + 16, 4, 4))
    pygame.draw.rect(sup, gema, (cx - 1, y + 17, 2, 2))
    sup.set_at((cx - 1, y + 17), _tono(gema, 0.7))
    sup.set_at((cx - 4, y + 16), (80, 220, 130))
    sup.set_at((cx + 3, y + 16), (250, 110, 70))
    pygame.draw.line(sup, tostado, (cx - 5, y + 21), (cx + 4, y + 21))                # cinturón
    for bx in (cx - 5, cx + 3):
        _caja_sombreada(sup, (bx, y + 20, 2, 3), tostado)
    pygame.draw.rect(sup, hebilla, (cx - 1, y + 21, 2, 1))

    if mate >= 0:                                           # el mostrador queda 24 píxeles debajo del borde de arriba
        hombro = (cx + 7, y + 14)
        # (termo: posición y si está inclinado), calabaza del mate, y el brazo (codo, mano) si se mueve
        estados = {
            0: ((cx + 19, y + 18, False), (cx + 7, y + 21), None),
            1: ((cx + 19, y + 13, False), (cx + 7, y + 21), ((cx + 13, y + 18), (cx + 17, y + 15))),
            2: ((cx + 15, y + 7, True), (cx + 7, y + 21), ((cx + 14, y + 16), (cx + 16, y + 11))),
            3: ((cx + 15, y + 7, True), (cx + 7, y + 21), ((cx + 14, y + 16), (cx + 16, y + 11))),
            4: ((cx + 19, y + 18, False), (cx + 6, y + 20), ((cx + 12, y + 19), (cx + 8, y + 21))),
            5: ((cx + 19, y + 18, False), (cx + 2, y + 20), ((cx + 12, y + 19), (cx + 5, y + 21))),
        }
        (tx, ty, inclinado), (gx, gy), brazo_mate = estados[mate]
        if brazo_mate:                                           # el brazo, con la mano (en la posición que toca)
            codo, mano = brazo_mate
            pygame.draw.lines(sup, contorno, False, [hombro, codo, mano], 5)
            pygame.draw.lines(sup, traje, False, [hombro, codo, mano], 3)
            pygame.draw.line(sup, _tono(traje, 0.3), hombro, codo)
        _termo(sup, tx, ty, inclinado)
        if brazo_mate:
            pygame.draw.rect(sup, contorno, (mano[0] - 2, mano[1] - 2, 5, 5))
            pygame.draw.rect(sup, piel, (mano[0] - 1, mano[1] - 1, 3, 3))                  # la mano
        if mate in (2, 3):                                  # el chorro de agua, de la tapa del termo a la calabaza
            for py in range(y + 13, gy - 2):
                if (py + mate) % 2 == 0:
                    sup.set_at((cx + 9, py), (150, 214, 255))
                else:
                    sup.set_at((cx + 9, py), (214, 240, 255))
        pygame.draw.rect(sup, contorno, (gx - 3, gy - 3, 7, 7))                            # el mate: calabaza con aro de metal
        pygame.draw.rect(sup, (126, 82, 50), (gx - 2, gy - 2, 5, 5))
        pygame.draw.rect(sup, (176, 124, 78), (gx - 2, gy - 2, 5, 1))
        pygame.draw.rect(sup, (84, 54, 34), (gx - 2, gy + 1, 5, 2))
        pygame.draw.line(sup, (214, 218, 236), (gx - 2, gy - 2), (gx + 2, gy - 2))
        pygame.draw.line(sup, (214, 218, 236), (gx, gy - 3), (gx, gy - 7))               # la bombilla: SIEMPRE derecha, nunca doblada
        sup.set_at((gx, gy - 7), (255, 255, 255))
        if mate in (3, 4):                                  # el vapor del agua caliente
            for dx, dy in ((2, -5), (3, -7), (2, -9)):
                sup.set_at((gx + dx, gy + dy), (236, 240, 250))


    if brazo:                                               # el brazo derecho en movimiento (y el hacha, si la lleva)
        hombro = (cx + 7, y + 14)
        posiciones = {
            "arriba": ((cx + 11, y + 8), (cx + 11, y + 3)),
            "abajo": ((cx + 11, y + 8), (cx + 10, y + 10)),
            "lado_a": ((cx + 10, y + 13), (cx + 5, y + 11)),
            "lado_b": ((cx + 11, y + 13), (cx + 13, y + 8)),
        }
        codo, mano = posiciones[brazo]
        pygame.draw.lines(sup, contorno, False, [hombro, codo, mano], 5)
        pygame.draw.lines(sup, traje, False, [hombro, codo, mano], 3)
        pygame.draw.line(sup, _tono(traje, 0.3), hombro, codo)
        if hacha:
            acero, filo, cabo = (170, 176, 198), (240, 244, 255), (150, 98, 56)
            if brazo == "arriba":                           # el hacha en alto: la hoja para arriba
                pygame.draw.rect(sup, contorno, (mano[0] - 5, mano[1] - 9, 8, 7))
                pygame.draw.rect(sup, acero, (mano[0] - 4, mano[1] - 8, 6, 5))
                pygame.draw.line(sup, filo, (mano[0] - 4, mano[1] - 8), (mano[0] + 1, mano[1] - 8))
                pygame.draw.line(sup, cabo, (mano[0], mano[1] - 3), (mano[0], mano[1]), 2)
            else:                                           # el golpe: la hoja contra la tabla
                pygame.draw.rect(sup, contorno, (mano[0] - 4, mano[1] + 1, 8, 6))
                pygame.draw.rect(sup, acero, (mano[0] - 3, mano[1] + 2, 6, 4))
                pygame.draw.line(sup, filo, (mano[0] - 3, mano[1] + 5), (mano[0] + 2, mano[1] + 5))
                pygame.draw.line(sup, cabo, (mano[0], mano[1] - 1), (mano[0], mano[1] + 1), 2)
        pygame.draw.rect(sup, contorno, (mano[0] - 2, mano[1] - 1, 5, 4))
        pygame.draw.rect(sup, piel, (mano[0] - 1, mano[1], 3, 2))                    # la mano


def rotar_pixel(sup, grados):
    """
    Gira todo el dibujo 'grados' (positivo = hacia la derecha) alrededor del punto donde apoya en
    el piso (abajo, en el medio), como una mecedora que se hamaca. Sirve para animarla.
    Para que el pixel art no se arruine, se agranda 4 veces, se gira y se vuelve a achicar
    tomando el píxel del centro de cada bloque (los colores siguen siendo los mismos, sin mezclas).
    """
    if grados == 0:
        return
    ancho, alto = sup.get_size()
    px, py = ancho / 2, alto - 3.5                           # el pivote: el patín en el piso
    f = 4
    grande = pygame.transform.scale(sup, (ancho * f, alto * f))
    lado = f * 2 * max(ancho, alto)
    lienzo = pygame.Surface((lado, lado), pygame.SRCALPHA)
    lienzo.blit(grande, (lado // 2 - int(px * f), lado // 2 - int(py * f)))   # el pivote queda en el centro
    girado = pygame.transform.rotate(lienzo, -grados)        # rotate gira hacia la izquierda con ángulos positivos
    cx, cy = girado.get_width() // 2, girado.get_height() // 2
    recorte = pygame.Rect(cx - int(px * f) + f // 2, cy - int(py * f) + f // 2, ancho * f, alto * f)
    chico = pygame.transform.scale(girado.subsurface(recorte), (ancho, alto))
    sup.fill((0, 0, 0, 0))
    sup.blit(chico, (0, 0))


def pico_pared(sup, rect, entero=False):
    """
    Un pico apoyado en la pared. Solo la cabeza de metal (sin mango), o el pico entero con su mango.
    La cabeza es una media luna que termina en dos PUNTAS finas, como un pico de verdad.
    """
    x, y, w, h = rect
    contorno = (14, 10, 24)
    acero, brillo, filo, mango = (186, 192, 214), (240, 244, 255), (120, 126, 150), (150, 98, 56)
    ty = y if entero else y + (h - 9)                                 # arriba de la cabeza
    if entero:                                                        # el mango, derecho, con luz a la izquierda
        pygame.draw.line(sup, contorno, (x + 6, ty + 3), (x + 6, y + h - 1), 4)
        pygame.draw.line(sup, mango, (x + 6, ty + 3), (x + 6, y + h - 2), 2)
        pygame.draw.line(sup, (196, 140, 88), (x + 5, ty + 3), (x + 5, y + h - 2))
    exterior = [(x, ty + 8), (x + 1, ty + 4), (x + 3, ty + 2), (x + 6, ty + 1), (x + 9, ty + 2), (x + 11, ty + 4), (x + 12, ty + 8)]
    interior = [(x + 10, ty + 5), (x + 8, ty + 4), (x + 6, ty + 3), (x + 4, ty + 4), (x + 2, ty + 5)]
    cabeza = exterior + interior                                      # los dos extremos del arco son puntas
    pygame.draw.polygon(sup, acero, cabeza)
    pygame.draw.polygon(sup, contorno, cabeza, 1)
    pygame.draw.lines(sup, brillo, False, exterior[1:4], 1)           # luz en el lomo de arriba
    for punta in (exterior[0], exterior[-1]):                         # las puntas, más oscuras y afiladas
        sup.set_at(punta, filo)
    if not entero:
        pygame.draw.rect(sup, (96, 102, 126), (x + 5, ty + 2, 3, 2))   # el hueco donde iría el mango


def cofre(sup, rect, abierto=False):
    """Un cofre de madera con herrajes. Abierto, la tapa queda levantada hacia atrás."""
    x, y, w, h = rect
    contorno = (14, 10, 24)
    madera, claro, metal = (130, 80, 46), (166, 108, 62), (186, 192, 214)
    cuerpo = pygame.Rect(x, y + 6, w, h - 6)
    if abierto:
        tapa = pygame.Rect(x + 1, y - 3, w - 2, 6)
        pygame.draw.rect(sup, contorno, tapa.inflate(2, 2))
        pygame.draw.rect(sup, (96, 58, 34), tapa)                                    # el revés de la tapa
    pygame.draw.rect(sup, contorno, cuerpo.inflate(2, 2))
    pygame.draw.rect(sup, madera, cuerpo)
    pygame.draw.rect(sup, claro, (x + 1, y + h - 3, w - 2, 1))                      # reflejo abajo
    for bx in (x + 3, x + w - 5):                                                    # herrajes
        pygame.draw.rect(sup, metal, (bx, y + 6, 2, h - 6))
    if abierto:
        pygame.draw.rect(sup, (24, 14, 18), (x + 1, y + 6, w - 2, 3))               # el interior, oscuro
    else:
        tapa = pygame.Rect(x, y, w, 7)
        pygame.draw.rect(sup, contorno, tapa.inflate(2, 2))
        pygame.draw.rect(sup, claro, tapa)
        for bx in (x + 3, x + w - 5):
            pygame.draw.rect(sup, metal, (bx, y, 2, 7))
        pygame.draw.rect(sup, (240, 200, 50), (x + w // 2 - 1, y + 5, 3, 3))        # cerradura
        pygame.draw.rect(sup, contorno, (x + w // 2, y + 6, 1, 1))


def flecha(sup, rect, direccion):
    """Flecha del borde: indica una salida a otro escenario (el titileo lo hace quien la dibuja)."""
    cx, cy = pygame.Rect(rect).center
    if direccion == "izquierda":
        puntos = [(cx - 4, cy), (cx + 3, cy - 6), (cx + 3, cy + 6)]
    elif direccion == "derecha":
        puntos = [(cx + 4, cy), (cx - 3, cy - 6), (cx - 3, cy + 6)]
    elif direccion == "arriba":
        puntos = [(cx, cy - 5), (cx - 6, cy + 3), (cx + 6, cy + 3)]
    else:   # abajo
        puntos = [(cx, cy + 5), (cx - 6, cy - 3), (cx + 6, cy - 3)]
    pygame.draw.polygon(sup, (255, 214, 102), puntos)
    pygame.draw.polygon(sup, (40, 24, 10), puntos, 1)
