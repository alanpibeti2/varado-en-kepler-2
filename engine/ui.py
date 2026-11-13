"""
engine/ui.py
Interfaz en estilo 16 bits: textos sin suavizado, paneles con relieve,
degradados por bandas y botones.
"""

import pygame

# Colores por defecto de los botones (el juego puede pasar los suyos)
COLORES_POR_DEFECTO = {
    "fondo": (52, 40, 90),
    "fondo_activo": (96, 74, 150),
    "luz": (130, 110, 200),
    "sombra": (20, 14, 40),
    "texto": (235, 230, 255),
    "texto_activo": (255, 220, 110),
    "texto_apagado": (110, 100, 140),
}


# ---------------------------------------------------------------------- #
#  Textos
# ---------------------------------------------------------------------- #

def texto(superficie, contenido, fuente, color, pos, ancla="topleft", sombra=(0, 0, 0)):
    """
    Escribe un texto con una sombra de 1 píxel abajo a la derecha.
    'ancla' indica qué punto del texto se ubica en 'pos'
    (por ejemplo "center", "midtop", "topleft").
    El False de render() desactiva el suavizado: así las letras quedan pixeladas.
    """
    imagen = fuente.render(contenido, False, color)
    rect = imagen.get_rect(**{ancla: pos})
    if sombra is not None:
        superficie.blit(fuente.render(contenido, False, sombra), rect.move(1, 1))
    superficie.blit(imagen, rect)
    return rect


def envolver_texto(contenido, fuente, ancho_max):
    """Corta un texto largo en varias líneas que entren en 'ancho_max' píxeles."""
    palabras = contenido.split()
    lineas = []
    actual = ""
    for palabra in palabras:
        prueba = palabra if not actual else actual + " " + palabra
        if fuente.size(prueba)[0] <= ancho_max:
            actual = prueba
        else:
            if actual:
                lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


# ---------------------------------------------------------------------- #
#  Efectos de dibujo
# ---------------------------------------------------------------------- #

def panel(superficie, rect, fondo, luz, sombra, borde=(0, 0, 0)):
    """
    Panel con relieve, como las ventanas de los juegos de SNES:
    borde negro, línea clara arriba/izquierda y oscura abajo/derecha.
    Si se invierten 'luz' y 'sombra', el panel parece hundido.
    """
    r = pygame.Rect(rect)
    pygame.draw.rect(superficie, borde, r)
    interior = r.inflate(-2, -2)
    pygame.draw.rect(superficie, fondo, interior)
    pygame.draw.line(superficie, luz, interior.topleft, (interior.right - 1, interior.top))
    pygame.draw.line(superficie, luz, interior.topleft, (interior.left, interior.bottom - 1))
    pygame.draw.line(superficie, sombra, (interior.left, interior.bottom - 1),
                     (interior.right - 1, interior.bottom - 1))
    pygame.draw.line(superficie, sombra, (interior.right - 1, interior.top),
                     (interior.right - 1, interior.bottom - 1))


def bandas(superficie, rect, colores):
    """
    Degradado "por bandas": divide el rectángulo en franjas horizontales,
    una por color. Es el típico cielo de los juegos de 16 bits.
    """
    x, y, ancho, alto = rect
    alto_banda = alto / len(colores)
    for i, color in enumerate(colores):
        y0 = y + round(i * alto_banda)
        y1 = y + round((i + 1) * alto_banda)
        pygame.draw.rect(superficie, color, (x, y0, ancho, y1 - y0))


def oscurecer(superficie, opacidad=150):
    """Tapa la pantalla con una capa negra semitransparente (0 a 255)."""
    capa = pygame.Surface(superficie.get_size(), pygame.SRCALPHA)
    capa.fill((0, 0, 0, opacidad))
    superficie.blit(capa, (0, 0))


# ---------------------------------------------------------------------- #
#  Botón
# ---------------------------------------------------------------------- #

class Boton:
    """
    Botón con texto que ejecuta una función al hacerle clic.
    Se ilumina con el mouse encima o cuando está "activo" (ej: el verbo elegido).
    Si 'habilitado' es False, se ve apagado y no responde.
    """

    def __init__(self, rect, texto_boton, al_hacer_clic, fuente, colores=None, icono=None):
        self.rect = pygame.Rect(rect)
        self.texto = texto_boton
        self.al_hacer_clic = al_hacer_clic
        self.fuente = fuente
        self.colores = colores or COLORES_POR_DEFECTO
        self.icono = icono          # Surface opcional que se dibuja a la izquierda
        self.habilitado = True

    def manejar_evento(self, evento):
        """Devuelve True si el clic cayó sobre el botón (y lo atendió)."""
        if not self.habilitado:
            return False
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if self.rect.collidepoint(evento.pos):
                self.al_hacer_clic()
                return True
        return False

    def dibujar(self, superficie, activo=False):
        c = self.colores
        encima = self.habilitado and self.rect.collidepoint(pygame.mouse.get_pos())
        resaltado = activo or encima
        panel(superficie, self.rect, c["fondo_activo"] if resaltado else c["fondo"],
              c["luz"], c["sombra"])

        centro = self.rect.center
        if self.icono is not None:
            alto_icono = self.icono.get_height()
            superficie.blit(self.icono, (self.rect.x + 4, self.rect.centery - alto_icono // 2))
            centro = (self.rect.centerx + self.icono.get_width() // 2 + 2, self.rect.centery)

        if not self.habilitado:
            color = c["texto_apagado"]
        else:
            color = c["texto_activo"] if resaltado else c["texto"]
        texto(superficie, self.texto, self.fuente, color, centro, ancla="center")
