"""
engine/spritesheet.py
Hoja de sprites (sprite sheet): UNA imagen PNG con muchos sprites y texturas
juntos, más un archivo JSON que dice dónde está cada uno.

    hoja_sprites.png   -> la imagen con todos los dibujos pegados
    hoja_sprites.json  -> {"robot": [x, y, ancho, alto], "suelo": [...], ...}

Es como lo hacían las consolas: se carga una sola imagen en memoria y se
"recortan" pedazos. Además se puede editar con cualquier programa de pixel
art (Aseprite, Piskel, GIMP...) sin tocar el código.

Uso:
    hoja = HojaSprites("assets/hoja_sprites.png")      # busca el .json al lado
    robot = hoja["robot"]                               # Surface recortada
    cuadros = hoja.grilla((0, 64), (16, 16), 4)         # 4 cuadros de 16x16 seguidos

    rellenar_textura(fondo, hoja["suelo"], (0, 100, 320, 50))   # repite una textura

Y para armar una hoja a partir de sprites ya creados:
    exportar_hoja({"robot": sup_robot, ...}, "assets/hoja_sprites.png")
"""

import json
import os

import pygame


def cargar_imagen(ruta, transparencia=True):
    """Carga un PNG. Si la ventana ya está abierta, lo convierte para que se dibuje más rápido."""
    imagen = pygame.image.load(ruta)
    if pygame.display.get_surface() is not None:   # convert solo funciona con la ventana abierta
        imagen = imagen.convert_alpha() if transparencia else imagen.convert()
    return imagen


class HojaSprites:
    def __init__(self, ruta_png, ruta_json=None):
        self.imagen = cargar_imagen(ruta_png)

        if ruta_json is None:
            ruta_json = os.path.splitext(ruta_png)[0] + ".json"
        self.regiones = {}
        if os.path.exists(ruta_json):
            with open(ruta_json, encoding="utf-8") as archivo:
                self.regiones = {nombre: tuple(rect) for nombre, rect in json.load(archivo).items()}
        self._cache = {}

    def recortar(self, rect):
        """Devuelve una copia del pedazo (x, y, ancho, alto) de la hoja."""
        return self.imagen.subsurface(pygame.Rect(rect)).copy()

    def __getitem__(self, nombre):
        """hoja["robot"] -> el sprite con ese nombre (recortado una sola vez)."""
        if nombre not in self._cache:
            if nombre not in self.regiones:
                raise KeyError(f"La hoja no tiene un sprite llamado '{nombre}'")
            self._cache[nombre] = self.recortar(self.regiones[nombre])
        return self._cache[nombre]

    def __contains__(self, nombre):
        return nombre in self.regiones

    def nombres(self):
        return list(self.regiones)

    def todos(self):
        """Diccionario nombre -> Surface con todo lo que tiene la hoja."""
        return {nombre: self[nombre] for nombre in self.regiones}

    def grilla(self, origen, tamano, cantidad, columnas=None):
        """
        Recorta cuadros del mismo tamaño puestos en grilla (típico de animaciones).
        origen: (x, y) del primer cuadro. tamano: (ancho, alto) de cada cuadro.
        """
        x0, y0 = origen
        ancho, alto = tamano
        columnas = columnas or cantidad
        return [self.recortar((x0 + (i % columnas) * ancho, y0 + (i // columnas) * alto, ancho, alto))
                for i in range(cantidad)]


def rellenar_textura(superficie, textura, rect, desfase=(0, 0)):
    """
    Repite una textura (tile) como baldosas hasta cubrir 'rect'.
    Lo que queda afuera de 'rect' no se pinta.
    """
    rect = pygame.Rect(rect)
    ancho, alto = textura.get_size()
    recorte_anterior = superficie.get_clip()
    superficie.set_clip(rect.clip(recorte_anterior))
    dx, dy = desfase
    for y in range(rect.top - dy % alto, rect.bottom, alto):
        for x in range(rect.left - dx % ancho, rect.right, ancho):
            superficie.blit(textura, (x, y))
    superficie.set_clip(recorte_anterior)


def guardar_imagen(imagen, ruta):
    """Guarda una Surface como PNG, creando la carpeta si hace falta."""
    carpeta = os.path.dirname(ruta)
    if carpeta:
        os.makedirs(carpeta, exist_ok=True)
    pygame.image.save(imagen, ruta)


def exportar_hoja(sprites, ruta_png, ancho_max=256, separacion=1):
    """
    Pega todos los sprites en una sola imagen (por filas, de más alto a más bajo)
    y guarda el PNG y el JSON con la posición de cada uno.
    Devuelve el diccionario de regiones.
    """
    orden = sorted(sprites, key=lambda nombre: -sprites[nombre].get_height())
    regiones = {}
    x = y = alto_fila = 0
    for nombre in orden:
        ancho, alto = sprites[nombre].get_size()
        if x > 0 and x + ancho > ancho_max:   # no entra: fila nueva
            x, y = 0, y + alto_fila + separacion
            alto_fila = 0
        regiones[nombre] = [x, y, ancho, alto]
        x += ancho + separacion
        alto_fila = max(alto_fila, alto)

    ancho_total = max(r[0] + r[2] for r in regiones.values())
    alto_total = max(r[1] + r[3] for r in regiones.values())
    hoja = pygame.Surface((ancho_total, alto_total), pygame.SRCALPHA)
    for nombre, (x, y, _, _) in regiones.items():
        hoja.blit(sprites[nombre], (x, y))

    guardar_imagen(hoja, ruta_png)
    with open(os.path.splitext(ruta_png)[0] + ".json", "w", encoding="utf-8") as archivo:
        json.dump(regiones, archivo, indent=2)
    return regiones
