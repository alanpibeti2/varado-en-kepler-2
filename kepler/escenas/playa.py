"""
kepler/escenas/playa.py
Escenario: la playa, a la derecha del mercado. Se llega al borde de un barranco: la astronauta queda parada arriba,
en una cornisa de tierra anaranjada. Abajo, mucho más abajo, hay una playa de arena amarilla y un mar verde.
No hay forma de bajar. Abajo está la mercader de los cristales, acorralada por un perro alien contra la pared
del barranco.

PUZLE: con la caña rudimentaria (palo + cuerda, de la caja negra) y un cebo de carne (se la cambia al carnicero
por la billetera vacía, después de dársela al robot) se usa la caña con cebo sobre el perro. Es una animación que
hace sola la astronauta: va hasta el borde, saca la caña, la estira sobre el vacío, baja el cebo hasta la cara del
perro (que se acerca, se calma y lo mira) y después lo revolea bien lejos. El perro sale corriendo detrás, la
mercader agradece y vuelve a su puesto.
"""

import math

import pygame

from engine import Escena, ObjetoEscena
from kepler import paisaje, arte
from kepler.arte16 import _elegir
from kepler.config import ANCHO, ALTO_ESCENA
from kepler.sprites import dibujar_flecha, dibujar_objeto
from kepler.dialogos import dialogo_mercader_acorralada, dialogo_mercader_rescatada

Y_CIMA = 92          # donde empieza la cornisa (el fondo de la tierra, lejos)
Y_BORDE = 116        # el borde delantero de la cornisa, donde empieza la pared del barranco
X_BORDE = 148        # hasta dónde llega la cornisa por la derecha (después, el vacío)
Y_MAR = 100          # el horizonte del mar
ORILLA = 128         # más o menos donde termina el agua y empieza la arena
Y_PIE = 142          # donde termina la pared del barranco: de ahí para abajo la playa sigue por delante, hacia la izquierda
PUNTO_BORDE = (134, 106)                         # donde se para la astronauta en el borde (de ahí usa la caña)
RECT_MERCADER = pygame.Rect(152, 116, 18, 30)    # la mercader, al pie del barranco, pegada a la pared
RECT_PERRO = pygame.Rect(222, 130, 30, 18)       # el perro alien, frente a ella (a unos pasos)

# La animación de la caña (segundos desde que empieza)
LARGO_CANA = 48          # la caña mide bastante más que la astronauta, para llegar sobre el vacío
T_SACA, T_ESTIRA, T_BAJA, T_SUELTA = 0.5, 1.3, 2.5, 4.0
T_PERRO_SE_ACERCA = 1.6
T_FIN = 5.0
X_PERRO_CEBO = 183       # donde queda el perro cuando está oliendo el cebo


def _orilla(x):
    """La línea de la orilla (varía con x, como una costa)."""
    return ORILLA + 3 * math.sin(x / 23.0) + 2 * math.sin(x / 9.0 + 1.0)


def _suave(u):
    u = max(0.0, min(1.0, u))
    return u * u * (3 - 2 * u)


class EscenaPlaya(Escena):
    def __init__(self, juego):
        self.juego = juego
        self.t_rescate = None          # None hasta que se usa la caña con cebo; después, segundos desde que empieza
        self.fase = "perro"            # "perro" (la animación) -> "huida" (corre la mercader) -> "listo"
        self.mercader_dx = 0.0
        self.hablo_cebo = False
        poligono = [(8, 94), (140, 94), (146, 114), (4, 114)]
        super().__init__("Playa", (ANCHO, ALTO_ESCENA), poligono)
        sprites = juego.sprites

        self.objetos = [
            ObjetoEscena("mar", (160, 100, 160, 26), PUNTO_BORDE,
                         dibujo=self.dibujar_olas,
                         respuestas={
                             "Mirar": "Un mar verde que brilla raro. Desde acá no se ve ni una isla.",
                             "Usar": "Está lejísimos. Y abajo.",
                             "Agarrar": "No llego.",
                             "Hablar": "¡Ehhh! ...Solo el viento.",
                         }),
            ObjetoEscena("playa", (160, 128, 160, 22), PUNTO_BORDE,
                         respuestas={
                             "Mirar": "Una playa de arena amarilla, tranquila, muy abajo. Daría lo que sea por bajar.",
                             "Usar": "Desde acá arriba no puedo.",
                             "Agarrar": "No llego a la arena.",
                         }),
            ObjetoEscena("barranco", (0, 116, 152, 34), PUNTO_BORDE,
                         respuestas={
                             "Mirar": "Un barranco altísimo, de tierra anaranjada. No hay cómo bajar.",
                             "Usar": "Ni loco me tiro de acá.",
                             "Agarrar": "Se desmorona en mis manos.",
                         }),
            ObjetoEscena("borde", (124, 94, 26, 22), PUNTO_BORDE,
                         respuestas={
                             "Mirar": "El borde de la cornisa. Un paso más y me convierto en parte del paisaje.",
                             "Usar": "Mejor me quedo a una distancia segura.",
                             "Agarrar": "Solo hay tierra suelta.",
                         }),
            # Abajo, contra la pared del barranco: la mercader de los cristales, acorralada por un perro alien
            ObjetoEscena("mercader", RECT_MERCADER, PUNTO_BORDE,
                         dibujo=self.dibujar_mercader,
                         visible_si=lambda: not self.juego.progreso["mercader_en_puesto"],
                         respuestas={
                             "Mirar": "Una alien en apuros siendo intimidada por un perro. Debería hacer algo.",
                             "Hablar": self.hablar_mercader,
                             "Usar": "Está muy abajo. No llego.",
                             "Agarrar": "Está muy abajo. No llego.",
                         },
                         usos={"cristal": lambda: "Está muy abajo, no llego a dárselo.",
                               "cana_cebo": lambda: "El cebo no es para ella."}),
            ObjetoEscena("perro alien", RECT_PERRO, PUNTO_BORDE,
                         dibujo=self.dibujar_perro,
                         visible_si=lambda: not self.juego.progreso["mercader_en_puesto"],
                         respuestas={
                             "Mirar": "Un perro alien enorme, con púas rosadas y tres ojos. Le gruñe a la mercader.",
                             "Hablar": "¡Ehh, perro! ...Ni me mira.",
                             "Usar": "Ni loco me acerco.",
                             "Agarrar": "Ni loco me acerco.",
                         },
                         usos={"cana_cebo": self.usar_cana,
                               "cana": lambda: "Sin cebo, ni me mira.",
                               "carne": lambda: "Si se la tiro así, vuelve enseguida."}),
            ObjetoEscena("caña", (0, 0, 0, 0), PUNTO_BORDE, dibujo=self.dibujar_cana),
            ObjetoEscena("el mercado", (0, 90, 14, 28), (12, 104),
                         dibujo=lambda sup, r: dibujar_flecha(sup, sprites, r, "izquierda", self.juego.tiempo),
                         salida=("mercado", (298, 126)),
                         respuestas={"Mirar": "Por ahí vuelvo al mercado."}),
        ]

    # ---------- La mercader y el perro ----------

    def hablar_mercader(self):
        self.juego.iniciar_dialogo(dialogo_mercader_acorralada(self.juego))
        return None   # no dice nada: empieza el diálogo

    def usar_cana(self):
        """Empieza la animación: la astronauta mira hacia el vacío y saca la caña. Los clics quedan bloqueados."""
        if self.t_rescate is not None:
            return None
        self.juego.inventario.quitar("cana_cebo")
        self.juego.inventario.agregar("cana")          # el cebo se pierde, pero la caña se la queda (se puede desarmar)
        personaje = self.juego.personaje
        personaje.detener()
        personaje.mirando_derecha = True
        self.t_rescate = 0.0
        self.hablo_cebo = False
        self.bloqueada = True
        return None   # la animación habla por ella

    # --- la caña, en función del tiempo ---

    def mano(self):
        p = self.juego.personaje
        return (int(p.x) + 5, int(p.y) - 14)

    @staticmethod
    def angulo_y_largo(t):
        """(ángulo en grados sobre la horizontal, largo) de la caña en el instante t."""
        if t < T_SACA:                                       # la saca: se despliega hacia arriba
            return 72, LARGO_CANA * _suave(t / T_SACA)
        if t < T_ESTIRA:                                     # la estira sobre el vacío
            return 72 - 80 * _suave((t - T_SACA) / (T_ESTIRA - T_SACA)), LARGO_CANA
        if t < 3.5:                                          # sostiene (un leve vaivén)
            return -8 + math.sin(t * 5) * 1.2, LARGO_CANA
        if t < 3.8:                                          # echa la caña atrás
            return -8 + 78 * _suave((t - 3.5) / 0.3), LARGO_CANA
        if t < T_SUELTA:                                     # y la revolea hacia adelante
            return 70 - 78 * _suave((t - 3.8) / 0.2), LARGO_CANA
        if t < 4.4:                                          # sigue de largo
            return -8 - 14 * _suave((t - T_SUELTA) / 0.4), LARGO_CANA
        if t < T_FIN:                                        # la guarda
            u = _suave((t - 4.4) / (T_FIN - 4.4))
            return -22 + 94 * u, LARGO_CANA * (1 - u)
        return 0, 0

    def punta(self, t):
        ang, largo = self.angulo_y_largo(t)
        mx, my = self.mano()
        return (mx + largo * math.cos(math.radians(ang)), my - largo * math.sin(math.radians(ang)))

    def largo_cuerda(self, t):
        if t < T_ESTIRA:
            return 3
        if t < T_BAJA:
            return 3 + 33 * _suave((t - T_ESTIRA) / (T_BAJA - T_ESTIRA))
        return 36

    def posicion_cebo(self, t):
        """El cebo colgando de la cuerda (se balancea) o, ya soltado, volando en arco hasta la arena."""
        if t >= T_SUELTA:
            x0, y0 = self._cebo_colgado(T_SUELTA)
            u = min(1.0, (t - T_SUELTA) / 0.55)
            return (x0 + (292 - x0) * u, y0 + (136 - y0) * u - 30 * math.sin(math.pi * u))
        return self._cebo_colgado(t)

    def _cebo_colgado(self, t):
        px, py = self.punta(t)
        s = self.largo_cuerda(t)
        balanceo = math.sin(t * 6.0) * 2.0 * _suave((t - T_ESTIRA) / 1.0) if t > T_ESTIRA else 0
        return (px + balanceo, py + s)

    def x_perro(self, t):
        if t < T_PERRO_SE_ACERCA:
            return RECT_PERRO.x
        if t < T_SUELTA + 0.05:
            u = _suave((t - T_PERRO_SE_ACERCA) / 1.0)
            return RECT_PERRO.x + (X_PERRO_CEBO - RECT_PERRO.x) * u
        return X_PERRO_CEBO + (t - T_SUELTA - 0.05) * 200          # corre detrás del cebo

    def actualizar(self, dt):
        """El rescate: la caña, el perro que corre detrás del cebo, la mercader que agradece y se va a su puesto."""
        if self.t_rescate is None:
            return
        progreso = self.juego.progreso
        if self.fase == "perro":
            self.t_rescate += dt
            t = self.t_rescate
            if t > 2.6 and not self.hablo_cebo:
                self.hablo_cebo = True
                self.juego.personaje.decir("Mirá qué rico, perrito...")
            if t > 4.6:
                self.bloqueada = False                                 # ya puede moverse
            if t > T_FIN:
                progreso["perro_ahuyentado"] = True
                self.juego.estados["JUGANDO"].poner_musica()              # se acabó el peligro: vuelve la música común
                self.fase = "huida"
                self.juego.iniciar_dialogo(dialogo_mercader_rescatada())
        elif self.fase == "huida":
            self.mercader_dx -= 105 * dt                               # corre hacia la izquierda (hacia el mercado), al revés que el perro
            if RECT_MERCADER.x + self.mercader_dx < -24:
                progreso["mercader_en_puesto"] = True
                self.fase = "listo"

    def dibujar_cana(self, sup, rect):
        """La caña (un palo largo con cuerda) que maneja la astronauta, y el cebo que cuelga o vuela."""
        t = self.t_rescate
        if t is None or t > T_FIN:
            return
        ang, largo = self.angulo_y_largo(t)
        mx, my = self.mano()
        tx, ty = self.punta(t)
        pygame.draw.line(sup, (30, 18, 12), (mx, my), (int(tx), int(ty)), 3)
        pygame.draw.line(sup, (150, 96, 54), (mx, my), (int(tx), int(ty)), 1)
        if largo < 4:
            return
        if t < T_SUELTA:                                             # la cuerda con el cebo colgando
            x, y = self.posicion_cebo(t)
            pygame.draw.line(sup, (236, 224, 190), (int(tx), int(ty)), (int(x) + 1, int(y)))
            self._dibujar_trozo(sup, int(x), int(y))
        else:
            self._dibujar_trozo_volando(sup, t)

    def _dibujar_trozo_volando(self, sup, t):
        x, y = self.posicion_cebo(t)
        if t - T_SUELTA <= 0.55 or self.x_perro(t) < x - 12:          # queda en la arena hasta que el perro llega
            self._dibujar_trozo(sup, int(x), int(y))

    @staticmethod
    def _dibujar_trozo(sup, x, y):
        pygame.draw.rect(sup, (30, 14, 20), (x - 1, y - 1, 5, 4))
        pygame.draw.rect(sup, (206, 82, 90), (x, y, 3, 2))
        sup.set_at((x, y), (250, 160, 160))

    def dibujar_mercader(self, sup, rect):
        """La mercader tiembla de miedo, pegada a la pared del barranco."""
        t = self.juego.tiempo
        nombre = "mercader_miedo_f4" if t % 2.6 < 0.2 else ("mercader_miedo_f0", "mercader_miedo_f1", "mercader_miedo_f2", "mercader_miedo_f3")[int((t % 1.2) / 0.3)]
        if self.fase == "huida":                                       # libre: sale corriendo hacia su puesto, saltando
            dx = int(self.mercader_dx)
            dy = -(int(t * 12) % 2)
            dibujar_objeto(sup, self.juego.sprites, nombre, rect.move(dx, dy))
            return
        temblor = (1, 0, -1, 0)[int(t * 14) % 4]
        dibujar_objeto(sup, self.juego.sprites, nombre, rect.move(temblor, 0))

    def dibujar_perro(self, sup, rect):
        """El perro gruñe; cuando le muestran el cebo se acerca, se calma y lo olfatea; y después sale corriendo."""
        t = self.juego.tiempo
        tr = self.t_rescate
        if tr is not None and tr >= T_SUELTA + 0.05:                   # corre detrás del cebo, hacia la derecha
            sprite = pygame.transform.flip(self.juego.sprites["perro_alien_f%d" % (int(t * 12) % 2)], True, False)
            x = int(self.x_perro(tr))
            if x < ANCHO:
                sup.blit(sprite, (x, rect.y - (int(t * 12) % 2)))
            return
        if tr is not None and tr >= T_PERRO_SE_ACERCA:                 # deja de gruñir y sigue el cebo con el hocico
            subida = int(math.sin(tr * 6.0) * 1.5)
            sup.blit(self.juego.sprites["perro_alien_f0"], (int(self.x_perro(tr)), rect.y + subida))
            return
        abierta = int(t * 2.8) % 2 == 0
        sprite = self.juego.sprites["perro_alien_f1" if abierta else "perro_alien_f0"]
        sup.blit(sprite, rect.move(0, 1 if abierta else 0).topleft)

    # ---------- Animación: olas y brillos ----------

    def dibujar_olas(self, sup, rect):
        """El mar se mueve: espuma que va y viene en la orilla y destellos sobre el agua."""
        t = self.juego.tiempo
        for x in range(X_BORDE + 14, ANCHO):
            y = int(_orilla(x) + 1.8 * math.sin(t * 1.1 + x / 17.0))
            if int(x / 3 + t * 2) % 5 != 0:                         # la espuma se corta en tramos
                sup.set_at((x, y), (236, 252, 240))
                if (x + int(t * 4)) % 3 == 0:
                    sup.set_at((x, y - 1), (170, 226, 200))
        for k in range(26):                                          # destellos
            x = X_BORDE + 18 + (k * 37 + int(t * 3 + k * 5)) % (ANCHO - X_BORDE - 20)
            y = Y_MAR + 3 + (k * 11) % 20
            if int(t * 2 + k) % 4 == 0:
                sup.set_at((x, y), (230, 255, 240))
                sup.set_at((x + 1, y), (150, 220, 190))

    # ---------- Fondo ----------

    def construir_fondo(self, sup):
        paisaje.cielo(sup)
        self._mar(sup)
        self._arena(sup)
        self._cornisa(sup)
        self._pared(sup)

    def _mar(self, sup):
        rampa = [(70, 176, 122), (48, 156, 114), (32, 130, 104), (22, 104, 92), (16, 82, 78)]
        for y in range(Y_MAR, ORILLA + 8):
            for x in range(ANCHO):
                f = (y - Y_MAR) / (ORILLA + 8 - Y_MAR)
                f += 0.05 * math.sin(x / 7.0 + y / 3.0)
                sup.set_at((x, y), _elegir(rampa, f, x, y))
        for x in range(ANCHO):                                       # línea de horizonte clara
            sup.set_at((x, Y_MAR), (186, 236, 206))
        for x in range(214, 246):                                    # una isla lejana
            alto = int(5 * math.sin((x - 214) / 32.0 * math.pi) ** 1.2)
            for y in range(Y_MAR - alto, Y_MAR):
                sup.set_at((x, y), (60, 44, 84) if (x + y) % 2 else (74, 54, 96))

    def _arena(self, sup):
        rampa = [(206, 170, 92), (226, 192, 112), (242, 214, 140), (250, 232, 170)]
        for x in range(ANCHO):
            o = int(_orilla(x))
            for y in range(o, ALTO_ESCENA):
                f = 1 - (y - o) / max(1, ALTO_ESCENA - o)
                f = f * 0.6 + 0.3 + 0.05 * math.sin(x / 5.0)
                c = _elegir(rampa, f, x, y)
                if y < o + 4:                                        # arena mojada, más oscura, cerca de la orilla
                    c = _elegir([(150, 122, 70), (176, 144, 82)], 0.5, x, y)
                sup.set_at((x, y), c)
        for k in range(120):                                         # granos y piedritas
            x = (k * 73 + 11) % ANCHO
            y = ORILLA + 8 + (k * 29) % (ALTO_ESCENA - ORILLA - 8)
            sup.set_at((x, y), (176, 140, 84) if k % 3 else (255, 244, 200))

    def _cornisa(self, sup):
        """La cima del barranco: la tierra donde se camina, con su borde delantero."""
        pts = [(0, Y_CIMA), (X_BORDE - 8, Y_CIMA), (X_BORDE - 2, Y_CIMA + 7), (X_BORDE, Y_BORDE), (0, Y_BORDE)]
        mascara = pygame.Surface((ANCHO, ALTO_ESCENA), pygame.SRCALPHA)
        pygame.draw.polygon(mascara, (255, 255, 255, 255), pts)
        rampa = [(186, 96, 58), (206, 116, 66), (224, 138, 78), (238, 160, 92)]
        for y in range(Y_CIMA, Y_BORDE + 1):
            for x in range(X_BORDE + 1):
                if mascara.get_at((x, y)).a:
                    f = (y - Y_CIMA) / (Y_BORDE - Y_CIMA)
                    sup.set_at((x, y), _elegir(rampa, f * 0.8 + 0.1 + 0.06 * math.sin(x / 11.0), x, y))
        for k in range(90):                                          # piedritas y matas secas de la cornisa
            x = (k * 53 + 7) % (X_BORDE - 6)
            y = Y_CIMA + 3 + (k * 17) % (Y_BORDE - Y_CIMA - 5)
            if mascara.get_at((x, y)).a:
                if k % 5 == 0:
                    pygame.draw.line(sup, (120, 60, 40), (x, y), (x, y - 2))
                    sup.set_at((x + 1, y - 2), (150, 80, 48))
                else:
                    sup.set_at((x, y), (136, 66, 44))
                    sup.set_at((x + 1, y), (248, 180, 110))
        pygame.draw.line(sup, (250, 186, 116), (0, Y_BORDE - 1), (X_BORDE - 1, Y_BORDE - 1))   # luz en el borde
        pygame.draw.line(sup, (70, 32, 30), (0, Y_BORDE), (X_BORDE, Y_BORDE))

    def _pared(self, sup):
        """La pared del barranco: capas de tierra de colores, grietas y sombra hacia el vacío."""
        colores = [(214, 120, 58), (170, 84, 46), (236, 156, 78), (132, 62, 44), (196, 104, 56)]
        borde_derecho = lambda y: X_BORDE + 4 * math.sin(y / 5.0) + (y - Y_BORDE) * 0.06    # noqa: E731
        for y in range(Y_BORDE + 1, Y_PIE):
            limite = int(borde_derecho(y))
            for x in range(0, limite + 1):
                capa = int((y + 3 * math.sin(x / 9.0) + 2 * math.sin(x / 4.3 + y / 20.0)) / 6)
                color = colores[capa % len(colores)]
                sombra = -0.05 - 0.4 * (x / max(1, limite)) ** 2
                if x < 10:
                    sombra += 0.08
                color = arte._tono(color, sombra)
                if paisaje._umbral(x, y) < 0.1:                      # puntitos de tierra más oscura
                    color = arte._tono(color, -0.25)
                sup.set_at((x, y), color)
            sup.set_at((limite, y), (60, 28, 28))                     # el contorno derecho de la pared
            sup.set_at((max(0, limite - 1), y), (96, 44, 36))
        for x0, y0, largo in ((20, 124, 18), (48, 130, 22), (80, 122, 26), (36, 142, 14), (96, 138, 12)):   # grietas
            for k in range(largo):
                sup.set_at((x0 + int(2 * math.sin(k / 3.0)), y0 + k), (70, 34, 30))
        for x in range(0, X_BORDE + 6):                               # el pie del barranco: línea oscura y sombra tramada sobre la arena
            sup.set_at((x, Y_PIE), (70, 36, 30))
            for dy in (1, 2, 3):
                if paisaje._umbral(x, Y_PIE + dy) < 0.5 - dy * 0.12:
                    sup.set_at((x, Y_PIE + dy), (150, 110, 70))
        for k in range(10):                                           # derrumbe al pie del barranco
            x = 134 + (k * 11) % 16
            y = 143 + (k * 5) % 7
            paisaje.roca(sup, x, y - 4, 4 + k % 3, 3)
