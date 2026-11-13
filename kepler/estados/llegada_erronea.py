"""
kepler/estados/llegada_erronea.py
Estado LLEGADA_ERRONEA: el cohete viaja hacia el planeta que elegiste mal,
aterriza ahí y después aparece el game over.
"""

import math
import random

import pygame

from engine import Estado, texto
from kepler import arte
from kepler.config import ANCHO, ALTO, AMARILLO, BLANCO

DURACION = 5.0            # segundos hasta el game over
ATERRIZAJE = 3.0          # segundos hasta que el cohete toca el planeta

# Colores de cada planeta equivocado: (color, sombra, franja)
PLANETAS = {
    "ROJO-1": ((190, 74, 56), (130, 44, 44), (210, 96, 66)),
    "VERDE-2": ((80, 170, 100), (40, 110, 70), (120, 210, 140)),
}


class EstadoLlegadaErronea(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        azar = random.Random(9)
        self.estrellas = [(azar.randrange(ANCHO), azar.randrange(ALTO), azar.choice((20, 40, 80)))
                          for _ in range(90)]
        self.t = 0.0
        self.destino = "ROJO-1"

    def entrar(self):
        self.t = 0.0
        self.destino = self.juego.destino_erroneo

    def manejar_evento(self, evento):
        # Un clic o una tecla saltan al game over (después de un segundo, para no saltar por accidente)
        if self.t > 1 and evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.juego.cambiar_estado("GAME_OVER")

    def actualizar(self, dt):
        self.t += dt
        if self.t > DURACION:
            self.juego.cambiar_estado("GAME_OVER")

    def dibujar(self, sup):
        t = self.t
        color, sombra, franja = PLANETAS[self.destino]
        sup.fill((6, 4, 16))
        for x0, y, velocidad in self.estrellas:
            x = int(x0 - t * velocidad) % ANCHO
            brillo = 90 + velocidad * 2
            sup.set_at((x, y), (brillo, brillo, min(255, brillo + 30)))

        # El planeta crece a medida que el cohete se acerca
        centro = (244, 92)
        radio = int(min(44, 8 + t * 12))
        arte.planeta(sup, centro, radio, color, sombra, franja=franja)

        # El cohete avanza hasta el borde del planeta y se queda ahí
        x_final = centro[0] - radio - 6
        progreso = min(1.0, t / ATERRIZAJE)
        x = int(-20 + (x_final + 20) * progreso)
        y = int(92 + math.sin(t * 3) * 2 * (1 - progreso))
        if progreso < 1.0:   # llama solo mientras viaja
            largo_llama = 4 + int(t * 20) % 4
            pygame.draw.rect(sup, (255, 160, 40), (x - largo_llama, y - 2, largo_llama, 4))
            pygame.draw.rect(sup, (255, 240, 120), (x - largo_llama // 2, y - 1, largo_llama // 2, 2))
        cohete = self.juego.sprites["cohete_chico"]
        sup.blit(cohete, cohete.get_rect(midleft=(x, y)))

        fuentes = self.juego.fuentes
        if t < ATERRIZAJE:
            texto(sup, f"Llegando a {self.destino}...", fuentes["normal"], BLANCO, (ANCHO // 2, 30),
                  ancla="center")
        else:
            texto(sup, "¡Caíste en cualquier lado!", fuentes["titulo"], AMARILLO, (ANCHO // 2, 30),
                  ancla="center", sombra=(90, 30, 40))
