"""
kepler/generar_hoja.py
Arma los assets gráficos del juego:

  - kepler/assets/hoja_sprites.png + .json: todos los sprites (personajes, ítems,
    texturas y objetos grandes de los escenarios).
  - kepler/assets/fondos/*.png: el fondo de cada escenario.

    python -m kepler.generar_hoja

Después se pueden abrir los PNG en un programa de pixel art y retocarlos: el juego
los carga solos. Ojo: correr este script SOBRESCRIBE lo que hayas editado en esos PNG.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame  # noqa: E402

from engine import exportar_hoja, guardar_imagen  # noqa: E402
from kepler.config import ANCHO, ALTO_ESCENA, CARPETA_FONDOS, RUTA_HOJA  # noqa: E402
from kepler.sprites import crear_sprites_desde_codigo  # noqa: E402


def generar_hoja():
    regiones = exportar_hoja(crear_sprites_desde_codigo(), RUTA_HOJA)
    print(f"Hoja guardada en {RUTA_HOJA} con {len(regiones)} sprites.")


def generar_fondos():
    # Importar aca: el juego crea la ventana, y la generacion de fondos la necesita
    from kepler.main import VaradoEnKepler
    juego = VaradoEnKepler()
    for nombre, escena in juego.escenas.items():
        sup = pygame.Surface((ANCHO, ALTO_ESCENA))
        escena.construir_fondo(sup)     # el dibujo con código, no el PNG
        ruta = os.path.join(CARPETA_FONDOS, f"{nombre}.png")
        guardar_imagen(sup, ruta)
        print(f"Fondo guardado en {ruta}")


if __name__ == "__main__":
    pygame.init()
    generar_hoja()
    generar_fondos()
