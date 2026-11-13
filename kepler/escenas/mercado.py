"""
kepler/escenas/mercado.py
Escenario: el mercado, a la derecha de la cueva (y a la izquierda de la playa). Tiene tres puestos del mismo tamaño:

  - Carnicería (izquierda): la atiende un alien rosado que ofrece su carne. Es solo ambientación.
  - Cristales (medio): la atiende la mercader, pero por ahora el puesto está vacío: ella está acorralada en la
    playa (ver playa.py). Cuando vuelva (progreso['mercader_en_puesto']), usar un cristal sobre ella -> te paga
    200 keplesos (el precio del boleto a la plataforma).
  - Frutas (derecha): atiende un alien de mal humor que solo sabe echarte.
"""

import pygame

from engine import Escena, ObjetoEscena
from kepler import paisaje, arte16
from kepler.config import ANCHO, ALTO_ESCENA
from kepler.sprites import dibujar_objeto, dibujar_flecha
from kepler.dialogos import (dialogo_mercader, dialogo_mercader_compra, dialogo_frutero, dialogo_carnicero,
                              dialogo_carnicero_trueque)

# Dónde empieza (borde izquierdo) cada puesto: todos miden arte16.ANCHO_PUESTO
X_REPUESTOS, X_CRISTALES, X_FRUTAS = 16, 122, 228
# Quien atiende se dibuja detrás del mostrador, centrado en su puesto
Y_ATIENDE = 79
RECT_CARNICERO = pygame.Rect(X_REPUESTOS + arte16.ANCHO_PUESTO // 2 - 9, Y_ATIENDE, 18, 30)
RECT_MERCADER = pygame.Rect(X_CRISTALES + arte16.ANCHO_PUESTO // 2 - 9, Y_ATIENDE, 18, 30)
RECT_FRUTERO = pygame.Rect(X_FRUTAS + arte16.ANCHO_PUESTO // 2 - 9, Y_ATIENDE, 18, 30)


class EscenaMercado(Escena):
    def __init__(self, juego):
        self.juego = juego
        poligono = [(8, 108), (312, 108), (318, 147), (2, 147)]
        super().__init__("Mercado", (ANCHO, ALTO_ESCENA), poligono)
        sprites = juego.sprites
        ancho = arte16.ANCHO_PUESTO

        self.objetos = [
            ObjetoEscena("carnicería", (X_REPUESTOS, 58, ancho, 56), (X_REPUESTOS + 36, 122),
                         dibujo=self.dibujar_puesto_carniceria,
                         respuestas={
                             "Mirar": "Una carnicería: jamones, chorizos y un bife violeta que no quiero saber qué es. Lo atiende un alien rosado.",
                             "Agarrar": "No es mío. Mejor no tocar nada.",
                             "Usar": "No tengo hambre. Y menos de eso.",
                             "Hablar": self.hablar_carnicero,
                         },
                         usos=self.usos_carnicero()),
            # Los puestos con vendedor dibujan al vendedor y después el puesto, para que el mostrador le tape el cuerpo
            ObjetoEscena("puesto de cristales", (X_CRISTALES, 58, ancho, 56), (X_CRISTALES + 36, 122),
                         dibujo=self.dibujar_puesto_cristales,
                         respuestas={
                             "Mirar": self.mirar_puesto_cristales,
                             "Agarrar": "No voy a robar nada acá.",
                             "Usar": self.usar_puesto_cristales,
                             "Hablar": self.hablar_mercader,
                         },
                         usos={"cristal": self.vender_cristal}),
            ObjetoEscena("puesto de frutas", (X_FRUTAS, 58, ancho, 56), (X_FRUTAS + 36, 122),
                         dibujo=self.dibujar_puesto_frutas,
                         respuestas={
                             "Mirar": "Frutas raras de Kepler-7. Una es azul y se mueve. No, gracias.",
                             "Agarrar": "Mejor no robar en un mercado ajeno.",
                             "Usar": "No quiero comprar nada de ahí.",
                         }),
            # Los vendedores van al final: así los clics sobre ellos los atienden a ellos (se dibujan con su puesto)
            ObjetoEscena("mercader", (RECT_MERCADER.x, RECT_MERCADER.y, 18, 22), (X_CRISTALES + 36, 122),
                         visible_si=lambda: self.juego.progreso["mercader_en_puesto"],
                         respuestas={
                             "Mirar": "Un alien violeta con ropa de colores. Atiende el puesto.",
                             "Hablar": self.hablar_mercader,
                             "Usar": "No creo que le guste que lo use.",
                             "Agarrar": "No voy a cargar a un alien.",
                         },
                         usos={"cristal": self.vender_cristal}),
            ObjetoEscena("frutero", (RECT_FRUTERO.x, RECT_FRUTERO.y, 18, 22), (X_FRUTAS + 36, 122),
                         respuestas={
                             "Mirar": "Un alien naranja de ceño fruncido atiende el puesto de frutas.",
                             "Hablar": self.hablar_frutero,
                             "Usar": self.hablar_frutero,
                             "Agarrar": self.hablar_frutero,
                         }),
            ObjetoEscena("carnicero", (RECT_CARNICERO.x, RECT_CARNICERO.y, 18, 22), (X_REPUESTOS + 36, 122),
                         respuestas={
                             "Mirar": "Un alien rosado con delantal blanco. Atiende la carnicería.",
                             "Hablar": self.hablar_carnicero,
                             "Usar": "No creo que le guste que lo use.",
                             "Agarrar": "No voy a cargar a un alien.",
                         },
                         usos=self.usos_carnicero()),
            ObjetoEscena("la cueva", (0, 108, 14, 38), (12, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "izquierda", self.juego.tiempo),
                         salida=("cueva", (296, 126)),
                         respuestas={"Mirar": "Por ahí vuelvo a la entrada de la cueva."}),
            ObjetoEscena("la playa", (306, 108, 14, 38), (308, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "derecha", self.juego.tiempo),
                         salida=("playa", (20, 104)),
                         respuestas={"Mirar": "Un camino que sigue a la derecha. Se siente olor a mar."}),
        ]

    # ---------- Hablar y vender el cristal ----------

    def usos_carnicero(self):
        """Lo que se puede entregar al carnicero: una billetera vacía a cambio de carne."""
        return {"billetera_vacia": self.trueque_carne,
                "billetera": lambda: "Todavía tiene monedas. Mejor la guardo."}

    def trueque_carne(self):
        inventario = self.juego.inventario
        inventario.quitar("billetera_vacia")
        inventario.agregar("carne")
        self.juego.iniciar_dialogo(dialogo_carnicero_trueque())
        return None   # no dice nada: empieza el diálogo

    def hablar_carnicero(self):
        self.juego.iniciar_dialogo(dialogo_carnicero(self.juego))
        return None   # no dice nada: empieza el diálogo

    def hablar_frutero(self):
        self.juego.iniciar_dialogo(dialogo_frutero(self.juego))
        return None   # no dice nada: empieza el diálogo

    def mirar_puesto_cristales(self):
        if self.juego.progreso["mercader_en_puesto"]:
            return "Un puesto lleno de cristales de colores. Lo atiende un alien violeta."
        return "Un puesto lleno de cristales de colores. No hay nadie atendiendo."

    def usar_puesto_cristales(self):
        if self.juego.progreso["mercader_en_puesto"]:
            return "Mejor le hablo a la mercader."
        return "No hay nadie a quien comprarle ni venderle."

    def hablar_mercader(self):
        if not self.juego.progreso["mercader_en_puesto"]:
            return "¿Hola? ...Nadie atiende."
        self.juego.iniciar_dialogo(dialogo_mercader(self.juego))
        return None   # no dice nada: empieza el diálogo

    def vender_cristal(self):
        progreso = self.juego.progreso
        inventario = self.juego.inventario
        if not progreso["mercader_en_puesto"]:
            return "No hay nadie que me lo compre."
        if progreso["vendio_cristal"]:
            return "Ya me pagó. No creo que quiera comprar más cristales."
        inventario.quitar("cristal")
        inventario.agregar("plata")
        progreso["vendio_cristal"] = True
        self.juego.iniciar_dialogo(dialogo_mercader_compra())
        return None   # no dice nada: empieza el diálogo

    # ---------- Dibujo de los puestos ----------

    def dibujar_mercader(self, sup):
        """La mercader no se queda quieta: mece las antenas, sube y baja la cabeza y parpadea."""
        t = self.juego.tiempo
        if t % 3.4 < 0.18:
            nombre = "mercader_f4"                                  # parpadeo
        else:
            nombre = ("mercader_f0", "mercader_f1", "mercader_f2", "mercader_f3")[int((t % 1.6) / 0.4)]
        dibujar_objeto(sup, self.juego.sprites, nombre, RECT_MERCADER)

    def dibujar_puesto_cristales(self, sup, rect):
        if self.juego.progreso["mercader_en_puesto"]:
            self.dibujar_mercader(sup)
        arte16.puesto(sup, X_CRISTALES, (160, 96, 210), (242, 232, 216), arte16.mercaderia_cristales)

    def dibujar_puesto_carniceria(self, sup, rect):
        """
        El carnicero mece las antenas y parpadea; cada 3,2 segundos levanta el hacha y corta un trozo de carne sobre la
        tabla (el trozo se parte en dos y salta algún pedacito).
        """
        t = self.juego.tiempo
        c = t % 3.2
        if 1.2 <= c < 1.7:
            nombre = "carnicero_hacha_arriba"
        elif 1.7 <= c < 2.1:
            nombre = "carnicero_hacha_abajo"
        elif t % 3.4 < 0.18:
            nombre = "carnicero_f4"
        else:
            nombre = ("carnicero_f0", "carnicero_f1", "carnicero_f2", "carnicero_f3")[int((t % 1.6) / 0.4)]
        dibujar_objeto(sup, self.juego.sprites, nombre, RECT_CARNICERO)
        arte16.puesto(sup, X_REPUESTOS, (176, 46, 56), (242, 232, 216), arte16.mercaderia_carniceria)
        # El trozo de carne sobre la tabla: entero, partido en dos después del golpe, y uno nuevo
        tx, ty = X_REPUESTOS + 43, arte16.Y_MOSTRADOR - 6
        if 1.7 <= c < 2.8:
            sep = 2 if c >= 2.1 else 0
            for dx, ancho in ((-sep, 3), (3 + sep, 4)):
                pygame.draw.ellipse(sup, (30, 14, 20), (tx + dx - 1, ty - 1, ancho + 2, 5))
                pygame.draw.ellipse(sup, (210, 92, 92), (tx + dx, ty, ancho, 3))
            if 1.7 <= c < 2.0:                                           # pedacitos que saltan con el golpe
                u = (c - 1.7) / 0.3
                for k, (vx, vy) in enumerate(((-9, -16), (7, -20), (12, -12))):
                    sup.set_at((int(tx + 3 + vx * u), int(ty + vy * u + 30 * u * u)), (230, 110, 110))
        else:
            pygame.draw.ellipse(sup, (30, 14, 20), (tx - 1, ty - 1, 9, 5))
            pygame.draw.ellipse(sup, (210, 92, 92), (tx, ty, 7, 3))

    def dibujar_puesto_frutas(self, sup, rect):
        """El frutero, de mal humor: mece las antenas, parpadea y, cada tanto, agita la mano echando a los clientes."""
        t = self.juego.tiempo
        c = t % 5.0
        if 3.0 <= c < 4.2:
            nombre = "frutero_gesto_a" if int(c * 4) % 2 == 0 else "frutero_gesto_b"
        elif t % 3.9 < 0.18:
            nombre = "frutero_f4"
        else:
            nombre = ("frutero_f0", "frutero_f1", "frutero_f2", "frutero_f3")[int((t % 1.6) / 0.4)]
        dibujar_objeto(sup, self.juego.sprites, nombre, RECT_FRUTERO)
        arte16.puesto(sup, X_FRUTAS, (216, 66, 88), (242, 232, 216), arte16.mercaderia_frutas)

    # ---------- Fondo ----------

    def construir_fondo(self, sup):
        paisaje.cielo(sup)       # el mismo cielo que en las demás pantallas de exterior
        paisaje.cordillera(sup, [(0, 70), (30, 62), (64, 72), (100, 56), (140, 70), (180, 63), (225, 74),
                                 (262, 58), (300, 68), (320, 64)], 84, (150, 64, 92), (222, 110, 96))
        # Carpas de otros puestos, a lo lejos, asomando entre los puestos de adelante
        for x, color in ((91, (110, 190, 220)), (197, (230, 150, 70))):
            arte16.carpa(sup, x, 78, 30, color)
        paisaje.suelo_llano(sup, 84, [(176, 76, 66), (190, 88, 64), (200, 98, 66), (206, 104, 66),
                                      (196, 94, 60), (178, 82, 56)], 9)
        # Postes de madera (en los bordes y entre los puestos) que sujetan la guirnalda de banderines de punta a punta
        postes = (9, 106, 213, 311)
        for x in postes:
            arte16.poste_madera(sup, x, 47, 112)
        arte16.guirnalda(sup, [x + 1 for x in postes], 48, ((230, 80, 90), (110, 190, 220), (250, 210, 80)))
