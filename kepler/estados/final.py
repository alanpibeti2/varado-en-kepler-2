"""
kepler/estados/final.py
Estado FINAL: el cohete viaja por el espacio y llega a AZUL-3, el planeta de la astronauta.
"""

import math
import random

import pygame

from engine import Estado, Boton, texto
from kepler import arte
from kepler.config import ANCHO, ALTO, AMARILLO, BLANCO, COLORES_BOTON


class EstadoFinal(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        azar = random.Random(5)
        # Cada estrella: (x inicial, y, velocidad). Las más rápidas parecen más cercanas.
        self.estrellas = [(azar.randrange(ANCHO), azar.randrange(ALTO), azar.choice((20, 40, 80)))
                          for _ in range(90)]
        self.boton_menu = Boton((ANCHO // 2 - 60, 172, 120, 16), "Volver al menú",
                                lambda: juego.cambiar_estado("MENU"), juego.fuentes["normal"], COLORES_BOTON)
        self.t = 0.0
        self.video_visto = False            # el video final se muestra una vez, después de la animación
        self.volviendo_del_video = False    # lo prende el estado VIDEO al terminar, para no reiniciar la animación

    def entrar(self):
        if self.volviendo_del_video:        # vuelve del video: la pantalla final sigue como estaba
            self.volviendo_del_video = False
            return
        self.t = 0.0    # la animación arranca de cero cada vez
        self.video_visto = False

    def manejar_evento(self, evento):
        if self.video_visto:
            self.boton_menu.manejar_evento(evento)

    def actualizar(self, dt):
        self.t += dt
        if self.t > 5.5 and not self.video_visto:    # terminó la animación: se pasa el video final
            self.video_visto = True
            self.juego.cambiar_estado("VIDEO")

    def dibujar(self, sup):
        t = self.t
        sup.fill((6, 4, 16))
        for x0, y, velocidad in self.estrellas:          # estrellas que pasan hacia la izquierda
            x = int(x0 - t * velocidad) % ANCHO
            brillo = 90 + velocidad * 2
            sup.set_at((x, y), (brillo, brillo, min(255, brillo + 30)))

        radio = int(min(44, 8 + t * 10))                 # el planeta se acerca (crece)
        arte.planeta(sup, (244, 92), radio, (70, 140, 230), (40, 80, 170), franja=(110, 190, 120),
                     anillo=(210, 220, 245))

        cohete = self.juego.sprites["cohete_chico"]
        x = int(min(120, -20 + t * 45))                  # el cohete avanza hasta el centro
        y = int(92 + math.sin(t * 3) * 2)
        largo_llama = 4 + int(t * 20) % 4                # la llama titila
        pygame.draw.rect(sup, (255, 160, 40), (x - largo_llama, y - 2, largo_llama, 4))
        pygame.draw.rect(sup, (255, 240, 120), (x - largo_llama // 2, y - 1, largo_llama // 2, 2))
        sup.blit(cohete, cohete.get_rect(midleft=(x, y)))

        fuentes = self.juego.fuentes
        if t > 3.2:
            texto(sup, "¡LLEGASTE A CASA!", fuentes["titulo"], AMARILLO, (ANCHO // 2, 30), ancla="center",
                  sombra=(60, 30, 80))
        if t > 4:
            texto(sup, "Gracias por jugar Varado en Kepler", fuentes["normal"], BLANCO, (ANCHO // 2, 152),
                  ancla="center")
            if self.video_visto:
                self.boton_menu.dibujar(sup)
