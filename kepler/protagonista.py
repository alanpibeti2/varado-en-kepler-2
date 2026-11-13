"""
kepler/protagonista.py
La astronauta protagonista.

Hereda de Actor (del engine), que ya sabe caminar y hablar. Acá solo
definimos CÓMO SE VE: elige qué cuadro del sprite mostrar y hacia dónde mira.
"""

import pygame

from engine import Actor, espejar
from kepler.config import TEXTO_HABLA


class Astronauta(Actor):
    def __init__(self, x, y, sprites):
        super().__init__(x, y, velocidad=70, color_texto=TEXTO_HABLA)
        # Cuadros mirando a la derecha: [quieta, pisada, pierna izq. arriba, pierna der. arriba]
        self.cuadros_derecha = [sprites["astronauta_quieto"], sprites["astronauta_paso"],
                                sprites["astronauta_alza_izq"], sprites["astronauta_alza_der"]]
        # ...y los mismos espejados, para mirar a la izquierda
        self.cuadros_izquierda = [espejar(cuadro) for cuadro in self.cuadros_derecha]

    # Ciclo de caminata de 4 fases: pisada, pierna izq. arriba, pisada, pierna der. arriba.
    # En la pisada el cuerpo está más bajo; al pasar una pierna, sube 1 píxel (el "rebote").
    CICLO = [(1, 0), (2, -1), (1, 0), (3, -1)]    # (cuadro, desplazamiento vertical)
    FASES_POR_SEGUNDO = 7

    def dibujar(self, sup, fuente):
        cuadros = self.cuadros_derecha if self.mirando_derecha else self.cuadros_izquierda
        rebote = 0
        if self.caminando:
            indice, rebote = self.CICLO[int(self.tiempo_animacion * self.FASES_POR_SEGUNDO) % len(self.CICLO)]
            cuadro = cuadros[indice]
        else:
            cuadro = cuadros[0]

        x, y = int(self.x), int(self.y)
        pygame.draw.ellipse(sup, (30, 20, 30), (x - 8, y - 2, 16, 4))   # sombra
        rect = cuadro.get_rect(midbottom=(x, y + rebote))                # los pies en (x, y)
        sup.blit(cuadro, rect)

        self.dibujar_texto(sup, fuente, rect.top)
