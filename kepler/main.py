"""
kepler/main.py
Clase principal del juego. Hereda de Juego (del engine), que ya trae la
ventana pixelada, el bucle principal y la máquina de estados.

Acá se hacen tres cosas:
  1. Cargar lo que no cambia: fuentes, sprites y catálogo de ítems.
  2. Crear los DATOS DE LA PARTIDA (nueva_partida): progreso de la historia,
     inventario, escenarios y personaje. Viven en el juego, no en los estados,
     para que se compartan entre estados y no se pierdan al ir y volver.
  3. Registrar los ESTADOS de la máquina y arrancar en el menú.
"""

import json
import os
import sys

# Permite ejecutar este archivo directamente (botón ▶ de VS Code):
# agrega la carpeta del proyecto al path para encontrar 'engine'.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from engine import Juego, Inventario, Sonidos  # noqa: E402
from kepler.config import ANCHO, ALTO, FPS, TITULO, PROGRESO_INICIAL, CARPETA_SONIDOS  # noqa: E402
from kepler.glifos import FuenteConGlifos  # noqa: E402
from kepler.sprites import crear_sprites  # noqa: E402
from kepler.items import crear_catalogo, RECETAS, DESARMES  # noqa: E402
from kepler.protagonista import Astronauta  # noqa: E402
from kepler.escenas.choque import EscenaChoque  # noqa: E402
from kepler.escenas.capsula_interior import EscenaCapsulaInterior  # noqa: E402
from kepler.escenas.cueva import EscenaCueva  # noqa: E402
from kepler.escenas.mercado import EscenaMercado  # noqa: E402
from kepler.escenas.playa import EscenaPlaya  # noqa: E402
from kepler.escenas.boleteria import EscenaBoleteria  # noqa: E402
from kepler.escenas.cueva_interior import EscenaCuevaInterior  # noqa: E402
from kepler.escenas.plataforma import EscenaPlataforma  # noqa: E402
from kepler.estados.menu import EstadoMenu  # noqa: E402
from kepler.estados.intro import EstadoIntro  # noqa: E402
from kepler.estados.jugando import EstadoJugando  # noqa: E402
from kepler.estados.inventario import EstadoInventario  # noqa: E402
from kepler.estados.video import EstadoVideo  # noqa: E402
from kepler.estados.dialogo import EstadoDialogo  # noqa: E402
from kepler.estados.teclado import EstadoTeclado  # noqa: E402
from kepler.estados.final import EstadoFinal  # noqa: E402
from kepler.estados.game_over import EstadoGameOver  # noqa: E402
from kepler.estados.llegada_erronea import EstadoLlegadaErronea  # noqa: E402


class VaradoEnKepler(Juego):
    def __init__(self):
        super().__init__(ANCHO, ALTO, TITULO, FPS)

        # 1) Lo que no cambia entre partidas
        self.fuentes = {      # con FuenteConGlifos también pueden escribir los símbolos alienígenas
            "titulo": FuenteConGlifos(pygame.font.Font(None, 32)),
            "normal": FuenteConGlifos(pygame.font.Font(None, 16)),
            "chica": FuenteConGlifos(pygame.font.Font(None, 14)),
        }
        self.sonidos = Sonidos(CARPETA_SONIDOS)
        self.cargar_ajustes()
        self.sprites = crear_sprites()
        self.catalogo = crear_catalogo(self.sprites)

        # 2) Datos de la partida
        self.partida_en_curso = False
        self.nueva_partida()

        # 3) Estados de la máquina
        self.registrar_estado("MENU", EstadoMenu(self))
        self.registrar_estado("INTRO", EstadoIntro(self))
        self.registrar_estado("JUGANDO", EstadoJugando(self))
        self.registrar_estado("INVENTARIO", EstadoInventario(self))
        self.registrar_estado("VIDEO", EstadoVideo(self))
        self.registrar_estado("DIALOGO", EstadoDialogo(self))
        self.registrar_estado("TECLADO", EstadoTeclado(self))
        self.registrar_estado("FINAL", EstadoFinal(self))
        self.registrar_estado("LLEGADA_ERRONEA", EstadoLlegadaErronea(self))
        self.registrar_estado("GAME_OVER", EstadoGameOver(self))
        self.cambiar_estado("MENU")

    def actualizar_general(self, dt):
        self.sonidos.actualizar()     # la música se pausa mientras suena otra cosa

    # ------------------------------------------------------------------ #
    #  Partida
    # ------------------------------------------------------------------ #
    # ---------- Ajustes (el volumen se recuerda entre partidas) ----------

    RUTA_AJUSTES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ajustes.json")

    def cargar_ajustes(self):
        try:
            with open(self.RUTA_AJUSTES, encoding="utf-8") as archivo:
                self.sonidos.poner_volumen_general(float(json.load(archivo).get("volumen", 1.0)))
        except (OSError, ValueError, TypeError):
            pass

    def guardar_ajustes(self):
        try:
            with open(self.RUTA_AJUSTES, "w", encoding="utf-8") as archivo:
                json.dump({"volumen": round(self.sonidos.volumen_general, 2)}, archivo)
        except OSError:
            pass

    def nueva_partida(self):
        """Deja todo como al principio de la historia."""
        self.progreso = {clave: False for clave in PROGRESO_INICIAL}
        self.inventario = Inventario(self.catalogo, RECETAS, desarmes=DESARMES)
        self.inventario.agregar("billetera")       # la astronauta siempre lleva su billetera con cambio
        self.item_en_mano = None
        self.escenas = {
            "choque": EscenaChoque(self),
            "capsula_interior": EscenaCapsulaInterior(self),
            "cueva": EscenaCueva(self),
            "mercado": EscenaMercado(self),
            "playa": EscenaPlaya(self),
            "boleteria": EscenaBoleteria(self),
            "cueva_interior": EscenaCuevaInterior(self),
            "plataforma": EscenaPlataforma(self),
        }
        self.escena = self.escenas["choque"]
        self.personaje = Astronauta(170, 128, self.sprites)
        self.personaje.decir("Mi nave quedó destrozada... Tengo que encontrar la forma de salir de este planeta.")

    def ir_a_escena(self, nombre, entrada):
        """Cambia de escenario y ubica a la astronauta en el punto de entrada."""
        self.escena = self.escenas[nombre]
        self.personaje.detener()
        self.personaje.x, self.personaje.y = entrada
        self.estados["JUGANDO"].poner_musica()      # algunas escenas (el mercado) tienen su propia música

    def nombre_escena_actual(self):
        """El nombre con el que está registrada la escena actual (por ejemplo "mercado")."""
        return next((n for n, e in self.escenas.items() if e is self.escena), None)

    def iniciar_dialogo(self, dialogo):
        self.personaje.texto = ""          # que no quede un texto viejo detrás del diálogo
        self.estados["DIALOGO"].empezar(dialogo)
        self.cambiar_estado("DIALOGO")

    def terminar_partida(self):
        """La astronauta despega: se termina la partida y se muestra el final."""
        self.partida_en_curso = False
        self.cambiar_estado("FINAL")

    def perder_partida(self, motivo, destino):
        """El cohete va al planeta equivocado, aterriza y después aparece el game over."""
        self.partida_en_curso = False
        self.motivo_game_over = motivo
        self.destino_erroneo = destino
        self.cambiar_estado("LLEGADA_ERRONEA")


def main():
    VaradoEnKepler().ejecutar()


if __name__ == "__main__":
    main()
