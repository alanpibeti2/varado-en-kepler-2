"""
kepler/escenas/boleteria.py
Escenario: la entrada a la plataforma de lanzamiento, con la boletería al frente.

  1. Usar los billetes en la boletería -> te da un boleto.
  2. Usar el boleto en la puerta de acceso (una valla que cruza todo el piso) -> se abre.
  3. Atravesarla hacia la izquierda: ese es el camino a la plataforma.
Sin boleto no se puede acceder a la zona del cohete.
"""

import random

import pygame

from engine import Escena, ObjetoEscena, bandas, rellenar_textura, texto
from kepler import paisaje, arte16
from kepler.config import ANCHO, ALTO_ESCENA, MARRON_CARTEL
from kepler.sprites import dibujar_flecha, dibujar_objeto
from kepler.dialogos import dialogo_boletero

# La puerta de acceso es una valla que cruza todo el piso, del horizonte al borde de abajo,
# y corta el camino hacia la plataforma. No sube al cielo.
PUERTA = pygame.Rect(0, 94, 38, ALTO_ESCENA - 94)
ZONA_PUERTA = pygame.Rect(0, 94, 50, ALTO_ESCENA - 94)   # PUERTA + la ranura para el boleto, que clickeás


class EscenaBoleteria(Escena):
    def __init__(self, juego):
        self.juego = juego
        poligono = [(50, 110), (312, 110), (318, 147), (50, 147)]    # la puerta ocupa el borde izquierdo
        super().__init__("Entrada a la plataforma", (ANCHO, ALTO_ESCENA), poligono)
        sprites = juego.sprites

        self.objetos = [
            ObjetoEscena("boletería", (148, 46, 66, 64), (182, 122),
                         dibujo=self.dibujar_boleteria,
                         respuestas={
                             "Mirar": self.mirar_boleteria,
                             "Usar": self.usar_boleteria,
                             "Hablar": self.hablar_boletero,
                             "Agarrar": "Está atornillada al piso.",
                         },
                         usos={"plata": self.comprar_boleto,
                               "billetera_vacia": lambda: "Ya no me queda cambio."}),
            # El boletero va después de la boletería para que los clics sobre él lo atiendan a él (se dibuja con ella)
            ObjetoEscena("boletero", (172, 72, 18, 18), (182, 122),
                         visible_si=self.atiende,
                         respuestas={
                             "Mirar": "Un alien de bigote enorme atiende la boletería. Parece aburrido.",
                             "Hablar": self.hablar_boletero,
                             "Usar": "No creo que le guste que lo use.",
                             "Agarrar": "No voy a cargar a un alien.",
                         },
                         # Los billetes también se le pueden dar a él (el boletero está parado justo sobre la ventanilla)
                         usos={"plata": self.comprar_boleto,
                               "billetera_vacia": lambda: "Ya no me queda cambio."}),
            ObjetoEscena("puerta de acceso", ZONA_PUERTA, (62, 126),
                         dibujo=lambda sup, r: self.dibujar_puerta(sup),
                         respuestas={
                             "Mirar": self.mirar_puerta,
                             "Usar": self.usar_puerta,
                             "Hablar": "Puerta, ¿me dejás pasar? ...No contesta.",
                             "Agarrar": "Está soldada a la pared.",
                         },
                         usos={"boleto": self.pasar_puerta}),
            # Con la puerta abierta, el camino sigue hacia la izquierda, atravesándola
            ObjetoEscena("la plataforma", ZONA_PUERTA, (62, 126),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "izquierda", self.juego.tiempo),
                         visible_si=lambda: self.juego.progreso["boleto_usado"],
                         salida=("plataforma", (296, 126)),
                         respuestas={"Mirar": "Por la puerta se llega a la plataforma de lanzamiento."}),
            ObjetoEscena("el sitio del choque", (306, 108, 14, 38), (308, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "derecha", self.juego.tiempo),
                         salida=("choque", (24, 126)),
                         respuestas={"Mirar": "Por ahí quedó mi nave."}),
        ]

    # ---------- Boletería ----------

    def atiende(self):
        """El boletero aparece recién después de hablar con R-7; antes, la boletería está vacía con un cartel."""
        return self.juego.progreso["hablo_con_robot"]

    def hablar_boletero(self):
        if not self.atiende():
            return "No hay nadie. Un cartel dice: VUELVO EN 5."
        self.juego.iniciar_dialogo(dialogo_boletero(self.juego))
        return None   # no dice nada: empieza el diálogo

    def mirar_boleteria(self):
        if self.juego.progreso["compro_boleto"]:
            return "La boletería. Ya compré mi boleto."
        self.juego.progreso["vio_boleteria"] = True
        if not self.atiende():
            return "Una boletería sin nadie. Un cartel dice: VUELVO EN 5."
        return "Una boletería. La atiende un alien de bigote enorme."

    def usar_boleteria(self):
        if self.juego.progreso["compro_boleto"]:
            return "Ya tengo mi boleto."
        self.juego.progreso["vio_boleteria"] = True
        return "Pide 200 keplesos por un boleto. No tengo plata."

    def comprar_boleto(self):
        progreso = self.juego.progreso
        if progreso["compro_boleto"]:
            return "Ya tengo mi boleto."
        inventario = self.juego.inventario
        inventario.quitar("plata")
        inventario.agregar("boleto")
        progreso["compro_boleto"] = True
        return "Metí los 200 keplesos y salió un boleto. ¡Ahora puedo pasar!"

    # ---------- Puerta de acceso ----------

    def mirar_puerta(self):
        if self.juego.progreso["boleto_usado"]:
            return "La puerta está abierta. Puedo pasar a la plataforma."
        self.juego.progreso["vio_boleteria"] = True
        return "Una puerta de acceso cerrada. Lleva a la plataforma y tiene una ranura para un boleto."

    def usar_puerta(self):
        if self.juego.progreso["boleto_usado"]:
            return "Ya está abierta."
        self.juego.progreso["vio_boleteria"] = True
        return "No se abre. Necesito un boleto para pasar."

    def pasar_puerta(self):
        progreso = self.juego.progreso
        if progreso["boleto_usado"]:
            return "Ya está abierta."
        self.juego.inventario.quitar("boleto")
        progreso["boleto_usado"] = True
        return "Pasé el boleto por la ranura... ¡la puerta se abrió!"

    # ---------- Dibujo de los objetos ----------

    def cuadro_boletero(self):
        """Qué cuadro de la animación del mate toca ahora: descansa, levanta el termo, sirve, agarra el mate y sorbe."""
        t = self.juego.tiempo % 9.0
        if t < 1.2:
            return 0
        if t < 1.7:
            return 1                                    # levanta el termo
        if t < 3.5:
            return 2 + int(t * 6) % 2                   # sirve el agua (la corriente se mueve)
        if t < 4.0:
            return 1                                    # deja el termo
        if t < 4.5:
            return 0
        if t < 5.0:
            return 4                                    # agarra el mate
        if t < 7.0:
            return 5                                    # sorbe
        if t < 7.5:
            return 4
        return 0

    def dibujar_boleteria(self, sup, rect):
        x, y, w, h = rect
        pygame.draw.rect(sup, (96, 100, 126), (x, y + 10, w, h - 10))              # cuerpo
        pygame.draw.rect(sup, (130, 134, 160), (x, y + 10, w, 4))
        pygame.draw.rect(sup, (60, 62, 84), (x - 3, y + 6, w + 6, 6))               # techo
        pygame.draw.rect(sup, (20, 24, 44), (x + 8, y + 22, w - 16, 28))            # ventanilla
        pygame.draw.rect(sup, (110, 230, 245), (x + 8, y + 22, w - 16, 3))
        # El boletero, detrás del vidrio: se lo recorta con el marco de la ventanilla, así no se le ven las piernas.
        # Se ceba mate con un termo que está sobre el mostrador (el ciclo dura 9 segundos).
        sup.set_clip(pygame.Rect(x + 8, y + 22, w - 16, 28))
        if self.atiende():
            dibujar_objeto(sup, self.juego.sprites, f"boletero_f{self.cuadro_boletero()}", pygame.Rect(x + 24, y + 26, 18, 30))
        else:                                               # nadie atiende: un cartel de papel colgado en la ventanilla
            for cx in (x + 17, x + 49):
                pygame.draw.line(sup, (200, 196, 180), (cx, y + 23), (cx, y + 27))
            pygame.draw.rect(sup, (40, 30, 20), (x + 10, y + 26, 46, 22))
            pygame.draw.rect(sup, (244, 236, 206), (x + 11, y + 27, 44, 20))
            fuente_cartel = self.juego.fuentes["chica"]
            texto(sup, "VUELVO", fuente_cartel, (60, 40, 30), (x + 33, y + 28), ancla="midtop")
            texto(sup, "EN", fuente_cartel, (60, 40, 30), (x + 25, y + 37), ancla="midtop")
            for fila, bits in enumerate(("111", "100", "111", "001", "111")):          # el 5, dibujado a mano para que se lea bien
                for col, bit in enumerate(bits):
                    if bit == "1":
                        pygame.draw.rect(sup, (60, 40, 30), (x + 36 + col * 2, y + 37 + fila * 2, 2, 2))
        sup.set_clip(None)
        pygame.draw.rect(sup, (150, 154, 176), (x + 8, y + 50, w - 16, 4))          # mostrador
        pygame.draw.rect(sup, (40, 42, 60), (x + w // 2 - 6, y + 57, 12, 3))        # ranura de billetes
        pygame.draw.rect(sup, (40, 36, 52), (x, y + 10, w, h - 10), 1)
        # Cartel con el precio
        pygame.draw.rect(sup, MARRON_CARTEL, (x - 4, y - 2, w + 8, 14))
        pygame.draw.rect(sup, (40, 30, 20), (x - 4, y - 2, w + 8, 14), 1)
        fuente = self.juego.fuentes["chica"]
        texto(sup, "BOLETERÍA", fuente, (255, 236, 180), (x + w // 2, y + 6), ancla="center")

    def dibujar_puerta(self, sup):
        """
        Puerta de acceso: una valla de barrotes que cruza todo el piso, del horizonte hasta el borde
        de abajo (no sube al cielo). Abierta, los barrotes se recogen y queda el paso libre.
        """
        x, y, w, h = PUERTA
        abierta = self.juego.progreso["boleto_usado"]
        reja = (150, 154, 176)
        if abierta:
            luz = pygame.Surface((w - 12, h), pygame.SRCALPHA)                         # luz del camino libre
            luz.fill((110, 230, 245, 70))
            sup.blit(luz, (x + 6, y))
            for bx in range(x + 1, x + 7, 3):                                          # barrotes recogidos
                pygame.draw.rect(sup, reja, (bx, y, 2, h))
        else:
            pygame.draw.rect(sup, (30, 28, 44), (x, y, w, h))                          # fondo oscuro tras la reja
            for bx in range(x + 2, x + w - 6, 5):                                      # barrotes verticales
                pygame.draw.rect(sup, reja, (bx, y, 2, h))
                pygame.draw.rect(sup, (96, 100, 126), (bx + 1, y, 1, h))
            for ry in (y + 6, y + h // 2):                                             # travesaños
                pygame.draw.rect(sup, (110, 114, 140), (x, ry, w - 4, 3))
            for py in range(0, w - 6, 8):                                              # franja de peligro, abajo
                pygame.draw.rect(sup, (230, 190, 40), (x + py, y + h - 8, 4, 8))
                pygame.draw.rect(sup, (30, 26, 30), (x + py + 4, y + h - 8, 4, 8))
        pygame.draw.rect(sup, (60, 62, 84), (x + w - 6, y - 4, 6, h + 4))              # poste del marco
        pygame.draw.rect(sup, (30, 28, 44), (x + w - 6, y - 4, 6, h + 4), 1)
        pygame.draw.rect(sup, (230, 190, 40), (x + w - 6, y - 7, 6, 4))                # luz de aviso arriba del poste
        # Luz de estado y ranura para el boleto, a la derecha del poste
        pygame.draw.rect(sup, (50, 50, 64), (x + w + 1, y + 14, 9, 24))
        pygame.draw.rect(sup, (30, 28, 44), (x + w + 1, y + 14, 9, 24), 1)
        pygame.draw.rect(sup, (90, 230, 120) if abierta else (230, 60, 60), (x + w + 3, y + 17, 5, 4))
        pygame.draw.rect(sup, (20, 20, 30), (x + w + 3, y + 26, 5, 2))                 # ranura

    # ---------- Fondo ----------

    def construir_fondo(self, sup):
        paisaje.cielo(sup)       # el mismo cielo que en las demás pantallas de exterior
        for x, r in ((250, 16), (292, 12)):                           # domos de la base, a lo lejos
            arte16.cupula(sup, x, 100, r)
        # Cartel bajo, clavado en el piso junto a la valla, que indica hacia dónde lleva
        for x in (58, 130):
            pygame.draw.rect(sup, (90, 94, 120), (x, 82, 3, 22))
        pygame.draw.rect(sup, (60, 62, 84), (52, 68, 88, 22))
        pygame.draw.rect(sup, (110, 230, 245), (52, 68, 88, 22), 1)
        fuente = self.juego.fuentes["chica"]
        texto(sup, "PLATAFORMA", fuente, (110, 230, 245), (96, 74), ancla="center")
        texto(sup, "DE LANZAMIENTO", fuente, (110, 230, 245), (96, 84), ancla="center")
        pygame.draw.rect(sup, (40, 34, 56), (0, 96, ANCHO, 4))
        # Piso metálico
        bandas(sup, (0, 100, ANCHO, ALTO_ESCENA - 100), [(70, 72, 92), (82, 84, 106), (94, 96, 120),
                                                         (104, 106, 130), (112, 114, 138)])
        rellenar_textura(sup, self.juego.sprites["textura_piso_metal"], (0, 103, ANCHO, ALTO_ESCENA - 103))
        for i in range(0, ANCHO, 8):                                  # borde de seguridad amarillo y negro
            pygame.draw.rect(sup, (230, 190, 40), (i, 100, 4, 3))
