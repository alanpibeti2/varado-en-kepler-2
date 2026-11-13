"""
kepler/config.py
Constantes del juego.
"""

import os

TITULO = "Varado en Kepler"

# Imágenes: hoja de sprites y fondos de cada escenario
CARPETA_ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
RUTA_HOJA = os.path.join(CARPETA_ASSETS, "hoja_sprites.png")
CARPETA_FONDOS = os.path.join(CARPETA_ASSETS, "fondos")
CARPETA_SONIDOS = os.path.join(CARPETA_ASSETS, "sonidos")   # efectos y voces (.ogg, .wav o .mp3)

# Resolución "lógica", como una consola de 16 bits. pygame agranda la ventana.
ANCHO = 320
ALTO = 200
FPS = 60

# Arriba va el escenario (0 a ALTO_ESCENA); abajo, el panel de verbos
ALTO_ESCENA = 150

# ---- Paleta de la interfaz ----
NEGRO = (8, 6, 16)
BLANCO = (240, 236, 255)
AMARILLO = (255, 214, 102)
CIAN = (120, 230, 240)
GRIS = (140, 132, 160)
TEXTO_HABLA = (255, 226, 130)     # lo que dice el astronauta
MARRON_CARTEL = (122, 84, 52)     # fondo de los carteles de madera

UI_FONDO = (34, 26, 62)
UI_LUZ = (84, 70, 140)
UI_SOMBRA = (14, 10, 30)
UI_HUNDIDO = (22, 16, 42)

COLORES_BOTON = {
    "fondo": (52, 40, 90),
    "fondo_activo": (98, 74, 156),
    "luz": (132, 112, 204),
    "sombra": (20, 14, 40),
    "texto": BLANCO,
    "texto_activo": AMARILLO,
    "texto_apagado": (100, 92, 130),
}

# Claves del progreso de la historia (se ponen en True a medida que avanzás)
PROGRESO_INICIAL = (
    "robot_activo",
    "hablo_con_robot",
    "vio_boleteria",
    "sabe_codigo",
    "linterna_dada",
    "compuerta_abierta",
    "cueva_iluminada",
    "heladera_abierta",
    "cofre_abierto",
    "intento_romper_cristal",
    "hablo_con_minero",
    "pico_dado",
    "cristal_minado",
    "hablo_con_mercader",
    "mercader_en_puesto",        # False hasta que se resuelva lo de la playa: mientras tanto el puesto está vacío
    "mercader_pidio_ayuda",
    "pregunto_keplesos",        # le preguntó a R-7 cómo conseguir keplesos (recién ahí aparece la pregunta de la mina)
    "pregunto_planeta",         # ya con el boleto, le preguntó al boletero a qué planeta ir (y no sabe)
    "perro_ahuyentado",         # el perro de la playa salió corriendo detrás del cebo
    "hablo_con_frutero",
    "hablo_con_carnicero",
    "hablo_con_boletero",
    "vendio_cristal",
    "compro_boleto",
    "boleto_usado",
)
