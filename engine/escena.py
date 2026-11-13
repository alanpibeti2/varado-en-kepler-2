"""
engine/escena.py
Un escenario genérico de aventura gráfica: fondo, objetos y zona caminable.

El juego crea sus escenarios como SUBCLASES de Escena, definiendo el
polígono caminable, los objetos y el fondo (una imagen PNG o código).
"""

import os

import pygame

from engine.navegacion import ZonaCaminable
from engine.spritesheet import cargar_imagen

# Lo que dice el personaje cuando un objeto no tiene una respuesta propia
RESPUESTAS_POR_DEFECTO = {
    "Mirar": "No veo nada especial.",
    "Agarrar": "No puedo llevarme eso.",
    "Usar": "No sé cómo usar eso.",
    "Hablar": "No creo que me conteste.",
}


class ObjetoEscena:
    """
    Algo con lo que se puede interactuar en un escenario (un "hotspot").

    - respuestas: qué pasa con cada verbo. El valor puede ser un texto
      (lo que dice el personaje) o una función que se ejecuta y devuelve
      el texto a decir (o None para no decir nada).
          respuestas={"Mirar": "Un barril.", "Usar": self.abrir_barril}
    - usos: qué pasa al usar un ÍTEM del inventario sobre este objeto.
          usos={"llave": self.abrir_puerta}
    - salida: si el objeto es un camino a otra escena: (nombre_escena, (x, y)).
    - visible_si: función que devuelve True/False. Permite que un objeto
      aparezca recién cuando pasa algo (ej: la batería, al abrir la caja).
    """

    def __init__(self, nombre, rect, punto_interaccion, dibujo=None, id_item=None,
                 salida=None, visible_si=None, respuestas=None, usos=None):
        self.nombre = nombre                        # lo que se ve en "Mirar robot"
        self.rect = pygame.Rect(rect)               # zona donde se puede hacer clic
        self.punto_interaccion = punto_interaccion  # dónde se para el personaje
        self.dibujo = dibujo                        # función dibujo(superficie, rect)
        self.id_item = id_item                      # si no es None, se puede coger
        self.salida = salida
        self.visible_si = visible_si
        self.respuestas = respuestas or {}
        self.usos = usos or {}

    @property
    def visible(self):
        return self.visible_si is None or self.visible_si()

    def contiene(self, pos):
        return self.rect.collidepoint(pos)

    def responder(self, verbo):
        """Devuelve el texto que dice el personaje al usar 'verbo' sobre el objeto."""
        respuesta = self.respuestas.get(verbo, RESPUESTAS_POR_DEFECTO.get(verbo))
        if callable(respuesta):        # si es una función, la ejecutamos
            return respuesta()
        return respuesta

    def usar_item(self, id_item):
        """Devuelve el texto a decir al usar el ítem 'id_item' sobre el objeto."""
        if id_item in self.usos:
            return self.usos[id_item]()
        return "Eso no sirve acá."

    def dibujar(self, superficie):
        if self.dibujo:
            self.dibujo(superficie, self.rect)


class Escena:
    zoom = 1       # 2 = la cámara acerca la escena al doble y sigue al personaje (la escena lo decide)
    zoom_y = 0     # con zoom: desde qué fila de la escena empieza lo que se ve
    bloqueada = False   # True mientras pasa una animación: se ignoran los clics en la escena

    def __init__(self, nombre, tamano, poligono, ruta_fondo=None):
        """
        ruta_fondo: imagen PNG del fondo. Si no se pasa o no existe, el fondo
        se dibuja con código llamando a construir_fondo.
        """
        self.nombre = nombre
        self.zona = ZonaCaminable(poligono)
        self.objetos = []
        # El fondo se arma UNA vez en una superficie y después solo se copia
        if ruta_fondo and os.path.exists(ruta_fondo):
            self.fondo = cargar_imagen(ruta_fondo, transparencia=False)
        else:
            self.fondo = pygame.Surface(tamano)
            self.construir_fondo(self.fondo)

    def actualizar(self, dt):
        """Se llama en cada cuadro mientras se juega en esta escena (para eventos con tiempo). No hace nada por defecto."""
        pass

    def construir_fondo(self, superficie):
        """Cada escenario concreto lo sobrescribe para pintar su fondo."""
        superficie.fill((0, 0, 0))

    def objetos_visibles(self):
        return [objeto for objeto in self.objetos if objeto.visible]

    def objeto_en(self, pos):
        """Devuelve el objeto visible bajo 'pos' o None."""
        # Recorremos al revés: el último dibujado es el que está "encima"
        for objeto in reversed(self.objetos_visibles()):
            if objeto.contiene(pos):
                return objeto
        return None

    def quitar_objeto(self, objeto):
        if objeto in self.objetos:
            self.objetos.remove(objeto)

    def dibujar(self, superficie):
        superficie.blit(self.fondo, (0, 0))
        for objeto in self.objetos_visibles():
            objeto.dibujar(superficie)

    def dibujar_debug(self, superficie):
        """Muestra la zona caminable, las zonas clicables y los puntos de interacción."""
        self.zona.dibujar_debug(superficie)
        for objeto in self.objetos_visibles():
            pygame.draw.rect(superficie, (255, 255, 0), objeto.rect, 1)
            pygame.draw.circle(superficie, (255, 80, 80), objeto.punto_interaccion, 2)
