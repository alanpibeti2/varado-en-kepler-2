"""
kepler/escenas/choque.py
Escenario 1: el sitio del choque. Acá arranca el juego.

Está la nave estrellada (un transbordador enorme, con humo que sube; se puede entrar), a un costado la
caja negra naranja con un palo y una cuerda adentro, y los caminos hacia la plataforma (izquierda) y la cueva (derecha).
"""

import os

import pygame

from engine import Escena, ObjetoEscena, bandas, rellenar_textura
from kepler import paisaje, arte16
from kepler.config import ANCHO, ALTO_ESCENA, CARPETA_FONDOS
from kepler.sprites import dibujar_objeto, dibujar_flecha


class EscenaChoque(Escena):
    def __init__(self, juego):
        self.juego = juego   # antes de super(), porque construir_fondo puede necesitarlo
        poligono = [(8, 104), (312, 104), (318, 147), (2, 147)]
        super().__init__("Sitio del choque", (ANCHO, ALTO_ESCENA), poligono,
                         ruta_fondo=os.path.join(CARPETA_FONDOS, "choque.png"))
        sprites = juego.sprites

        self.objetos = [
            ObjetoEscena("nave", arte16.RECT_CLIC_NAVE, (140, 122),
                         dibujo=self.dibujar_nave,
                         salida=("capsula_interior", (30, 128)),
                         respuestas={
                             "Mirar": "Mi nave de escape. Quedó hecha chatarra.",
                             "Usar": self.entrar_capsula,
                             "Agarrar": "Pesa una tonelada.",
                             "Hablar": "Nave, estoy muy decepcionado de vos.",
                         }),
            ObjetoEscena("caja negra", (266, 98, 20, 14), (276, 120),
                         dibujo=self.dibujar_cofre,
                         respuestas={
                             "Mirar": self.mirar_cofre,
                             "Usar": self.abrir_cofre,
                             "Agarrar": "Pesa demasiado para llevármelo.",
                             "Hablar": "No creo que una caja me conteste.",
                         }),
            # El palo se ve asomando del cofre recién cuando lo abrís
            ObjetoEscena("palo", (268, 91, 12, 12), (276, 120),
                         dibujo=lambda sup, r: sup.blit(sprites["palo"], r),
                         visible_si=lambda: self.juego.progreso["cofre_abierto"],
                         respuestas={
                             "Mirar": "No puse nada porque me re colgué... ¿Para qué quiero un palo?",
                             "Agarrar": self.coger_palo,
                         }),
            ObjetoEscena("cuerda", (277, 95, 12, 12), (276, 120),
                         dibujo=lambda sup, r: sup.blit(sprites["cuerda"], r),
                         visible_si=lambda: self.juego.progreso["cofre_abierto"],
                         respuestas={
                             "Mirar": "Una cuerda enrollada. Tampoco la puse yo.",
                             "Agarrar": self.coger_cuerda,
                         }),
            # Salidas a los otros escenarios
            ObjetoEscena("la plataforma", (0, 104, 14, 40), (12, 126),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "izquierda", self.juego.tiempo),
                         salida=("boleteria", (296, 126)),
                         respuestas={"Mirar": "Por ahí se ve una base con una plataforma de lanzamiento."}),
            ObjetoEscena("la cueva", (306, 104, 14, 40), (308, 126),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "derecha", self.juego.tiempo),
                         salida=("cueva", (24, 126)),
                         respuestas={"Mirar": "Un camino hacia unas rocas enormes."}),
        ]

    # ---------- Fondo ----------

    def construir_fondo(self, sup):
        paisaje.fondo_choque(sup)      # cielo compartido + montañas, dunas y rocas con estilo de 16 bits

    # ---------- Cápsula ----------

    def dibujar_nave(self, sup, rect):
        """La nave estrellada y su humo, que sube y se mueve. (Se dibuja entera, aunque se la pueda tocar solo arriba.)"""
        dibujar_objeto(sup, self.juego.sprites, "capsula", pygame.Rect(arte16.RECT_NAVE))
        arte16.humo_animado(sup, *arte16.ORIGEN_HUMO_NAVE, self.juego.tiempo, bolas=10, altura=30, escala=1.5)

    def entrar_capsula(self):
        self.juego.ir_a_escena("capsula_interior", (30, 128))
        return None   # no dice nada: cambia de escenario

    # ---------- Cofre ----------

    def dibujar_cofre(self, sup, rect):
        nombre = "cofre_abierto" if self.juego.progreso["cofre_abierto"] else "cofre_cerrado"
        dibujar_objeto(sup, self.juego.sprites, nombre, rect)

    def mirar_cofre(self):
        if not self.juego.progreso["cofre_abierto"]:
            return "Una caja negra de emergencia. Es naranja para que se encuentre entre los restos."
        if self.palo in self.objetos:
            return "No puse nada porque me re colgué... ¿Para qué quiero un palo?"
        if self.cuerda in self.objetos:
            return "Todavía hay cosas adentro."
        return "La caja negra, abierta y vacía."

    def abrir_cofre(self):
        progreso = self.juego.progreso
        if progreso["cofre_abierto"]:
            return "Ya está abierto."
        progreso["cofre_abierto"] = True
        return "La abrí. Adentro hay un palo y una cuerda."

    def coger_palo(self):
        self.juego.inventario.agregar("palo")
        self.quitar_objeto(self.palo)
        return "Es un simple palo, pero me lo llevo igual."

    def coger_cuerda(self):
        self.juego.inventario.agregar("cuerda")
        self.quitar_objeto(self.cuerda)
        return "Una cuerda. Esta sí puede servir."

    @property
    def cuerda(self):
        return next((o for o in self.objetos if o.nombre == "cuerda"), None)

    @property
    def palo(self):
        return next((o for o in self.objetos if o.nombre == "palo"), None)
