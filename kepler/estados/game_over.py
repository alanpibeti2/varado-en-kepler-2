"""
kepler/estados/game_over.py
Estado GAME_OVER: se muestra cuando elegís un destino equivocado en la consola
y el cohete te deja en cualquier lado.
"""

import pygame

from engine import Estado, Boton, texto
from kepler import arte
from kepler.config import ANCHO, ALTO, AMARILLO, BLANCO, GRIS, COLORES_BOTON


class EstadoGameOver(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        self.boton_menu = Boton((ANCHO // 2 - 60, 150, 120, 16), "Volver al menú",
                                lambda: juego.cambiar_estado("MENU"), juego.fuentes["normal"], COLORES_BOTON)
        self.motivo = "Caíste en cualquier lado."

    def entrar(self):
        # El texto que explica el error se toma del último destino elegido
        self.motivo = getattr(self.juego, "motivo_game_over", "Caíste en cualquier lado.")

    def manejar_evento(self, evento):
        self.boton_menu.manejar_evento(evento)
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_RETURN, pygame.K_SPACE):
            self.juego.cambiar_estado("MENU")

    def dibujar(self, sup):
        sup.fill((6, 4, 16))
        arte.estrellas(sup, (0, 0, ANCHO, ALTO), 80, semilla=13, tiempo=self.juego.tiempo)
        fuentes = self.juego.fuentes
        texto(sup, "GAME OVER", fuentes["titulo"], (230, 80, 80), (ANCHO // 2, 60), ancla="center",
              sombra=(90, 20, 30))
        texto(sup, self.motivo, fuentes["normal"], BLANCO, (ANCHO // 2, 96), ancla="center")
        texto(sup, "El cohete no llegó a AZUL-3.", fuentes["chica"], GRIS, (ANCHO // 2, 116), ancla="center")
        self.boton_menu.dibujar(sup)
