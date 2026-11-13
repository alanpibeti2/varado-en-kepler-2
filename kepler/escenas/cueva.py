"""
kepler/escenas/cueva.py
Escenario 2: la entrada a la cueva de cristales.

PUZLE 1 (acá mismo): R-7, el robot minero, está apagado y tiene una ranura que pide 10 keplesos (la billetera
  tiene pesos de la Tierra, pero hay monedas que entran en la ranura).
  Usar la billetera (que siempre llevás en la mochila) en el robot -> se enciende. Hablarle -> te da el código
  de la compuerta (escrito con símbolos raros) y la linterna.

PUZLE 2:
  1. Usar la compuerta -> se abre un tablero de símbolos alienígenas: hay que teclear el código a mano.
     El robot te lo dice, escrito con esos mismos símbolos.
  2. Con el código, la compuerta se abre, pero adentro está oscuro.
  3. Usar la linterna en la compuerta -> se ilumina y se puede entrar.
  4. El minero de la entrada tiene el pico roto (solo le queda la cabeza de metal) y te la
     presta a cambio de una coca de 3L (la coca está en la heladera de la nave; se la das
     usándola sobre el minero). Para armar el pico hay que combinar la cabeza con un palo
     (el palo está en la caja negra naranja junto a la nave).
     Podés devolverle el pico armado usándolo sobre él, pero solo una vez que lo usaste
     (si no sacaste un fragmento, te dice que te lo quedes) y solo cuando el palo ya no hace falta: el mismo palo sirve
     para la caña con la que se espanta al perro de la playa (hasta que no pase eso, la astronauta se lo guarda).
  5. Entrar a la cueva (escena cueva_interior) y picar el cristal grande: el fragmento
     se vende en el mercado (a la derecha) para pagar el boleto a la plataforma.
"""

import math
import os

import pygame

from engine import Escena, ObjetoEscena, bandas, rellenar_textura
from kepler import arte, paisaje
from kepler.config import ANCHO, ALTO_ESCENA, CARPETA_FONDOS
from kepler.sprites import dibujar_objeto, dibujar_flecha, ANGULOS_MECEDORA, crear_robot
from kepler.dialogos import CODIGO_COMPUERTA, dialogo_robot, dialogo_minero, dialogo_minero_recibe_coca, dialogo_minero_recibe_pico


class EscenaCueva(Escena):
    def __init__(self, juego):
        self.juego = juego
        self._cuadros_robot = {}          # los cuadros de R-7 ya dibujados (para no rehacerlos en cada cuadro)
        poligono = [(8, 110), (312, 110), (318, 147), (2, 147)]
        super().__init__("Cueva de cristales", (ANCHO, ALTO_ESCENA), poligono,
                         ruta_fondo=os.path.join(CARPETA_FONDOS, "cueva.png"))
        sprites = juego.sprites

        self.objetos = [
            ObjetoEscena("compuerta", (138, 54, 48, 56), (190, 120),
                         dibujo=self.dibujar_compuerta,
                         respuestas={
                             "Mirar": self.mirar_compuerta,
                             "Usar": self.usar_compuerta,
                             "Hablar": "¿Ábrete sésamo? No, no funciona.",
                             "Agarrar": "Está atornillada a la roca.",
                         },
                         usos={"linterna": self.iluminar}),
            # El tablerito de la derecha: ahí se camina para teclear el código
            ObjetoEscena("tablero", (191, 66, 12, 25), (197, 121),
                         respuestas={
                             "Mirar": self.mirar_tablero,
                             "Usar": self.usar_compuerta,
                             "Agarrar": "Está soldado a la roca.",
                             "Hablar": "Tablero, ¿me dejás pasar? ...No contesta.",
                         }),
            # Una vez iluminada, la compuerta es un camino hacia adentro (tapa a la compuerta)
            ObjetoEscena("el interior de la cueva", (138, 54, 48, 56), (162, 118),
                         visible_si=lambda: self.juego.progreso["cueva_iluminada"],
                         salida=("cueva_interior", (30, 128)),
                         respuestas={
                             "Mirar": self.mirar_compuerta,
                             "Usar": "Ya está abierta. Mejor entro a buscar el cristal.",
                             "Hablar": "¿Hola? ...Nadie. Solo el eco.",
                             "Agarrar": "Está atornillada a la roca.",
                         }),
            # R-7, el robot minero de la mina: está apagado hasta que le metés monedas
            ObjetoEscena("robot", (98, 90, 24, 26), (110, 124),
                         dibujo=self.dibujar_robot,
                         respuestas={
                             "Mirar": self.mirar_robot,
                             "Hablar": self.hablar_robot,
                             "Usar": self.usar_robot,
                             "Agarrar": "No me lo voy a llevar a upa.",
                         },
                         usos={
                             "billetera": self.encender_robot,
                             "billetera_vacia": lambda: "Ya no me queda cambio.",
                         }),
            # El compartimiento del pecho de R-7: aparece abierto, con la linterna, después de que R-7 avisa
            ObjetoEscena("compartimiento de R-7", (104, 100, 12, 8), (110, 124),
                         dibujo=self.dibujar_compartimiento,
                         visible_si=lambda: self.juego.progreso["sabe_codigo"],
                         respuestas={
                             "Mirar": "El compartimiento del pecho de R-7, abierto. Hay una linterna adentro.",
                             "Usar": "Mejor agarro la linterna.",
                             "Hablar": "R-7, ¿puedo llevarme la linterna? ...Me dijo que sí.",
                             "Agarrar": self.agarrar_linterna,
                         }),
            ObjetoEscena("cartel", (60, 88, 24, 20), (72, 124),
                         dibujo=lambda sup, r: dibujar_objeto(sup, sprites, "cartel", r),
                         respuestas={
                             "Mirar": "Dice: MINA KEPLER-7. PELIGRO: CUEVA SIN LUZ.",
                             "Agarrar": "Está clavado en la roca.",
                         }),
            # La cabeza del pico, apoyada en la pared junto al minero (se la lleva quien se la gana con la coca)
            ObjetoEscena("cabeza de pico", (228, 102, 12, 12), (236, 124),
                         dibujo=self.dibujar_cabeza_pico,
                         visible_si=lambda: not self.juego.progreso["pico_dado"] and not self.juego.progreso["cristal_minado"],
                         respuestas={
                             "Mirar": "La parte de metal de un pico, apoyada en la pared. No tiene mango.",
                             "Agarrar": "Es del minero. No me corresponde llevármela.",
                         }),
            # Si le devolvés el pico armado, queda apoyado entero en el mismo lugar
            ObjetoEscena("pico", (228, 88, 12, 26), (236, 124),
                         dibujo=self.dibujar_pico_entero,
                         visible_si=lambda: self.juego.progreso["cristal_minado"] and not self.juego.progreso["pico_dado"],
                         respuestas={
                             "Mirar": "El pico del minero, apoyado en la pared. Otra vez con su mango.",
                             "Agarrar": "Es del minero. Ya me ayudó bastante.",
                         }),
            ObjetoEscena("minero", (244, 90, 22, 30), (236, 124),
                         dibujo=self.dibujar_minero,
                         respuestas={
                             "Mirar": self.mirar_minero,
                             "Hablar": self.hablar_minero,
                             "Usar": "No creo que le guste que lo use.",
                             "Agarrar": "No voy a cargar a un alien.",
                         },
                         usos={"coca": self.dar_coca, "pico": self.devolver_pico,
                               "cabeza_pico": lambda: "Todavía la necesito. Se la devuelvo cuando termine."}),
            ObjetoEscena("el mercado", (306, 108, 14, 38), (308, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "derecha", self.juego.tiempo),
                         salida=("mercado", (24, 126)),
                         respuestas={"Mirar": "Por ahí se ven unos toldos de colores a lo lejos."}),
            ObjetoEscena("el sitio del choque", (0, 108, 14, 38), (12, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "izquierda", self.juego.tiempo),
                         salida=("choque", (296, 126)),
                         respuestas={"Mirar": "Por ahí quedó mi nave."}),
        ]

    def dibujar_compuerta(self, sup, rect):
        progreso = self.juego.progreso
        abierta, iluminada = progreso["compuerta_abierta"], progreso["cueva_iluminada"]
        if not abierta:
            nombre = "compuerta_cerrada"
        else:
            nombre = "compuerta_iluminada" if iluminada else "compuerta_oscura"
        dibujar_objeto(sup, self.juego.sprites, nombre, rect)
        arte.luz_compuerta(sup, rect, abierta, self.juego.tiempo)

    # ---------- Fondo ----------

    def construir_fondo(self, sup):
        paisaje.cielo(sup)       # el mismo cielo que en las demás pantallas de exterior
        paisaje.pared_cueva(sup)
        paisaje.suelo_cueva(sup)

    # ---------- Minero ----------

    def dibujar_minero(self, sup, rect):
        # Se hamaca en su mecedora, de atrás hacia adelante, un vaivén de unos 3 segundos
        fase = (math.sin(self.juego.tiempo * 2.1) + 1) / 2          # 0 (inclinado atrás) a 1 (adelante)
        cuadro = round(fase * (len(ANGULOS_MECEDORA) - 1))
        dibujar_objeto(sup, self.juego.sprites, f"minero_silla_{cuadro}", rect)

    def dibujar_cabeza_pico(self, sup, rect):
        dibujar_objeto(sup, self.juego.sprites, "cabeza_pico_pared", rect)

    def dibujar_pico_entero(self, sup, rect):
        dibujar_objeto(sup, self.juego.sprites, "pico_pared", rect)

    def mirar_minero(self):
        return "Un alien verde con antenas, sentado en una mecedora. No lleva casco. Parece amable."

    def hablar_minero(self):
        self.juego.iniciar_dialogo(dialogo_minero(self.juego))
        return None   # no dice nada: empieza el diálogo

    def dar_coca(self):
        self.juego.inventario.quitar("coca")
        self.juego.progreso["pico_dado"] = True
        self.juego.inventario.agregar("cabeza_pico")      # el pico está roto: solo le queda la cabeza
        self.juego.iniciar_dialogo(dialogo_minero_recibe_coca())
        return None   # no dice nada: empieza el diálogo

    def devolver_pico(self):
        progreso = self.juego.progreso
        lo_uso = progreso["cristal_minado"]      # ¿ya sacó el fragmento?
        if lo_uso and not progreso["perro_ahuyentado"]:
            # El palo del mango también hace falta para la caña (el perro de la playa): hasta que no termine eso, se lo queda
            return "Todavía voy a necesitar el palo. Se lo devuelvo más tarde."
        if lo_uso:
            self.juego.inventario.quitar("pico")
            progreso["pico_dado"] = False
        self.juego.iniciar_dialogo(dialogo_minero_recibe_pico(lo_uso))
        return None

    # ---------- Robot ----------

    def dibujar_robot(self, sup, rect):
        """Apagado, quieto. Encendido: mira para los costados, parpadea, balancea la cabeza y las lucecitas corren."""
        if not self.juego.progreso["robot_activo"]:
            sup.blit(self.juego.sprites["robot_apagado"], rect)
            return
        t = self.juego.tiempo
        ciclo = t % 7.0
        mirada = -1 if 1.0 <= ciclo < 2.2 else 1 if 3.6 <= ciclo < 4.8 else 0
        parpadeo = (2.6 <= ciclo < 2.75) or (5.5 <= ciclo < 5.65) or (6.3 <= ciclo < 6.4)
        dy = 1 if int(t * 1.4) % 4 == 3 else 0
        luz = int(t * 3) % 3
        clave = (mirada, parpadeo, dy, luz)
        if clave not in self._cuadros_robot:
            self._cuadros_robot[clave] = crear_robot(True, mirada, parpadeo, dy, luz)
        sup.blit(self._cuadros_robot[clave], rect)

    def dibujar_compartimiento(self, sup, rect):
        """La tapita del pecho abierta, con una linterna asomando y un brillo que titila."""
        pygame.draw.rect(sup, (24, 20, 26), (rect.x, rect.y, 12, 8))
        pygame.draw.rect(sup, (84, 66, 40), (rect.x + 1, rect.y + 1, 10, 6))
        pygame.draw.rect(sup, (30, 30, 40), (rect.x + 2, rect.y + 2, 7, 4))
        pygame.draw.rect(sup, (210, 214, 230), (rect.x + 3, rect.y + 3, 5, 2))
        pygame.draw.rect(sup, (250, 230, 120) if int(self.juego.tiempo * 2) % 2 == 0 else (200, 170, 70),
                         (rect.x + 8, rect.y + 3, 2, 2))

    def agarrar_linterna(self):
        progreso = self.juego.progreso
        progreso["linterna_dada"] = True
        self.juego.inventario.agregar("linterna")
        self.quitar_objeto(next(o for o in self.objetos if o.nombre == "compartimiento de R-7"))
        return "Una linterna. Con esto debería poder ver adentro."

    def mirar_robot(self):
        if self.juego.progreso["robot_activo"]:
            return "R-7, el robot minero. Ahora tiene energía."
        return "Está apagado. Tiene una ranura para monedas: pide 10 keplesos para funcionar."

    def hablar_robot(self):
        if not self.juego.progreso["robot_activo"]:
            return "No responde. Está sin energía."
        self.juego.iniciar_dialogo(dialogo_robot(self.juego))
        return None   # no dice nada: empieza el diálogo

    def usar_robot(self):
        if self.juego.progreso["robot_activo"]:
            return "Mejor le hablo."
        return "Tiene una ranura para monedas."

    def encender_robot(self):
        if self.juego.progreso["robot_activo"]:
            return "Ya tiene energía."
        inventario = self.juego.inventario
        inventario.quitar("billetera")
        inventario.agregar("billetera_vacia")      # se quedó sin cambio
        self.juego.progreso["robot_activo"] = True
        return "Pide keplesos y en la billetera solo tengo pesos de la Tierra. Pruebo con las monedas que entran... ¡Funcionó! El robot se está encendiendo. Voy a hablarle."

    # ---------- Compuerta ----------

    def mirar_compuerta(self):
        progreso = self.juego.progreso
        if not progreso["compuerta_abierta"]:
            return "Una compuerta blindada con un tablero lleno de símbolos que no conozco."
        if not progreso["cueva_iluminada"]:
            return "Adentro está completamente oscuro. No veo nada."
        return "Una cueva llena de cristales brillantes. Al fondo brilla algo más fuerte."

    def mirar_tablero(self):
        if self.juego.progreso["compuerta_abierta"]:
            return "El tablero de la compuerta. Ya la abrí: la luz está en verde."
        return "Un tablero con doce teclas de símbolos raros y una luz roja. Seguro abre la compuerta."

    def usar_compuerta(self):
        progreso = self.juego.progreso
        if progreso["compuerta_abierta"]:
            return "Ya está abierta."
        # Se abre el tablero numérico: el código hay que teclearlo a mano
        self.juego.estados["TECLADO"].empezar(CODIGO_COMPUERTA, self.abrir_compuerta, "COMPUERTA")
        self.juego.cambiar_estado("TECLADO")
        return None   # no dice nada: se abre el tablero

    def abrir_compuerta(self):
        """Se ejecuta cuando se acierta el código en el tablero."""
        self.juego.progreso["compuerta_abierta"] = True
        self.juego.personaje.decir("¡La compuerta se abrió!")

    def iluminar(self):
        progreso = self.juego.progreso
        if not progreso["compuerta_abierta"]:
            return "Primero tengo que abrir la compuerta."
        if progreso["cueva_iluminada"]:
            return "Ya está iluminado."
        progreso["cueva_iluminada"] = True
        return "¡Ahora se ve! Al fondo de la cueva brilla un cristal. Voy a entrar."
