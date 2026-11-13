"""
kepler/escenas/plataforma.py
Escenario 3: la plataforma de lanzamiento con el cohete abandonado.

PUZLE FINAL:
  Se llega comprando un boleto (ver boleteria.py). El cohete ya está listo:
  usar la consola -> elegir el destino correcto (AZUL-3, la pista del robot).
"""

import os

import pygame

from engine import Escena, ObjetoEscena, bandas, rellenar_textura
from kepler import arte, arte16, paisaje
from kepler.config import ANCHO, ALTO_ESCENA, CARPETA_FONDOS
from kepler.sprites import dibujar_objeto, dibujar_flecha
from kepler.dialogos import dialogo_consola


class EscenaPlataforma(Escena):
    def __init__(self, juego):
        self.juego = juego
        poligono = [(20, 110), (300, 110), (318, 147), (2, 147)]
        super().__init__("Plataforma de lanzamiento", (ANCHO, ALTO_ESCENA), poligono,
                         ruta_fondo=os.path.join(CARPETA_FONDOS, "plataforma.png"))

        self.objetos = [
            ObjetoEscena("cohete", (220, 18, 44, 92), (236, 120),
                         dibujo=self.dibujar_cohete,
                         respuestas={
                             "Mirar": self.mirar_cohete,
                             "Usar": self.usar_cohete,
                             "Agarrar": "Ja. No.",
                             "Hablar": "Vamos, cohete, vos podés.",
                         }),
            ObjetoEscena("consola", (110, 86, 30, 26), (125, 118),
                         dibujo=self.dibujar_consola,
                         respuestas={
                             "Mirar": self.mirar_consola,
                             "Usar": self.usar_consola,
                             "Hablar": "BIP BIP. No, así no funciona.",
                             "Agarrar": "Está fija al piso.",
                         }),
            ObjetoEscena("la entrada", (306, 110, 14, 36), (300, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, self.juego.sprites, r, "derecha", self.juego.tiempo),
                         salida=("boleteria", (62, 126)),
                         respuestas={"Mirar": "Por ahí se vuelve a la entrada, donde está la boletería."}),
        ]

    def dibujar_cohete(self, sup, rect):
        dibujar_objeto(sup, self.juego.sprites, "cohete_encendido", rect)     # el cohete está listo
        arte.luces_cohete(sup, rect, True, self.juego.tiempo)

    def dibujar_consola(self, sup, rect):
        dibujar_objeto(sup, self.juego.sprites, "consola_encendida", rect)
        arte.pantalla_consola(sup, rect, True, self.juego.tiempo)

    # ---------- Fondo ----------

    def construir_fondo(self, sup):
        paisaje.cielo(sup)       # el mismo cielo que en las demás pantallas de exterior
        for x, r in ((30, 18), (74, 12), (150, 14)):    # domos de la base, a lo lejos
            arte16.cupula(sup, x, 100, r)
        pygame.draw.rect(sup, (40, 34, 56), (0, 96, ANCHO, 4))
        # Torre de lanzamiento (detrás del cohete)
        arte16.torre(sup, 272, 284, 14, 104)
        pygame.draw.line(sup, (150, 118, 116), (256, 44), (272, 44), 2)    # brazo de la torre
        pygame.draw.line(sup, (210, 176, 164), (256, 43), (272, 43))
        # Piso metálico
        bandas(sup, (0, 100, ANCHO, ALTO_ESCENA - 100), [(70, 72, 92), (82, 84, 106), (94, 96, 120),
                                                         (104, 106, 130), (112, 114, 138)])
        rellenar_textura(sup, self.juego.sprites["textura_piso_metal"], (0, 103, ANCHO, ALTO_ESCENA - 103))
        for i in range(0, ANCHO, 8):   # borde de seguridad amarillo y negro
            pygame.draw.rect(sup, (230, 190, 40), (i, 100, 4, 3))

    # ---------- Cohete ----------

    def mirar_cohete(self):
        return "Un cohete viejo pero entero. Parece listo para despegar. Falta elegir el destino en la consola."

    def usar_cohete(self):
        return "Primero tengo que elegir el destino en la consola."

    # ---------- Consola ----------

    def mirar_consola(self):
        return "La consola de control del cohete. Está encendida y pide un destino."

    def usar_consola(self):
        self.juego.iniciar_dialogo(dialogo_consola(self.juego))
        return None
