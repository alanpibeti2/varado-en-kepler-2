"""
engine/navegacion.py
Por dónde puede caminar un personaje.

La zona caminable es un POLÍGONO: una lista de puntos (x, y) que marcan
el contorno del piso. Un personaje solo puede pararse dentro de él.
"""

import pygame


def punto_en_poligono(punto, poligono):
    """
    Algoritmo de "ray casting" (lanzar un rayo):
    Desde el punto trazamos una línea imaginaria hacia la derecha y contamos
    cuántos bordes del polígono cruza.
      - Cantidad impar  -> el punto está ADENTRO.
      - Cantidad par    -> el punto está AFUERA.
    """
    x, y = punto
    dentro = False
    n = len(poligono)
    j = n - 1
    for i in range(n):
        xi, yi = poligono[i]
        xj, yj = poligono[j]
        # ¿El borde (i, j) cruza la altura 'y' del punto?
        if (yi > y) != (yj > y):
            # Coordenada x donde el borde corta esa altura
            x_cruce = xi + (y - yi) * (xj - xi) / (yj - yi)
            if x < x_cruce:
                dentro = not dentro
        j = i
    return dentro


class ZonaCaminable:
    def __init__(self, poligono):
        self.poligono = poligono

    def contiene(self, punto):
        return punto_en_poligono(punto, self.poligono)

    def dibujar_debug(self, superficie, color=(0, 255, 120)):
        """Dibuja el polígono (para depurar)."""
        pygame.draw.polygon(superficie, color, self.poligono, 1)
