"""
kepler/glifos.py
El alfabeto alienígena: 10 símbolos raros (uno por cada dígito del 0 al 9) dibujados en píxeles.

Se usan en el tablero de la compuerta de la mina (las teclas y lo que se teclea) y en lo que
dice R-7 cuando da el código. Para poder escribirlos dentro de un texto normal, cada símbolo es un
carácter "privado" (\\ue000 a \\ue009), y FuenteConGlifos sabe dibujarlos en lugar de las letras.

    glifos("471")   ->  los símbolos del 4, el 7 y el 1, separados por espacios
"""

import pygame

PRIMER_GLIFO = 0xE000          # el carácter del símbolo 0; el símbolo n es PRIMER_GLIFO + n
ANCHO_GLIFO, ALTO_GLIFO = 5, 7

BITMAPS = [
    (".###.", "#...#", "#.#.#", "#...#", ".###.", "..#..", ".###."),     # 0: ojo sobre un pie
    ("#.#.#", "#.#.#", "#.#.#", "#####", "..#..", "..#..", "..#.."),     # 1: tridente
    ("####.", "...#.", ".#.#.", ".#.#.", ".#...", ".####", "....."),     # 2: espiral
    ("#####", ".#.#.", "..#..", ".#.#.", "#####", "..#..", "#####"),     # 3: reloj de arena
    ("..##.", ".##..", "##...", ".###.", "...##", "..##.", ".##.."),     # 4: rayo
    ("#.#.#", ".###.", "#####", ".###.", "#.#.#", "..#..", "..#.."),     # 5: estrella
    ("#...#", "##.##", "#.#.#", "#...#", ".###.", "..#..", ".###."),     # 6: cuernos
    ("..###", ".#..#", "#...#", "#####", "#...#", "#...#", "#####"),     # 7: cubo
    ("#..#.", ".##.#", "....#", "###..", "..###", ".#..#", "#.##."),     # 8: olas
    (".###.", "#####", "#.#.#", "#####", ".###.", "..#..", "#####"),     # 9: planeta con anillo
]


def glifo(digito):
    """El carácter del símbolo que corresponde a un dígito (0 a 9)."""
    return chr(PRIMER_GLIFO + int(digito))


def glifos(digitos):
    """Los símbolos de una serie de dígitos, separados por espacios (para escribirlos en un texto)."""
    return " ".join(glifo(d) for d in digitos)


def imagen_glifo(digito, color, escala=1):
    """La imagen (con transparencia) del símbolo de un dígito, del color y tamaño pedidos."""
    imagen = pygame.Surface((ANCHO_GLIFO, ALTO_GLIFO), pygame.SRCALPHA)
    for y, fila in enumerate(BITMAPS[int(digito)]):
        for x, punto in enumerate(fila):
            if punto == "#":
                imagen.set_at((x, y), color)
    if escala != 1:
        imagen = pygame.transform.scale(imagen, (ANCHO_GLIFO * escala, ALTO_GLIFO * escala))
    return imagen


def _es_glifo(caracter):
    return PRIMER_GLIFO <= ord(caracter) < PRIMER_GLIFO + len(BITMAPS)


class FuenteConGlifos:
    """
    Envuelve una fuente de pygame y le enseña a dibujar los símbolos alienígenas dentro de un texto.
    Tiene los mismos métodos que usa el resto del juego (render, size, get_height).
    """

    ESPACIO = 1     # separación (en píxeles) a cada lado de un símbolo

    def __init__(self, base):
        self.base = base

    def get_height(self):
        return self.base.get_height()

    def _tramos(self, contenido):
        """Parte el texto en tramos: (es_glifo, texto o dígito)."""
        tramo, tramos = "", []
        for caracter in contenido:
            if _es_glifo(caracter):
                if tramo:
                    tramos.append((False, tramo))
                    tramo = ""
                tramos.append((True, ord(caracter) - PRIMER_GLIFO))
            else:
                tramo += caracter
        if tramo:
            tramos.append((False, tramo))
        return tramos

    def size(self, contenido):
        ancho = 0
        for es_glifo, dato in self._tramos(contenido):
            ancho += (ANCHO_GLIFO + 2 * self.ESPACIO) if es_glifo else self.base.size(dato)[0]
        return ancho, self.base.get_height()

    def render(self, contenido, suavizado, color, fondo=None):
        ancho, alto = self.size(contenido)
        imagen = pygame.Surface((max(1, ancho), alto), pygame.SRCALPHA)
        x = 0
        for es_glifo, dato in self._tramos(contenido):
            if es_glifo:
                imagen.blit(imagen_glifo(dato, color), (x + self.ESPACIO, (alto - ALTO_GLIFO) // 2))
                x += ANCHO_GLIFO + 2 * self.ESPACIO
            else:
                trozo = self.base.render(dato, suavizado, color)
                imagen.blit(trozo, (x, 0))
                x += trozo.get_width()
        return imagen
