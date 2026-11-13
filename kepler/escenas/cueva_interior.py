"""
kepler/escenas/cueva_interior.py
Escenario 3: el interior de la cueva. Al fondo, sobre un pedestal de roca, está el cristal de energía gigante, que
ilumina todo de celeste: la roca, los charcos, los racimos de cristales de las paredes y las estalactitas.

Se llega desde la entrada de la cueva, una vez que la compuerta está abierta y la cueva iluminada con la linterna.
La roca y los cristales fijos se pintan una vez en el fondo (kepler/arte_cueva.py); lo que se mueve (el halo del
cristal, el brillo, las motas de luz, las gotas y las ondas del agua) se dibuja en cada cuadro.
"""

import math

import pygame

from engine import Escena, ObjetoEscena
from kepler import arte_cueva
from kepler.config import ANCHO, ALTO_ESCENA
from kepler.sprites import dibujar_flecha

RECT_CRISTAL = pygame.Rect(130, 36, 60, 62)       # el cristal gigante (la base apoya en el pedestal, y=98)
Y_AGUA = (133, 137)                               # a qué altura queda el agua de cada charco


class EscenaCuevaInterior(Escena):
    def __init__(self, juego):
        self.juego = juego
        self.gotas = {}              # {x de la gota: (y de la punta, y del agua)}, lo arma construir_fondo
        # Igual que en las otras escenas: llega hasta los bordes, para que la flecha de salida sea alcanzable
        poligono = [(8, 112), (312, 112), (318, 147), (2, 147)]
        super().__init__("Interior de la cueva", (ANCHO, ALTO_ESCENA), poligono)
        sprites = juego.sprites
        (gx1, _), (gx2, _) = sorted(self.gotas.items())

        self.objetos = [
            ObjetoEscena("cristal de energía", tuple(RECT_CRISTAL), (160, 116),
                         dibujo=self.dibujar_cristal,
                         respuestas={
                             "Mirar": self.mirar_cristal,
                             "Usar": self.intentar_romper,
                             "Agarrar": self.intentar_romper,
                             "Hablar": "Brillás muy lindo. Sí, te estoy hablando a vos.",
                         },
                         usos={"pico": self.picar_cristal,
                               "cabeza_pico": lambda: "Sin mango no puedo darle un golpe fuerte."}),
            ObjetoEscena("cristales", (22, 62, 62, 48), (56, 120),
                         respuestas={
                             "Mirar": "Cristales más chicos. Brillan lindo, pero no tienen suficiente energía.",
                             "Agarrar": "Se rompen al tocarlos. No me sirven.",
                         }),
            ObjetoEscena("cristales de la pared", (236, 66, 58, 46), (264, 120),
                         respuestas={
                             "Mirar": "Más cristales, de colores. Ninguno tiene la energía del grande.",
                             "Agarrar": "Se rompen al tocarlos. No me sirven.",
                         }),
            ObjetoEscena("charco", (gx1 - 30, 128, 60, 14), (gx1, 126),
                         respuestas={
                             "Mirar": "Un charco de agua clara que gotea del techo y refleja el brillo del cristal.",
                             "Usar": "Agua de cueva. No tengo sed.",
                             "Agarrar": "Es solo agua.",
                         }),
            ObjetoEscena("charco chico", (gx2 - 22, 131, 44, 12), (gx2, 126),
                         respuestas={
                             "Mirar": "Otro charco, más chico. Las gotas del techo hacen ondas.",
                             "Agarrar": "Es solo agua.",
                         }),
            ObjetoEscena("ambiente", (0, 0, 0, 0), (160, 126), dibujo=self.dibujar_ambiente),
            ObjetoEscena("la salida", (0, 108, 14, 38), (12, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "izquierda", self.juego.tiempo),
                         salida=("cueva", (162, 126)),
                         respuestas={"Mirar": "Por ahí volvería a la entrada de la cueva."}),
        ]

    # ---------- Cristal ----------

    def dibujar_cristal(self, sup, rect):
        """El halo late detrás; el cristal, su brillo interno cambia suave y titilan los destellos."""
        t = self.juego.tiempo
        arte_cueva.halo(sup, RECT_CRISTAL.centerx, RECT_CRISTAL.centery + 6, t)
        arte_cueva.cristal_gigante(sup, RECT_CRISTAL.x, RECT_CRISTAL.bottom, RECT_CRISTAL.w, RECT_CRISTAL.h,
                                   brillo=math.sin(t * 2.4) * 0.8)
        arte_cueva.destellos(sup, RECT_CRISTAL, t)

    def dibujar_ambiente(self, sup, rect):
        """Motas de luz que suben alrededor del cristal y gotas que caen de las estalactitas a los charcos."""
        t = self.juego.tiempo
        arte_cueva.motas(sup, t)
        arte_cueva.goteras(sup, t, self.gotas)

    def mirar_cristal(self):
        if self.juego.progreso["cristal_minado"]:
            return "El cristal gigante. Ya le saqué un fragmento: con eso me alcanza."
        return "¡Un cristal de energía enorme! Brilla y está tibio."

    def intentar_romper(self):
        # Recién después de intentarlo la astronauta sabe que necesita algo para romperlo
        progreso = self.juego.progreso
        progreso["intento_romper_cristal"] = True
        if progreso["cristal_minado"]:
            return "No hay que ser avaricioso."
        return "Está demasiado duro, necesito romperlo de alguna forma."

    def picar_cristal(self):
        progreso = self.juego.progreso
        if progreso["cristal_minado"]:
            return "No hay que ser avaricioso."
        progreso["cristal_minado"] = True
        self.juego.inventario.agregar("cristal")
        return "¡Crac! Salió un fragmento de la punta. Tiene muchísima energía."

    # ---------- Fondo ----------

    def construir_fondo(self, sup):
        # 1) La pared lejana, con un túnel oscuro detrás del cristal
        arte_cueva.pared_del_fondo(sup)
        # 2) Los laterales: moles de roca en primer plano que miran al cristal
        arte_cueva.masa_de_roca(sup, [(0, 0), (40, 0), (32, 26), (46, 62), (30, 98), (42, 112), (0, 112)], 1, semilla=2)
        arte_cueva.masa_de_roca(sup, [(ANCHO, 0), (282, 0), (290, 30), (276, 66), (292, 100), (278, 112), (ANCHO, 112)],
                                -1, semilla=5)
        # 3) El techo con estalactitas
        puntas = arte_cueva.techo_con_estalactitas(sup)
        # 4) El piso, con los charcos justo debajo de dos estalactitas largas
        arte_cueva.piso(sup)
        largas = sorted(puntas, key=lambda p: -p[1])
        izq = min((p for p in largas[:8] if 60 < p[0] < 130), key=lambda p: -p[1], default=(92, 40))
        der = min((p for p in largas[:8] if 200 < p[0] < 262), key=lambda p: -p[1], default=(232, 36))
        self.gotas = {izq[0]: (izq[1], Y_AGUA[0]), der[0]: (der[1], Y_AGUA[1])}
        arte_cueva.charco(sup, izq[0], Y_AGUA[0], 30, 6)
        arte_cueva.charco(sup, der[0], Y_AGUA[1], 22, 5)
        # 5) El pedestal del cristal
        arte_cueva.masa_de_roca(sup, [(116, 112), (130, 100), (146, 93), (174, 93), (190, 100), (204, 112)], 2, semilla=9)
        for x, y, rx, ry in ((104, 118, 6, 3), (214, 120, 7, 4), (24, 128, 7, 4), (300, 130, 8, 4), (150, 140, 5, 3),
                             (260, 142, 5, 3)):
            arte_cueva.piedra(sup, x, y, rx, ry)
        # 6) Racimos de cristales de colores en las paredes y colgando del techo
        arte_cueva.racimo(sup, 30, 108, 36, 46, "cian")
        arte_cueva.racimo(sup, 70, 111, 16, 22, "violeta")
        arte_cueva.racimo(sup, 250, 108, 36, 42, "violeta")
        arte_cueva.racimo(sup, 234, 112, 14, 20, "verde")
        arte_cueva.racimo_colgante(sup, 58, 20, 16, 22, "violeta")
        arte_cueva.racimo_colgante(sup, 190, 20, 18, 24, "cian")
        arte_cueva.racimo_colgante(sup, 268, 22, 14, 16, "verde")
