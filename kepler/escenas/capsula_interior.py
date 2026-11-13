"""
kepler/escenas/capsula_interior.py
Escenario: el interior de la nave rota (la cabina del transbordador). Es una cabina baja y apretada:
techo con conductos, una consola llena de botones con luces, pantallas, medidores y cableado.

  1. Usar la heladera -> se abre y se ve una botella de coca de 3 litros.
  2. Agarrar la coca (sirve para negociar con el minero).
El resto de las cosas (consola, pantallas, asientos, casilleros, botiquín, extintor, mate, foto, cables)
es ambientación: se pueden mirar y probar, pero no llevan a ningún lado.
"""

import pygame

from engine import Escena, ObjetoEscena, rellenar_textura
from kepler import arte, arte16, paisaje
from kepler.config import ANCHO, ALTO_ESCENA
from kepler.sprites import dibujar_objeto, dibujar_flecha


ESCALA = 0.65     # las cosas de la cabina se achican a 0.65 para que la astronauta (32 px) no quede chiquita
TECHO = 74        # hasta dónde baja el techo (la cabina es chata)
PISO = 136        # hasta dónde llega el piso por donde se camina (debajo hay un zócalo)


def reducida(sup, x, y, ancho, alto, dibujar):
    """Dibuja algo con 'dibujar(capa)' en una capa de ancho x alto, la achica a ESCALA y la pone con la esquina en (x, y)."""
    capa = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    dibujar(capa)
    tam = (round(ancho * ESCALA), round(alto * ESCALA))
    sup.blit(pygame.transform.scale(capa, tam), (x, y))


class EscenaCapsulaInterior(Escena):
    zoom = 1.4      # adentro de la nave la cámara se acerca: así la cabina no se ve tan alta
    zoom_y = 42     # se ve desde el borde del techo hasta el piso

    def __init__(self, juego):
        self.juego = juego
        poligono = [(8, 112), (312, 112), (318, PISO), (2, PISO)]
        super().__init__("Interior de la nave", (ANCHO, ALTO_ESCENA), poligono)
        sprites = juego.sprites
        tiempo = lambda: self.juego.tiempo      # noqa: E731  (para las partes animadas)

        self.objetos = [
            ObjetoEscena("techo", (0, 0, ANCHO, TECHO), (160, 122),
                         respuestas={
                             "Mirar": "El techo está tan bajo que casi lo toco con la mano.",
                             "Usar": "No hay nada que hacer con el techo.",
                             "Agarrar": "No llego... y no me serviría.",
                         }),
            ObjetoEscena("luces del techo", (0, 0, 0, 0), (160, 122),
                         dibujo=lambda sup, r: arte16.luces_techo(sup, tiempo())),
            ObjetoEscena("heladera", (210, 77, 21, 35), (220, 122),
                         dibujo=self.dibujar_heladera,
                         respuestas={
                             "Mirar": self.mirar_heladera,
                             "Usar": self.usar_heladera,
                             "Agarrar": "Pesa demasiado, y está atornillada al piso.",
                             "Hablar": "Qué fría que sos. Literalmente.",
                         }),
            ObjetoEscena("coca de 3L", (214, 84, 9, 12), (220, 122),
                         dibujo=lambda sup, r: sup.blit(pygame.transform.scale(sprites["coca"], (r.w, r.h)), r),
                         id_item="coca",
                         visible_si=lambda: self.juego.progreso["heladera_abierta"],
                         respuestas={"Mirar": "Una botella de coca de 3 litros. Está fría y con gas."}),
            ObjetoEscena("ventana", (59, 83, 18, 18), (68, 122),
                         respuestas={
                             "Mirar": "Por la ventana se ven las estrellas. Y ni una sola ciudad.",
                             "Usar": "Está sellada.",
                             "Agarrar": "Es parte de la nave.",
                         }),
            ObjetoEscena("consola", (106, 80, 35, 26), (122, 122),
                         dibujo=lambda sup, r: reducida(sup, r.x, r.y, 54, 40, lambda c: arte16.consola_principal(c, 0, 0, tiempo())),
                         respuestas={
                             "Mirar": "La consola de la nave: un millón de botones con lucecitas. Salta alguna chispa de vez en cuando.",
                             "Usar": "No responde. La nave ya no vuela más.",
                             "Agarrar": "Está soldada al tablero.",
                             "Hablar": "Consola, ¿me escuchás? Nada.",
                         }),
            ObjetoEscena("pantallas", (108, 82, 31, 9), (122, 122),
                         respuestas={
                             "Mirar": "Un radar y mis signos vitales. El latido sigue normal, por suerte.",
                             "Usar": "Toco la pantalla y no pasa nada.",
                             "Agarrar": "Están soldadas a la consola.",
                             "Hablar": "¿Qué me estás diciendo, pantalla? No entiendo.",
                         }),
            ObjetoEscena("botones", (108, 92, 31, 8), (122, 122),
                         respuestas={
                             "Mirar": "Muchísimos botones con luces que titilan. Mejor no apretar nada raro.",
                             "Usar": "Aprieto uno al azar... Nada. Qué alivio.",
                             "Agarrar": "Están pegados a la consola.",
                         }),
            ObjetoEscena("medidores", (144, 80, 16, 18), (152, 122),
                         dibujo=lambda sup, r: reducida(sup, r.x, r.y, 24, 28, lambda c: arte16.medidores(c, 0, 0, tiempo())),
                         respuestas={
                             "Mirar": "Los medidores tienen las agujas temblando. Mala señal.",
                             "Usar": "Golpeo un reloj y la aguja salta un poco. Sigue igual.",
                             "Agarrar": "Están atornillados.",
                         }),
            ObjetoEscena("telemetría", (6, 78, 23, 9), (18, 122),
                         dibujo=lambda sup, r: reducida(sup, r.x, r.y, 36, 14, lambda c: arte16.telemetria(c, 0, 0, tiempo())),
                         respuestas={
                             "Mirar": "Una pantalla con barritas que suben y bajan. No sé qué miden.",
                             "Usar": "No responde a nada.",
                             "Agarrar": "Está empotrada en la pared.",
                         }),
            # ---- Ambientación: no hacen falta para avanzar ----
            ObjetoEscena("asiento del piloto", (80, 86, 18, 26), (89, 122),
                         respuestas={
                             "Mirar": "Mi asiento de piloto. Quedó torcido por el golpe.",
                             "Usar": "Mejor no sentarme: el arnés quedó medio flojo.",
                             "Agarrar": "Está atornillado al piso.",
                             "Hablar": "Aguantaste todo el viaje. Gracias.",
                         }),
            ObjetoEscena("asiento del copiloto", (166, 86, 18, 26), (175, 122),
                         respuestas={
                             "Mirar": "El asiento del copiloto. Viajé solo, así que nadie lo usó.",
                             "Usar": "No tengo tiempo de sentarme.",
                             "Agarrar": "Está atornillado al piso.",
                             "Hablar": "Silencio de copiloto. Como siempre.",
                         }),
            ObjetoEscena("casilleros", (252, 75, 44, 37), (274, 122),
                         respuestas={
                             "Mirar": "Los casilleros de la nave. Con el golpe se trabaron casi todos.",
                             "Usar": "Están trabados. No hay forma de abrirlos.",
                             "Agarrar": "No me voy a llevar un casillero.",
                             "Hablar": "Casilleros, ¿alguien en casa? No.",
                         }),
            ObjetoEscena("botiquín", (6, 90, 10, 10), (14, 122),
                         respuestas={
                             "Mirar": "Un botiquín de pared. Por suerte, no lo necesito.",
                             "Usar": "No me duele nada. Por ahora.",
                             "Agarrar": "Está bien donde está.",
                         }),
            ObjetoEscena("extintor", (36, 92, 7, 20), (42, 122),
                         respuestas={
                             "Mirar": "Un extintor. Por suerte no hubo incendio.",
                             "Usar": "No hay fuego que apagar.",
                             "Agarrar": "Pesa, y no lo necesito.",
                         }),
            ObjetoEscena("foto", (32, 78, 9, 8), (38, 122),
                         respuestas={
                             "Mirar": "Una foto de mi gato. Seguro está furioso porque lo dejé solo.",
                             "Usar": "La tengo bien pegada. Que se quede.",
                             "Agarrar": "Mejor que se quede en la nave.",
                         }),
            ObjetoEscena("mate y termo", (18, 100, 12, 11), (22, 122),
                         respuestas={
                             "Mirar": "Mi mate y mi termo. El agua se enfrió hace rato.",
                             "Usar": "Sin agua caliente no tiene gracia.",
                             "Agarrar": "Lo dejo acá. Tengo otras prioridades.",
                         }),
            ObjetoEscena("parche de la misión", (83, 75, 12, 12), (89, 122),
                         respuestas={
                             "Mirar": "El parche de mi misión: la Tierra con un aro rojo. Qué lejos que está ahora.",
                             "Usar": "Es solo un parche cosido a la pared.",
                             "Agarrar": "Se queda con la nave. Como mi suerte.",
                         }),
            ObjetoEscena("reloj", (188, 78, 18, 9), (196, 122),
                         dibujo=lambda sup, r: arte16.reloj_digital(sup, r.x, r.y, tiempo()),
                         respuestas={
                             "Mirar": "El reloj de la misión se quedó clavado en las 03:47: la hora del choque.",
                             "Usar": "Lo toco y sigue marcando la misma hora.",
                             "Agarrar": "Está atornillado a la pared.",
                         }),
            ObjetoEscena("mapa de ruta", (44, 76, 14, 9), (50, 122),
                         respuestas={
                             "Mirar": "La ruta del vuelo, a mano. La cruz roja era mi destino. Quedé lejísimos.",
                             "Usar": "No me sirve de nada acá.",
                             "Agarrar": "Prefiero dejarlo pegado.",
                         }),
            ObjetoEscena("caño", (312, 74, 5, 38), (306, 122),
                         respuestas={
                             "Mirar": "Un caño con una válvula roja. Mejor no tocarla.",
                             "Usar": "La válvula está trabada.",
                             "Agarrar": "Es parte de la nave.",
                         }),
            ObjetoEscena("cables", (238, 74, 16, 28), (240, 122),
                         dibujo=self.dibujar_chispas,
                         respuestas={
                             "Mirar": "Cables pelados colgando del techo. A veces sueltan chispas.",
                             "Usar": "Ni loco los toco.",
                             "Agarrar": "Ni loco.",
                             "Hablar": "Cables, quédense quietos.",
                         }),
            # El desastre del golpe: papeles, una placa caída y herramientas por el piso, y chispas que saltan
            ObjetoEscena("escombros", (110, 116, 50, 20), (134, 126),
                         respuestas={
                             "Mirar": "El golpe dejó todo patas para arriba: una placa del techo caída, papeles y tornillos por el piso.",
                             "Usar": "No hay nada que arreglar con esto.",
                             "Agarrar": "Es pura chatarra.",
                         }),
            ObjetoEscena("cable pelado", (176, 112, 38, 16), (190, 126),
                         respuestas={
                             "Mirar": "Un cable arrancado que echa chispas. Mejor no pisarlo.",
                             "Usar": "Ni loco lo toco.",
                             "Agarrar": "Ni loco lo toco.",
                         }),
            ObjetoEscena("chispas", (0, 0, 0, 0), (160, 122), dibujo=self.dibujar_chispas_piso),
            ObjetoEscena("la salida", (0, 108, 14, 28), (12, 128),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "izquierda", self.juego.tiempo),
                         salida=("choque", (150, 124)),
                         respuestas={"Mirar": "La escotilla de la nave. Por ahí salgo."}),
        ]

    # ---------- Heladera ----------

    def dibujar_heladera(self, sup, rect):
        nombre = "heladera_abierta" if self.juego.progreso["heladera_abierta"] else "heladera_cerrada"
        reducida(sup, rect.x, rect.y, 32, 54, lambda c: dibujar_objeto(c, self.juego.sprites, nombre, pygame.Rect(0, 0, 32, 54)))

    def mirar_heladera(self):
        if self.juego.progreso["heladera_abierta"]:
            return "La heladera está abierta."
        return "Una heladera. Sigue enchufada de milagro."

    def usar_heladera(self):
        progreso = self.juego.progreso
        if progreso["heladera_abierta"]:
            return "Ya está abierta."
        progreso["heladera_abierta"] = True
        return "La abrí. Adentro hay una botella de coca de 3 litros."

    # ---------- Chispas (animado) ----------

    def dibujar_chispas_piso(self, sup, rect):
        """Chispas del cable que cuelga y del cable del piso, de la consola y de los medidores; y un parpadeo de la luz."""
        t = self.juego.tiempo
        arte16.chispas(sup, 178, 126, t, fase=0.0, periodo=1.1)
        arte16.chispas(sup, 140, 80, t, fase=0.5, periodo=2.3, n=5)             # la consola
        arte16.chispas(sup, 152, 80, t, fase=1.4, periodo=3.1, n=4)             # los medidores
        arte16.chispas(sup, 246, 76, t, fase=0.9, periodo=1.7, n=5)             # los casilleros trabados
        if t % 6.0 < 0.12 or 3.0 < t % 6.0 < 3.07:                              # la luz parpadea
            sup.blit(self._oscuridad(), (0, 0))

    def _oscuridad(self):
        if not hasattr(self, "_trama_oscura"):
            self._trama_oscura = pygame.Surface((ANCHO, ALTO_ESCENA), pygame.SRCALPHA)
            for y in range(ALTO_ESCENA):
                for x in range(y % 2, ANCHO, 2):
                    self._trama_oscura.set_at((x, y), (8, 8, 16, 255))
        return self._trama_oscura

    def dibujar_chispas(self, sup, rect):
        """Los cables sueltan una chispa de vez en cuando: aparece un destello en las puntas peladas."""
        t = self.juego.tiempo
        for i, (px, py) in enumerate(arte16.puntas_cables(238, 74)):
            if int(t * 5 + i * 2) % 9 == 0:
                for dx, dy, c in ((0, 0, (255, 240, 150)), (1, 0, (255, 190, 80)), (-1, 1, (255, 190, 80)),
                                  (0, 2, (255, 240, 150)), (2, 2, (255, 150, 60))):
                    sup.set_at((px + dx, py + 2 + dy), c)

    # ---------- Fondo ----------

    @staticmethod
    def viga_baja(sup):
        """Una viga ancha que baja el techo hasta TECHO: la cabina es chata. Con remaches, costillas y franja de aviso."""
        arte16.pared_densa(sup, 0, 31, ANCHO, TECHO - 8, semilla=3)           # el techo también lleva equipos y cables
        for y in range(31, TECHO - 8):                                         # en sombra: trama de puntos negros (50 %)
            for x in range((y % 2), ANCHO, 2):
                sup.set_at((x, y), (10, 10, 18))
        arte16.cables_colgantes(sup, 0, ANCHO, 38, 12, semilla=21, caida=10)
        pygame.draw.line(sup, (120, 124, 152), (0, 31), (ANCHO, 31))
        pygame.draw.rect(sup, (50, 54, 76), (0, TECHO - 8, ANCHO, 8))
        pygame.draw.line(sup, (20, 22, 34), (0, TECHO - 1), (ANCHO, TECHO - 1))
        pygame.draw.rect(sup, (230, 190, 40), (0, TECHO - 8, ANCHO, 2))            # franja de aviso
        for x in range(0, ANCHO, 8):
            pygame.draw.rect(sup, (34, 30, 44), (x + 4, TECHO - 8, 4, 2))

    def construir_fondo(self, sup):
        # Pared metálica con paneles (debajo del techo bajo)
        arte16.pared_densa(sup, 0, 0, ANCHO, 112)       # toda la pared cubierta de equipos, como en una estación espacial
        arte16.techo(sup)
        self.viga_baja(sup)
        # Ventana redonda con las estrellas afuera
        pygame.draw.circle(sup, (36, 40, 58), (68, 92), 10)
        pygame.draw.circle(sup, (10, 8, 24), (68, 92), 8)
        arte.estrellas(sup, (62, 86, 12, 12), 5, semilla=5)
        pygame.draw.circle(sup, (150, 154, 176), (68, 92), 9, 2)
        pygame.draw.line(sup, (90, 100, 130), (63, 87), (73, 97))                 # rajadura en el vidrio
        # Piso metálico
        paisaje.degradado_tramado(sup, (0, 112, ANCHO, PISO - 112), [(66, 68, 90), (84, 86, 108), (98, 100, 126)])
        rellenar_textura(sup, self.juego.sprites["textura_piso_metal"], (0, 112, ANCHO, PISO - 112))
        pygame.draw.rect(sup, (30, 32, 44), (0, 110, ANCHO, 2))
        # Zócalo oscuro al pie de la pantalla: carriles, franja de aviso y remaches (baja el piso)
        pygame.draw.rect(sup, (28, 30, 42), (0, PISO, ANCHO, ALTO_ESCENA - PISO))
        pygame.draw.line(sup, (120, 124, 152), (0, PISO), (ANCHO, PISO))
        pygame.draw.line(sup, (70, 74, 100), (0, PISO + 1), (ANCHO, PISO + 1))
        for x in range(0, ANCHO, 8):
            pygame.draw.rect(sup, (230, 190, 40) if (x // 8) % 2 == 0 else (34, 30, 44), (x, PISO + 4, 8, 3))
        for x in range(6, ANCHO, 20):
            sup.set_at((x, PISO + 10), (110, 114, 142))

        # Cablerío por las paredes
        arte16.cableado(sup, 4, TECHO + 2, 104, ((230, 70, 70), (240, 200, 70), (90, 170, 240)))
        arte16.cableado(sup, 114, 96, 112, ((230, 70, 70), (96, 220, 130)))
        arte16.cableado(sup, 246, TECHO + 2, 112, ((240, 200, 70), (90, 170, 240), (230, 70, 70)))
        arte16.cableado(sup, 88, TECHO + 2, 80, ((96, 220, 130), (240, 200, 70)))
        # Las cosas de la cabina, achicadas a 3/4 de su tamaño original
        reducida(sup, 252, 75, 70, 58, lambda c: arte16.casilleros(c, 2, 2, 3, 2, deformado=(1, 1)))
        reducida(sup, 32, 78, 14, 12, lambda c: arte16.foto(c, 0, 0))
        reducida(sup, 6, 90, 16, 16, lambda c: arte16.botiquin(c, 0, 0))
        reducida(sup, 36, 92, 11, 31, lambda c: arte16.extintor(c, 0, 0))
        reducida(sup, 80, 86, 28, 40, lambda c: arte16.asiento(c, 0, 0))
        reducida(sup, 166, 86, 28, 40, lambda c: arte16.asiento(c, 0, 0))
        reducida(sup, 18, 100, 18, 17, lambda c: arte16.estante_mate(c, 0, 14))
        arte16.cables(sup, 238, 74)
        arte16.escombros(sup)
        arte16.cables_colgantes(sup, 0, ANCHO, TECHO, 16, semilla=5)
        arte16.cables_colgantes(sup, 0, ANCHO, TECHO + 18, 8, semilla=9, caida=10)
        # Más cosas de la cabina
        arte16.base_consola(sup, 108, 106, 32, 6)
        arte16.parche_mision(sup, 83, 75)
        arte16.mapa_ruta(sup, 44, 76)
        arte16.tubo_vertical(sup, 312, 74, 38)
