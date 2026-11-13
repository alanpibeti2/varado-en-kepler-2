"""
kepler/sprites.py
Todos los sprites del juego, dibujados como texto (pixel art).

Cada letra es un píxel; su color sale de la PALETA. El '.' es transparente.
Las funciones de engine/pixelart.py los convierten en imágenes y les
agregan un contorno oscuro de 1 píxel.

HOJA DE SPRITES: si existe kepler/assets/hoja_sprites.png (+ .json), los
sprites y texturas se cargan de esa imagen en vez de estos textos. Así se
pueden retocar en un programa de pixel art. Para generarla (o regenerarla
después de cambiar algún dibujo de acá) correr:
    python -m kepler.generar_hoja
"""

import os

import pygame

from engine import crear_sprite, HojaSprites
from engine.pixelart import agregar_contorno
from kepler import arte, arte16
from kepler.config import RUTA_HOJA

CONTORNO = (14, 10, 24)

# ---------------------------------------------------------------------- #
#  Astronauta (16 x 30). Mira hacia la derecha.
# ---------------------------------------------------------------------- #
PALETA_ASTRONAUTA = {
    "W": (232, 232, 242),   # traje
    "G": (150, 150, 172),   # partes grises
    "D": (40, 56, 120),     # visor
    "C": (150, 220, 255),   # brillo del visor
    "O": (240, 140, 40),    # panel del pecho
    "R": (230, 60, 60),     # luz roja
    "H": (110, 110, 132),   # guantes
    "B": (70, 70, 92),      # cinturón
    "K": (52, 46, 64),      # botas
}

_ASTRONAUTA_CUERPO = [
    ".....WWWWWW.....",
    "...WWWWWWWWWW...",
    "..WWWWWWWWWWWW..",
    "..WWWDDDDDDDWW..",
    ".WWWDDDDDDDDDWW.",
    ".WWDDDDDDCCDDDW.",
    ".WWDDDDDDDCDDDW.",
    ".WWDDDDDDDDDDDW.",
    ".WWWDDDDDDDDDWW.",
    "..WWWWDDDDDWWW..",
    "...WWWWWWWWWW...",
    "....GGWWWWGG....",
    "..GGWWWWWWWWGG..",
    ".GGWWWWWWWWWWGG.",
    ".GWWWWOOOOWWWWG.",
    ".GWWWWOROOWWWWG.",
    ".WWWWWOOOOWWWWW.",
    "WW.WWWWWWWWWW.WW",
    "WW.WWWWWWWWWW.WW",
    "HH.WWWWWWWWWW.HH",
    "...BBBBBBBBBB...",
    "...WWWWWWWWWW...",
]

_PIERNAS_QUIETO = [
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "..KKKKK..KKKKK..",
    "..KKKKK..KKKKK..",
]

# Pierna izquierda levantada (el pie se despega del piso) y la derecha apoyada
_PIERNAS_ALZA_IZQ = [
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "..KKKKK..WWWW...",
    "..KKKKK..WWWW...",
    ".........KKKKK..",
    ".........KKKKK..",
]

# Lo mismo, con la pierna derecha levantada
_PIERNAS_ALZA_DER = [
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..WWWW...",
    "...WWWW..KKKKK..",
    "...WWWW..KKKKK..",
    "..KKKKK.........",
    "..KKKKK.........",
]

_PIERNAS_PASO = [
    "...WWWW...WWWW..",
    "..WWWW.....WWWW.",
    "..WWWW.....WWWW.",
    ".WWWW.......WWWW",
    ".WWWW.......WWWW",
    ".WWWW.......WWWW",
    "KKKKK......KKKKK",
    "KKKKK......KKKKK",
]

# ---------------------------------------------------------------------- #
#  Robot R-7 (18 x 24). Dos paletas: apagado y encendido.
# ---------------------------------------------------------------------- #
_ROBOT = [
    "........AA........",
    "........MM........",
    ".........M........",
    "...MMMMMMMMMMMM...",
    "..MLLLLLLLLLLLLM..",
    "..MLLEEELLLEEELM..",
    "..MLLEEELLLEEELM..",
    "..MLLLLLLLLLLLLM..",
    "..MLLLMMMMMMLLLM..",
    "..MLLLLLLLLLLLLM..",
    "...MMMMMMMMMMMM...",
    "......MMMMMM......",
    "...MMMMMMMMMMMM...",
    ".MMLLLLLLLLLLLLMM.",
    "MMLLLLPPPPPPLLLLMM",
    "MMLLLLPPPPPPLLLLMM",
    "MMLLLLPPPPPPLLLLMM",
    ".MLLLLLLLLLLLLLLM.",
    "..MLLLLLLLLLLLLM..",
    "...MMMMMMMMMMMM...",
    "....MMM....MMM....",
    "....MLM....MLM....",
    "...MMMMM..MMMMM...",
    "...MMMMM..MMMMM...",
]
_METAL = {"M": (92, 96, 118), "L": (168, 174, 196)}
PALETA_ROBOT_APAGADO = {**_METAL, "A": (70, 70, 84), "E": (44, 44, 56), "P": (36, 36, 48)}
PALETA_ROBOT_ENCENDIDO = {**_METAL, "A": (240, 70, 70), "E": (110, 240, 250), "P": (90, 230, 120)}

# ---------------------------------------------------------------------- #
#  Ítems (12 x 12)
# ---------------------------------------------------------------------- #
_BATERIA = [
    ".....YY.....",
    "....GGGG....",
    "...GGGGGG...",
    "...GHGGGG...",
    "...GHGGGG...",
    "...GHYYGG...",
    "...GHYGGG...",
    "...GHGYGG...",
    "...GHYYGG...",
    "...GGGGGG...",
    "...gggggg...",
    "............",
]
PALETA_BATERIA = {"G": (70, 190, 90), "g": (40, 120, 60), "H": (170, 240, 170), "Y": (255, 220, 80)}

_CABLE = [
    "............",
    "...RRRR.....",
    "..R....R....",
    ".R..RR..R...",
    ".R.R..R.R...",
    ".R.R..R.R...",
    ".R..RR..R...",
    "..R....R....",
    "...RRRR.R...",
    "........R...",
    "........SS..",
    "........SS..",
]
PALETA_CABLE = {"R": (230, 90, 50), "S": (200, 200, 215)}

_BATERIA_CON_CABLE = [
    "..YY........",
    ".GGGG.RRR...",
    ".GHGG.R..R..",
    ".GHYGRR..R..",
    ".GHYG....R..",
    ".GHGG...R...",
    ".GGGG..R....",
    ".gggg.R.....",
    "......SS....",
    "............",
    "............",
    "............",
]
PALETA_BATERIA_CON_CABLE = {**PALETA_BATERIA, **PALETA_CABLE}

_LINTERNA = [
    "............",
    "............",
    "............",
    ".........YY.",
    ".SSSSSSSLLY.",
    ".SHHHHHSLLY.",
    ".SSSSSSSLLY.",
    ".SSRSSSSLL..",
    ".........YY.",
    "............",
    "............",
    "............",
]
PALETA_LINTERNA = {"S": (110, 116, 140), "H": (180, 186, 210), "L": (255, 240, 150),
                   "Y": (255, 220, 80), "R": (230, 60, 60)}

_BILLETERA = [
    "............",
    "............",
    ".BBBBBBBBB..",
    ".BLLLLLLLB..",
    ".BLLLLLLLB..",
    ".BLLLLYYLB..",
    ".BLLLLLLLB..",
    ".BLLLLLLLB..",
    ".BBBBBBBBB..",
    "............",
    "............",
    "............",
]
PALETA_BILLETERA = {"B": (84, 52, 30), "L": (150, 96, 54), "Y": (240, 200, 60)}

_PLATA = [
    "............",
    "............",
    ".GGGGGGGGG..",
    ".GLLLLLLLG..",
    ".GLLYYLLLG..",
    ".GLLYYLLLG..",
    ".GLLLLLLLG..",
    ".GGGGGGGGG..",
    "............",
    "............",
    "............",
    "............",
]
PALETA_PLATA = {"G": (40, 110, 60), "L": (110, 190, 110), "Y": (230, 240, 180)}

_BOLETO = [
    "............",
    "............",
    ".YYYYYYYYYY.",
    ".YRRRRRRRRY.",
    ".YRWWWWWWRY.",
    ".YRRRRRRRRY.",
    ".YYYYYYYYYY.",
    "............",
    "............",
    "............",
    "............",
    "............",
]
PALETA_BOLETO = {"Y": (240, 200, 60), "R": (200, 60, 60), "W": (250, 240, 220)}

_PICO = [      # el pico entero: la cabeza es una media luna que termina en dos puntas finas
    "............",
    "....SSSS....",
    "..SSSSSSSS..",
    ".SSSSMMSSSS.",
    ".SSS.MM.SSS.",
    "SSS..MM..SSS",
    "SS...MM...SS",
    "S....MM....S",
    ".....MM.....",
    ".....MM.....",
    ".....MM.....",
    ".....MM.....",
]
PALETA_PICO = {"S": (170, 176, 200), "M": (150, 96, 54)}

_CABEZA_PICO = [      # solo la parte de metal (falta el mango); las dos puntas terminan en un píxel
    "............",
    "....SSSS....",
    "..SSSSSSSS..",
    ".SSSSHHSSSS.",
    ".SSS.HH.SSS.",
    "SSS..HH..SSS",
    "SS...HH...SS",
    "S....HH....S",
    "............",
    "............",
    "............",
    "............",
]
PALETA_CABEZA_PICO = {"S": (170, 176, 200), "H": (96, 102, 126)}

_PALO = [
    "............",
    "..........MM",
    ".........MML",
    "........MML.",
    ".......MML..",
    "......MML...",
    ".....MML....",
    "....MML.....",
    "...MML......",
    "..MML.......",
    "..ML........",
    "............",
]
PALETA_PALO = {"M": (150, 96, 54), "L": (196, 140, 88)}

_COCA = [      # una botella: tapa roja, líquido marrón con brillo y la etiqueta entera roja
    "....CC......",
    "....bb......",
    "...bBBb.....",
    "..bBHBBb....",
    "..bBHBBb....",
    "..eEEEEs....",
    "..eEEEEs....",
    "..eEEEEs....",
    "..bBHBBb....",
    "..bBBBBb....",
    "..bBBBBb....",
    "...bbbb.....",
]
PALETA_COCA = {"C": (196, 24, 36), "b": (52, 26, 16), "B": (96, 50, 28), "H": (166, 104, 60),
               "e": (244, 100, 96), "E": (214, 30, 44), "s": (146, 14, 30)}

_CRISTAL = [
    ".....C......",
    "....CCC.....",
    "....CWC.....",
    "...CCWCC....",
    "...CWCCC....",
    "..CCWCCcC...",
    "..CWCCCcC...",
    "..CCCCcCC...",
    "...CCCcC....",
    "....CcC.....",
    ".....C......",
    "............",
]
PALETA_CRISTAL = {"C": (110, 230, 245), "c": (50, 150, 190), "W": (240, 255, 255)}

_MOCHILA = [
    "............",
    "....MMMM....",
    "...M....M...",
    "..BBBBBBBB..",
    ".BBbbbbbbBB.",
    ".BbbbbbbbbB.",
    ".BbbYYbbbbB.",
    ".BbbbbbbbbB.",
    ".BbbbbbbbbB.",
    ".BBBBBBBBBB.",
    "............",
    "............",
]
PALETA_MOCHILA = {"M": (120, 90, 60), "B": (140, 100, 60), "b": (190, 140, 80), "Y": (255, 214, 102)}

# ---------------------------------------------------------------------- #
#  Cohete chico para la animación final (16 x 9), con la punta a la derecha
# ---------------------------------------------------------------------- #
_COHETE_CHICO = [
    "......RR........",
    "...WWWWWWWW.....",
    "..WWWWWWWWWWW...",
    ".WWWBBWWWWWWWWR.",
    "WWWWBBWWWWWWWWWR",
    ".WWWWWWWWWWWWWR.",
    "..WWWWWWWWWWW...",
    "...WWWWWWWW.....",
    "......RR........",
]
PALETA_COHETE_CHICO = {"W": (232, 232, 242), "R": (220, 60, 60), "B": (110, 220, 250)}


# ---------------------------------------------------------------------- #
#  Texturas (16 x 16) que se repiten como baldosas sobre los pisos.
#  Tienen fondo transparente: solo agregan detalle (piedritas, grietas,
#  remaches) encima del degradado de cada escenario.
# ---------------------------------------------------------------------- #
_SUELO_MARTE = [
    "................",
    "..o.........l...",
    ".oo.............",
    "........d.......",
    "....l...........",
    "...........oo...",
    "..........oool..",
    "................",
    ".d..............",
    "......ool.......",
    ".....ooo........",
    "..............d.",
    "..l.............",
    "..........l.....",
    "....d...........",
    "................",
]
PALETA_SUELO_MARTE = {"o": (150, 62, 46), "l": (232, 132, 84), "d": (128, 52, 40)}

_SUELO_CUEVA = [
    "................",
    ".gg.........o...",
    "...g............",
    "....gg.....l....",
    "......g.........",
    "..o....g........",
    "........gg...o..",
    "..........g.....",
    "....l......g....",
    "............gg..",
    "..............g.",
    ".o..............",
    "........oo......",
    ".......ool......",
    "...l............",
    "................",
]
PALETA_SUELO_CUEVA = {"g": (118, 52, 40), "o": (132, 60, 44), "l": (200, 112, 74)}

_PISO_METAL = [
    "LLLLLLLLLLLLLLLS",
    "L.............dS",
    "L.R..........RdS",
    "L.............dS",
    "L.............dS",
    "L.............dS",
    "L......dd.....dS",
    "L.....d.......dS",
    "L.............dS",
    "L.............dS",
    "L.............dS",
    "L.............dS",
    "L.R..........RdS",
    "L.............dS",
    "LdddddddddddddDS",
    "SSSSSSSSSSSSSSSS",
]
PALETA_PISO_METAL = {"L": (128, 130, 154), "S": (56, 58, 76), "d": (74, 76, 98),
                     "D": (64, 66, 86), "R": (170, 172, 196)}


def _boletero(sup, rect, mate):
    """El boletero: un alien de piel celeste y bigote enorme, cebándose mate (mate = el momento, de 0 a 5)."""
    arte.minero(sup, rect, False, piel=(96, 164, 204), traje=(72, 52, 112), detalle=(224, 184, 64),
                gema=(255, 124, 84), antena=(255, 212, 92), bigote=True, mate=mate)


def _carnicero(sup, rect, dy_cabeza, mov_antena, parpadeo, brazo=None, hacha=False):
    """El carnicero: un alien rosado con delantal blanco y detalles rojos."""
    arte.minero(sup, rect, False, piel=(204, 100, 124), traje=(238, 234, 226), detalle=(176, 40, 52),
                gema=(120, 230, 250), antena=(255, 210, 100), dy_cabeza=dy_cabeza, mov_antena=mov_antena,
                parpadeo=parpadeo, brazo=brazo, hacha=hacha)


def _frutero(sup, rect, dy_cabeza, mov_antena, parpadeo, brazo=None):
    """El frutero: un alien naranja de ceño fruncido con delantal verde."""
    arte.minero(sup, rect, False, piel=(224, 120, 64), traje=(52, 96, 70), detalle=(200, 60, 72),
                gema=(255, 230, 110), antena=(120, 230, 150), enojado=True, dy_cabeza=dy_cabeza,
                mov_antena=mov_antena, parpadeo=parpadeo, brazo=brazo)


def _mercader(sup, rect, dy_cabeza, mov_antena, parpadeo, asustado=False):
    """La mercader: el mismo alien con otros colores (asustado: la cara de miedo de la playa)."""
    arte.minero(sup, rect, False, piel=(170, 110, 200), traje=(150, 50, 70), detalle=(240, 196, 70),
                gema=(110, 230, 245), antena=(250, 130, 190), dy_cabeza=dy_cabeza, mov_antena=mov_antena,
                parpadeo=parpadeo, asustado=asustado)


# ---------------------------------------------------------------------- #
#  Objetos grandes de los escenarios, dibujados con kepler/arte.py.
#  nombre: (tamaño del objeto, margen izq/arr/der/abj, función que lo dibuja)
#  El margen es el espacio extra para lo que sobresale (humo, tapa, teclado...).
# ---------------------------------------------------------------------- #
OBJETOS_GRANDES = {
    "capsula": ((240, 92), (6, 6, 6, 4), arte16.nave_estrellada),
    "caja_cerrada": ((22, 18), (2, 8, 4, 2), lambda sup, r: arte.caja(sup, r, False)),
    "caja_abierta": ((22, 18), (2, 8, 4, 2), lambda sup, r: arte.caja(sup, r, True)),
    "compuerta_cerrada": ((48, 56), (5, 5, 21, 2), lambda sup, r: arte16.compuerta(sup, r, False, False)),
    "compuerta_oscura": ((48, 56), (5, 5, 21, 2), lambda sup, r: arte16.compuerta(sup, r, True, False)),
    "compuerta_iluminada": ((48, 56), (5, 5, 21, 2), lambda sup, r: arte16.compuerta(sup, r, True, True)),
    "cartel": ((24, 20), (2, 2, 2, 14), arte16.cartel_peligro),
    "heladera_cerrada": ((32, 54), (2, 2, 10, 4), lambda sup, r: arte.heladera(sup, r, False)),
    "heladera_abierta": ((32, 54), (2, 2, 10, 4), lambda sup, r: arte.heladera(sup, r, True)),
    "cristal_grande": ((44, 52), (2, 2, 2, 2), arte.cristal_grande),
    "cofre_cerrado": ((20, 14), (1, 3, 1, 1), lambda sup, r: arte16.caja_negra(sup, r, False)),
    "cofre_abierto": ((20, 14), (1, 3, 1, 1), lambda sup, r: arte16.caja_negra(sup, r, True)),
    # El pico del minero, apoyado en la pared: solo la cabeza de metal, o el pico entero
    "cabeza_pico_pared": ((12, 12), (2, 2, 2, 2), lambda sup, r: arte.pico_pared(sup, r, False)),
    "pico_pared": ((12, 26), (2, 2, 2, 2), lambda sup, r: arte.pico_pared(sup, r, True)),
    # La mercader (otro alien, violeta, con otra ropa): 5 cuadros de animación (antenas, cabeza y parpadeo)
    # El frutero, del puesto de al lado: otro alien (naranja, con delantal verde) con cara de pocos amigos
    "frutero_f0": ((18, 30), (3, 7, 9, 2), lambda sup, r: _frutero(sup, r, 0, 0, False)),
    "frutero_f1": ((18, 30), (3, 7, 9, 2), lambda sup, r: _frutero(sup, r, -1, 1, False)),
    "frutero_f2": ((18, 30), (3, 7, 9, 2), lambda sup, r: _frutero(sup, r, -1, 0, False)),
    "frutero_f3": ((18, 30), (3, 7, 9, 2), lambda sup, r: _frutero(sup, r, 0, -1, False)),
    "frutero_f4": ((18, 30), (3, 7, 9, 2), lambda sup, r: _frutero(sup, r, 0, 0, True)),
    # El gesto de "largo de aquí": agita la mano de un lado al otro (dos cuadros)
    "frutero_gesto_a": ((18, 30), (3, 7, 9, 2), lambda sup, r: _frutero(sup, r, -1, 1, False, "lado_a")),
    "frutero_gesto_b": ((18, 30), (3, 7, 9, 2), lambda sup, r: _frutero(sup, r, -1, -1, False, "lado_b")),
    # El carnicero, del puesto de la izquierda: un alien rosado con delantal blanco. Mece las antenas, parpadea y,
    # de vez en cuando, levanta el hacha y corta un trozo de carne sobre la tabla.
    "carnicero_f0": ((18, 30), (3, 7, 9, 2), lambda sup, r: _carnicero(sup, r, 0, 0, False)),
    "carnicero_f1": ((18, 30), (3, 7, 9, 2), lambda sup, r: _carnicero(sup, r, -1, 1, False)),
    "carnicero_f2": ((18, 30), (3, 7, 9, 2), lambda sup, r: _carnicero(sup, r, -1, 0, False)),
    "carnicero_f3": ((18, 30), (3, 7, 9, 2), lambda sup, r: _carnicero(sup, r, 0, -1, False)),
    "carnicero_f4": ((18, 30), (3, 7, 9, 2), lambda sup, r: _carnicero(sup, r, 0, 0, True)),
    "carnicero_hacha_arriba": ((18, 30), (3, 11, 9, 2), lambda sup, r: _carnicero(sup, r, -1, 1, False, "arriba", True)),
    "carnicero_hacha_abajo": ((18, 30), (3, 11, 9, 2), lambda sup, r: _carnicero(sup, r, 0, -1, False, "abajo", True)),
    # El boletero: un alien de bigote enorme que atiende la boletería y se ceba mate. 6 cuadros: termo y mate quietos,
    # levanta el termo, sirve (dos cuadros para que la corriente se mueva), agarra el mate y sorbe.
    "boletero_f0": ((18, 30), (3, 7, 14, 2), lambda sup, r: _boletero(sup, r, 0)),
    "boletero_f1": ((18, 30), (3, 7, 14, 2), lambda sup, r: _boletero(sup, r, 1)),
    "boletero_f2": ((18, 30), (3, 7, 14, 2), lambda sup, r: _boletero(sup, r, 2)),
    "boletero_f3": ((18, 30), (3, 7, 14, 2), lambda sup, r: _boletero(sup, r, 3)),
    "boletero_f4": ((18, 30), (3, 7, 14, 2), lambda sup, r: _boletero(sup, r, 4)),
    "boletero_f5": ((18, 30), (3, 7, 14, 2), lambda sup, r: _boletero(sup, r, 5)),
    "mercader_f0": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, 0, 0, False)),
    "mercader_f1": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, -1, 1, False)),
    "mercader_f2": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, -1, 0, False)),
    "mercader_f3": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, 0, -1, False)),
    "mercader_f4": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, 0, 0, True)),
    # Con cara de susto (la mercader acorralada en la playa)
    "mercader_miedo_f0": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, 0, 0, False, True)),
    "mercader_miedo_f1": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, -1, 1, False, True)),
    "mercader_miedo_f2": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, -1, 0, False, True)),
    "mercader_miedo_f3": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, 0, -1, False, True)),
    "mercader_miedo_f4": ((18, 30), (3, 7, 3, 2), lambda sup, r: _mercader(sup, r, 0, 0, True, True)),
    "cohete_apagado": ((44, 92), (1, 4, 1, 1), lambda sup, r: arte16.cohete(sup, r, False)),
    "cohete_encendido": ((44, 92), (1, 4, 1, 1), lambda sup, r: arte16.cohete(sup, r, True)),
    "consola_apagada": ((30, 26), (1, 1, 1, 1), lambda sup, r: arte16.consola(sup, r, False)),
    "consola_encendida": ((30, 26), (1, 1, 1, 1), lambda sup, r: arte16.consola(sup, r, True)),
    "flecha_izquierda": ((14, 16), (0, 0, 0, 0), lambda sup, r: arte.flecha(sup, r, "izquierda")),
    "flecha_derecha": ((14, 16), (0, 0, 0, 0), lambda sup, r: arte.flecha(sup, r, "derecha")),
    "flecha_arriba": ((14, 16), (0, 0, 0, 0), lambda sup, r: arte.flecha(sup, r, "arriba")),
    "flecha_abajo": ((14, 16), (0, 0, 0, 0), lambda sup, r: arte.flecha(sup, r, "abajo")),
}


# El minero, sentado en una mecedora que se hamaca: un cuadro por cada ángulo (de atrás hacia adelante).
# La silla se gira alrededor del patín que apoya en el piso; el alien se corre sin deformarse.
ANGULOS_MECEDORA = (-5, -3.5, -2, -1, 0, 1, 2, 3.5, 5)


def _minero_en_mecedora(sup, rect, grados):
    arte.minero_mecedora(sup, rect, grados)


for _i, _grados in enumerate(ANGULOS_MECEDORA):
    OBJETOS_GRANDES[f"minero_silla_{_i}"] = ((18, 30), (5, 7, 5, 3),
                                             lambda sup, r, g=_grados: _minero_en_mecedora(sup, r, g))


def dibujar_objeto_con_codigo(nombre):
    """Dibuja un objeto grande en una imagen transparente de su tamaño más el margen."""
    (ancho, alto), (izq, arr, der, abj), funcion = OBJETOS_GRANDES[nombre]
    lienzo = pygame.Surface((izq + ancho + der, arr + alto + abj), pygame.SRCALPHA)
    funcion(lienzo, pygame.Rect(izq, arr, ancho, alto))
    return lienzo


def dibujar_objeto(sup, sprites, nombre, rect):
    """Pone el sprite de un objeto grande en la posición de su rectángulo."""
    izq, arr = OBJETOS_GRANDES[nombre][1][:2]
    sup.blit(sprites[nombre], (rect[0] - izq, rect[1] - arr))


def dibujar_flecha(sup, sprites, rect, direccion, tiempo):
    """La flecha de salida, centrada en su zona. Titila según el tiempo."""
    if int(tiempo * 2) % 2 == 0:
        return
    sprite = sprites["flecha_" + direccion]
    sup.blit(sprite, sprite.get_rect(center=pygame.Rect(rect).center))


def crear_sprites_desde_codigo():
    """Todo lo que se puede dibujar sin hoja: dibujos de letras y objetos de arte.py."""
    sprites = crear_sprites_desde_texto()
    for nombre in OBJETOS_GRANDES:
        sprites[nombre] = dibujar_objeto_con_codigo(nombre)
    return sprites


def _con_volumen(base, desde_fila=0, sin_tocar=()):
    """
    Le da volumen de 16 bits a un sprite plano (sin contorno): luz en los bordes que miran arriba y a
    la izquierda, sombra en los que miran abajo y a la derecha. Trabaja con los cambios de color y con
    el borde de la silueta. 'sin_tocar' son colores que se dejan planos (luces, paneles).
    """
    ancho, alto = base.get_size()
    salida = base.copy()

    def color(x, y):
        if not (0 <= x < ancho and 0 <= y < alto):
            return None
        c = base.get_at((x, y))
        return (c.r, c.g, c.b) if c.a > 0 else None

    for y in range(desde_fila, alto):
        for x in range(ancho):
            c = color(x, y)
            if c is None or c in sin_tocar:
                continue
            luz = color(x - 1, y) != c or color(x, y - 1) != c
            sombra = color(x + 1, y) != c or color(x, y + 1) != c
            if sombra and not luz:
                salida.set_at((x, y), arte._tono(c, -0.30))
            elif luz and not sombra:
                salida.set_at((x, y), arte._tono(c, 0.30))
            elif sombra and luz:
                salida.set_at((x, y), arte._tono(c, -0.12))
    return salida


def _astronauta_16bits(filas):
    """La astronauta con casco esférico sombreado, visor degradado con reflejo y traje con volumen."""
    paleta = PALETA_ASTRONAUTA
    base = crear_sprite(filas, paleta)               # plana, sin contorno
    salida = _con_volumen(base, desde_fila=11, sin_tocar=(paleta["O"], paleta["R"]))
    rampa = [(112, 118, 156), (160, 168, 200), (204, 210, 232), (236, 240, 250), (255, 255, 255)]
    cx, cy, rx, ry = 8.0, 5.4, 7.8, 6.4
    for y in range(11):                              # el casco: filas 0 a 10
        for x in range(base.get_width()):
            c = base.get_at((x, y))
            if c.a == 0:
                continue
            t = (c.r, c.g, c.b)
            if t == paleta["W"]:                     # carcasa del casco: esfera con luz arriba a la izquierda
                nx, ny = (x + 0.5 - cx) / rx, (y + 0.5 - cy) / ry
                nz = max(0.0, 1 - min(1.0, nx * nx + ny * ny)) ** 0.5
                luz = max(0.0, min(0.999, 0.18 + (-0.55 * nx - 0.5 * ny) * 0.55 + 0.55 * nz))
                salida.set_at((x, y), rampa[int(luz * len(rampa))])
            elif t == paleta["D"]:                   # visor: de azul profundo arriba a azul claro abajo
                k = min(1.0, max(0.0, (y - 3) / 6))
                salida.set_at((x, y), (int(26 + 40 * k), int(34 + 70 * k), int(92 + 104 * k)))
    for y in (4, 5):                                 # reflejo largo del visor, a la izquierda
        xs = [x for x in range(base.get_width()) if (lambda c: (c.r, c.g, c.b) == paleta["D"] and c.a)(base.get_at((x, y)))]
        if xs:
            salida.set_at((xs[0], y), (170, 222, 255))
            if y == 4 and len(xs) > 2:
                salida.set_at((xs[0] + 1, y), (120, 180, 250))
    return agregar_contorno(salida, CONTORNO)


def _icono_cuerda():
    """Un rollo de cuerda (12 x 12)."""
    sup = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(sup, CONTORNO, (1, 3, 10, 8))
    pygame.draw.ellipse(sup, (206, 170, 102), (2, 4, 8, 6))
    pygame.draw.ellipse(sup, CONTORNO, (4, 5, 4, 3))
    pygame.draw.ellipse(sup, (118, 90, 54), (5, 6, 2, 1))
    for x, y in ((3, 5), (5, 4), (8, 5), (9, 7), (4, 9), (7, 9)):
        sup.set_at((x, y), (244, 214, 150))                                   # hilos con luz
    pygame.draw.line(sup, CONTORNO, (9, 4), (11, 1))                          # la punta suelta
    sup.set_at((10, 2), (206, 170, 102))
    return sup


def _icono_carne():
    """Un trozo de carne con hueso (12 x 12)."""
    sup = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(sup, CONTORNO, (0, 2, 11, 9))
    pygame.draw.ellipse(sup, (206, 82, 90), (1, 3, 9, 7))
    pygame.draw.ellipse(sup, (240, 130, 130), (2, 4, 5, 3))
    pygame.draw.line(sup, (250, 226, 210), (3, 8), (7, 7))                    # vetas de grasa
    pygame.draw.rect(sup, CONTORNO, (8, 0, 4, 4))
    pygame.draw.rect(sup, (240, 234, 216), (9, 1, 2, 2))                      # el hueso
    return sup


def _icono_cana(con_cebo):
    """Una caña rudimentaria: palo con una cuerda que cuelga de la punta (con o sin un trozo de carne) (12 x 12)."""
    sup = pygame.Surface((12, 12), pygame.SRCALPHA)
    pygame.draw.line(sup, CONTORNO, (0, 11), (8, 3), 3)
    pygame.draw.line(sup, (150, 96, 54), (0, 10), (8, 2), 1)
    pygame.draw.line(sup, (196, 140, 88), (1, 10), (8, 3), 1)
    pygame.draw.line(sup, (236, 224, 190), (9, 2), (11, 6))                   # la cuerda
    if con_cebo:
        pygame.draw.rect(sup, CONTORNO, (9, 6, 3, 5))
        pygame.draw.rect(sup, (206, 82, 90), (10, 7, 1, 3))
        sup.set_at((10, 7), (250, 150, 150))
    else:
        sup.set_at((11, 7), (236, 224, 190))                                   # anzuelo vacío
        sup.set_at((10, 8), (190, 196, 214))
    return sup


def _perro_alien(boca_abierta):
    """
    Un perro alien que gruñe, mirando a la IZQUIERDA (30 x 18): pelaje violeta, púas rosadas en el lomo, tres ojos
    amarillos, colmillos y una cola con aleta. Con la boca abierta se le ve la garganta roja.
    """
    sup = pygame.Surface((30, 18), pygame.SRCALPHA)
    cuerpo, claro, oscuro = (96, 78, 156), (150, 130, 212), (54, 44, 98)
    espina, ojo = (244, 100, 184), (255, 232, 70)
    # Patas (las de adelante, más adelantadas y agachadas)
    for px in (10, 14, 21, 25):
        pygame.draw.rect(sup, CONTORNO, (px, 11, 4, 7))
        pygame.draw.rect(sup, cuerpo, (px + 1, 11, 2, 5))
        pygame.draw.rect(sup, oscuro, (px + 1, 16, 2, 1))
        sup.set_at((px, 17), (230, 230, 240))                                         # garritas
        sup.set_at((px + 3, 17), (230, 230, 240))
    # Cola con aleta
    pygame.draw.lines(sup, CONTORNO, False, [(26, 7), (28, 5), (28, 2)], 3)
    pygame.draw.lines(sup, cuerpo, False, [(26, 7), (28, 5), (28, 2)], 1)
    pygame.draw.polygon(sup, espina, [(28, 2), (26, 0), (29, 0)])
    # Cuerpo
    pygame.draw.ellipse(sup, CONTORNO, (8, 3, 20, 12))
    pygame.draw.ellipse(sup, cuerpo, (9, 4, 18, 10))
    pygame.draw.line(sup, claro, (12, 5), (23, 5))
    pygame.draw.line(sup, oscuro, (12, 12), (24, 12))
    for sx in (13, 17, 21):                                                           # púas del lomo
        pygame.draw.polygon(sup, CONTORNO, [(sx - 1, 4), (sx + 1, 0), (sx + 3, 4)])
        pygame.draw.polygon(sup, espina, [(sx, 4), (sx + 1, 1), (sx + 2, 4)])
    # Cabeza con el hocico hacia la izquierda
    pygame.draw.ellipse(sup, CONTORNO, (3, 2, 11, 11))
    pygame.draw.ellipse(sup, cuerpo, (4, 3, 9, 9))
    pygame.draw.polygon(sup, CONTORNO, [(0, 6), (7, 4), (8, 9), (1, 9)])              # hocico
    pygame.draw.polygon(sup, cuerpo, [(1, 7), (7, 5), (7, 8), (2, 8)])
    sup.set_at((0, 7), (20, 14, 30))                                                  # la nariz
    pygame.draw.polygon(sup, CONTORNO, [(9, 2), (11, 0), (12, 3)])                    # una oreja
    pygame.draw.polygon(sup, cuerpo, [(10, 2), (11, 1), (11, 3)])
    # Mandíbula de abajo
    if boca_abierta:
        pygame.draw.polygon(sup, CONTORNO, [(1, 9), (8, 9), (9, 14), (3, 14)])
        pygame.draw.polygon(sup, (160, 30, 54), [(2, 9), (7, 9), (7, 12), (3, 12)])
        pygame.draw.polygon(sup, cuerpo, [(3, 12), (8, 12), (8, 13), (4, 13)])
        for tx in (2, 4, 6):                                                          # colmillos de arriba y de abajo
            sup.set_at((tx, 9), (250, 250, 240))
        for tx in (3, 5):
            sup.set_at((tx, 11), (250, 250, 240))
        sup.set_at((3, 14), (150, 210, 250))                                         # baba
    else:
        pygame.draw.line(sup, CONTORNO, (1, 9), (8, 9))
        for tx in (2, 4, 6):
            sup.set_at((tx, 9), (250, 250, 240))
            sup.set_at((tx, 10), (250, 250, 240))
    # Tres ojos furiosos
    for ex, ey in ((7, 6), (9, 5), (11, 6)):
        sup.set_at((ex, ey), ojo)
    pygame.draw.line(sup, CONTORNO, (6, 4), (10, 3))
    return sup


def _caja_robot(sup, x, y, w, h, color):
    """Un bloque con contorno, luz arriba/izquierda y sombra abajo/derecha."""
    pygame.draw.rect(sup, CONTORNO, (x, y, w, h))
    pygame.draw.rect(sup, color, (x + 1, y + 1, w - 2, h - 2))
    luz, sombra = arte._tono(color, 0.35), arte._tono(color, -0.35)
    pygame.draw.line(sup, luz, (x + 1, y + 1), (x + w - 2, y + 1))
    pygame.draw.line(sup, luz, (x + 1, y + 1), (x + 1, y + h - 2))
    pygame.draw.line(sup, sombra, (x + 1, y + h - 2), (x + w - 2, y + h - 2))
    pygame.draw.line(sup, sombra, (x + w - 2, y + 1), (x + w - 2, y + h - 2))


def crear_robot(encendido, mirada=0, parpadeo=False, dy=0, luz=-1):
    """R-7 con la cabeza animable: 'mirada' (-1, 0, 1) mueve los ojos, 'parpadeo' cierra los ojos, 'dy' baja la cabeza
    un píxel y 'luz' (0 a 2) prende de a una las lucecitas del pecho (-1 = todas)."""
    return _robot_utilitario(encendido, mirada, parpadeo, dy, luz)


def _robot_utilitario(encendido, mirada=0, parpadeo=False, dy=0, luz=-1):
    """
    R-7, un robot de trabajo al estilo de un compactador de basura: cuerpo cuadrado y oxidado, orugas en vez
    de piernas, cuello corto con ojos tipo binoculares y brazos con pinzas (24 x 26). Apagado se ve opaco.
    """
    sup = pygame.Surface((24, 26), pygame.SRCALPHA)
    amarillo = (214, 164, 52) if encendido else (140, 120, 76)
    gris = (92, 96, 112) if encendido else (70, 72, 84)
    oruga = (54, 56, 66)
    # Orugas
    for x in (0, 14):
        pygame.draw.rect(sup, CONTORNO, (x, 20, 10, 6))
        pygame.draw.rect(sup, oruga, (x + 1, 21, 8, 4))
        for rx in (x + 3, x + 7):
            pygame.draw.circle(sup, (116, 120, 138), (rx, 23), 1)
        for rx in range(x + 1, x + 9, 2):
            sup.set_at((rx, 21), (34, 34, 44))
            sup.set_at((rx + 1, 24), (34, 34, 44))
    # Cuerpo: el cubo compactador, con óxido y un panel
    _caja_robot(sup, 4, 9, 16, 11, amarillo)
    pygame.draw.rect(sup, CONTORNO, (7, 12, 10, 5))
    pygame.draw.rect(sup, (58, 50, 36), (8, 13, 8, 3))
    for k, color in enumerate(((90, 230, 120), (250, 210, 80), (240, 80, 70))):
        prendida = encendido and (luz < 0 or luz == k)
        sup.set_at((9 + k * 2, 14), color if prendida else (40, 38, 34) if not encendido else tuple(c // 3 for c in color))
    for rx, ry in ((6, 10), (7, 10), (17, 18), (16, 18), (5, 17), (18, 11)):
        sup.set_at((rx, ry), (150, 84, 40) if encendido else (96, 70, 48))
    pygame.draw.line(sup, (150, 84, 40) if encendido else (96, 70, 48), (13, 17), (13, 19))
    # Brazos con pinzas
    for x in (0, 20):
        _caja_robot(sup, x + 1, 11, 3, 6, gris)
        pygame.draw.rect(sup, CONTORNO, (x, 17, 5, 3))
        sup.set_at((x + 2, 17), (0, 0, 0, 0))
        sup.set_at((x + 2, 18), (0, 0, 0, 0))
        sup.set_at((x + 1, 18), gris)
        sup.set_at((x + 3, 18), gris)
    # Cuello y ojos binoculares
    _caja_robot(sup, 10, 6, 4, 4, (62, 64, 78))
    for ex in (5, 12):
        _caja_robot(sup, ex, 1 + dy, 7, 7, (196, 164, 84) if encendido else (130, 116, 84))
        if parpadeo:                                         # ojos cerrados: una rayita
            pygame.draw.rect(sup, (10, 12, 20), (ex + 1, 4 + dy, 5, 2))
            continue
        pygame.draw.circle(sup, (10, 12, 20), (ex + 3, 4 + dy), 2)
        pygame.draw.circle(sup, (110, 240, 250) if encendido else (44, 46, 58), (ex + 3 + mirada, 4 + dy), 1)
        if encendido:
            sup.set_at((ex + 2 + mirada, 3 + dy), (255, 255, 255))
    return sup


def crear_sprites_desde_texto():
    """Arma todas las imágenes a partir de los dibujos de texto de este archivo."""
    return {
        "astronauta_quieto": _astronauta_16bits(_ASTRONAUTA_CUERPO + _PIERNAS_QUIETO),
        "astronauta_paso": _astronauta_16bits(_ASTRONAUTA_CUERPO + _PIERNAS_PASO),
        "astronauta_alza_izq": _astronauta_16bits(_ASTRONAUTA_CUERPO + _PIERNAS_ALZA_IZQ),
        "astronauta_alza_der": _astronauta_16bits(_ASTRONAUTA_CUERPO + _PIERNAS_ALZA_DER),
        "cuerda": _icono_cuerda(),
        "cana": _icono_cana(False),
        "cana_cebo": _icono_cana(True),
        "carne": _icono_carne(),
        "perro_alien_f0": _perro_alien(False),
        "perro_alien_f1": _perro_alien(True),
        "robot_apagado": _robot_utilitario(False),
        "robot_encendido": _robot_utilitario(True),
        "bateria": crear_sprite(_BATERIA, PALETA_BATERIA, CONTORNO),
        "cable": crear_sprite(_CABLE, PALETA_CABLE, CONTORNO),
        "bateria_con_cable": crear_sprite(_BATERIA_CON_CABLE, PALETA_BATERIA_CON_CABLE, CONTORNO),
        "linterna": crear_sprite(_LINTERNA, PALETA_LINTERNA, CONTORNO),
        "cristal": crear_sprite(_CRISTAL, PALETA_CRISTAL, CONTORNO),
        "pico": crear_sprite(_PICO, PALETA_PICO, CONTORNO),
        "cabeza_pico": crear_sprite(_CABEZA_PICO, PALETA_CABEZA_PICO, CONTORNO),
        "palo": crear_sprite(_PALO, PALETA_PALO, CONTORNO),
        "billetera": crear_sprite(_BILLETERA, PALETA_BILLETERA, CONTORNO),
        "plata": crear_sprite(_PLATA, PALETA_PLATA, CONTORNO),
        "boleto": crear_sprite(_BOLETO, PALETA_BOLETO, CONTORNO),
        "coca": crear_sprite(_COCA, PALETA_COCA, CONTORNO),
        "mochila": crear_sprite(_MOCHILA, PALETA_MOCHILA, CONTORNO),
        "cohete_chico": crear_sprite(_COHETE_CHICO, PALETA_COHETE_CHICO, CONTORNO),
        # Texturas: SIN contorno, para que se repitan sin costuras
        "textura_suelo_marte": crear_sprite(_SUELO_MARTE, PALETA_SUELO_MARTE),
        "textura_suelo_cueva": crear_sprite(_SUELO_CUEVA, PALETA_SUELO_CUEVA),
        "textura_piso_metal": crear_sprite(_PISO_METAL, PALETA_PISO_METAL),
    }


def crear_sprites():
    """
    Devuelve el diccionario nombre -> imagen con todos los sprites y texturas.
    Si hay hoja de sprites, lo que tenga la hoja reemplaza a los dibujos de
    texto (lo que falte en la hoja se sigue armando desde el texto).
    """
    sprites = crear_sprites_desde_codigo()
    if os.path.exists(RUTA_HOJA):
        sprites.update(HojaSprites(RUTA_HOJA).todos())
    return sprites
