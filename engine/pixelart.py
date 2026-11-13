"""
engine/pixelart.py
Herramientas para crear sprites de pixel art SIN archivos de imagen.

Un sprite se "dibuja" como una lista de textos, donde cada letra es un
píxel y cada letra tiene un color en la PALETA. El punto '.' es transparente.

Ejemplo (un corazón de 5x4 píxeles):
    filas = [
        ".R.R.",
        "RRRRR",
        ".RRR.",
        "..R..",
    ]
    paleta = {"R": (230, 40, 60)}
    corazon = crear_sprite(filas, paleta)

Es la misma idea que usaban las consolas de 16 bits: imágenes chiquitas
con pocos colores (una paleta), dibujadas píxel por píxel.
"""

import pygame


def crear_sprite(filas, paleta, contorno=None):
    """
    Convierte la lista de textos en una Surface de pygame.
    Si se pasa un color de 'contorno', le agrega un borde de 1 píxel
    alrededor (típico del pixel art, ayuda a que se lea sobre cualquier fondo).
    """
    ancho = len(filas[0])
    for i, fila in enumerate(filas):
        if len(fila) != ancho:
            raise ValueError(f"La fila {i} mide {len(fila)} y debería medir {ancho}: '{fila}'")

    sprite = pygame.Surface((ancho, len(filas)), pygame.SRCALPHA)   # SRCALPHA = con transparencia
    for y, fila in enumerate(filas):
        for x, letra in enumerate(fila):
            if letra != ".":
                sprite.set_at((x, y), paleta[letra])   # pinta un píxel
    if contorno is not None:
        sprite = agregar_contorno(sprite, contorno)
    return sprite


def agregar_contorno(sprite, color):
    """
    Devuelve una copia del sprite con un borde de 1 píxel.
    Por cada píxel visible, pinta del color del borde sus 4 vecinos
    (arriba, abajo, izquierda, derecha) y después pega el sprite encima.
    """
    ancho, alto = sprite.get_size()
    resultado = pygame.Surface((ancho + 2, alto + 2), pygame.SRCALPHA)
    for y in range(alto):
        for x in range(ancho):
            if sprite.get_at((x, y)).a > 0:                     # .a = opacidad del píxel
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    resultado.set_at((x + 1 + dx, y + 1 + dy), color)
    resultado.blit(sprite, (1, 1))
    return resultado


def espejar(sprite):
    """Da vuelta el sprite horizontalmente (para mirar hacia el otro lado)."""
    return pygame.transform.flip(sprite, True, False)


def escalar(sprite, factor):
    """Agranda el sprite un número entero de veces, sin suavizar los píxeles."""
    ancho, alto = sprite.get_size()
    return pygame.transform.scale(sprite, (ancho * factor, alto * factor))
