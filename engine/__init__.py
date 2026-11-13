"""
engine — Motor 2D para aventuras gráficas point-and-click en estilo pixel art (16 bits).

El motor NO sabe nada de ningún juego en particular. Solo ofrece piezas genéricas:

    Juego          -> ventana pixelada, bucle principal y MÁQUINA DE ESTADOS
    Estado         -> clase base de cada estado (menú, jugando, inventario...)
    ZonaCaminable  -> polígono de navegación (por dónde se puede caminar)
    Actor          -> personaje que camina hacia un punto y habla
    Escena         -> escenario: fondo, objetos y zona caminable
    ObjetoEscena   -> objeto con el que se interactúa (mirar, coger, usar, hablar...)
    Inventario     -> guardar, quitar y COMBINAR ítems
    Dialogo        -> conversaciones con opciones múltiples (árbol de nodos)
    crear_sprite   -> convierte un dibujo hecho con letras en una imagen pixel art
    HojaSprites    -> carga una hoja de sprites (PNG + JSON) y recorta cada sprite/textura
    Boton y textos -> interfaz reutilizable
    Sonidos        -> efectos y voces, por nombre de archivo (si falta, queda en silencio)

El juego concreto (carpeta kepler/) usa estas piezas y les pone el contenido.
"""

from engine.juego import Juego
from engine.estado import Estado
from engine.navegacion import ZonaCaminable, punto_en_poligono
from engine.actor import Actor
from engine.escena import Escena, ObjetoEscena
from engine.inventario import Inventario
from engine.dialogo import Dialogo, Nodo, Opcion
from engine.pixelart import crear_sprite, agregar_contorno, espejar, escalar
from engine.spritesheet import HojaSprites, rellenar_textura, exportar_hoja, cargar_imagen, guardar_imagen
from engine.ui import Boton, texto, envolver_texto, panel, bandas, oscurecer
from engine.sonido import Sonidos

__all__ = [
    "Juego", "Estado", "ZonaCaminable", "punto_en_poligono", "Actor",
    "Escena", "ObjetoEscena", "Inventario", "Dialogo", "Nodo", "Opcion",
    "crear_sprite", "agregar_contorno", "espejar", "escalar",
    "HojaSprites", "rellenar_textura", "exportar_hoja", "cargar_imagen", "guardar_imagen",
    "Boton", "texto", "envolver_texto", "panel", "bandas", "oscurecer", "Sonidos",
]
