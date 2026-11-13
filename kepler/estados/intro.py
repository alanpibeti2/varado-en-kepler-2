"""
kepler/estados/intro.py
Estado INTRO: la nave (un transbordador) de la astronauta cae envuelta en fuego y se estrella
en Kepler-7. Se ve sobre el mismo fondo del sitio del choque, con barras negras
de cine arriba y abajo. Un clic o una tecla la saltan.

Todo se calcula a partir del tiempo 't' (sin guardar partículas), así que
basta con dibujar la animación en el instante que corresponde.

El fuego, el humo y los destellos se dibujan al estilo de 16 bits: colores en escalones (sin
degradados suaves ni transparencias) y los bordes se deshacen con trama de puntitos (dithering).
"""

import math
import random

import pygame

from engine import Estado, texto
from kepler import arte16
from kepler.config import ANCHO, ALTO, ALTO_ESCENA, BLANCO, GRIS
from kepler.sprites import dibujar_objeto

CAIDA = 3.4          # segundos hasta el impacto
VOLUMEN_CHOQUE = 0.65    # volumen de la frenada y el choque (1.0 = el del archivo)
GOLPE_EN_AUDIO = 3.2    # en qué segundo del audio "intro_choque" ocurre el golpe (se ajustó a oído:
                         # si el choque suena tarde, subí este número; si suena temprano, bajalo)
DURACION = 7.4       # segundos hasta que empieza el juego
INICIO = (440, 44)   # de dónde entra la nave (a la derecha, fuera de pantalla, casi a la altura del choque)
IMPACTO = (129, 70)  # dónde está el centro de la nave al estrellarse (la nariz queda clavada más a la izquierda)
NARIZ = (16, 106)    # dónde queda clavada la nariz (de acá salen las chispas y el polvo)
BARRA = (ALTO - ALTO_ESCENA) // 2     # alto de cada barra negra
RECT_NAVE = pygame.Rect(*arte16.RECT_NAVE)   # igual que la nave estrellada del escenario

BAYER = ((0, 8, 2, 10), (12, 4, 14, 6), (3, 11, 1, 9), (15, 7, 13, 5))
FUEGO = [(255, 252, 222), (255, 232, 132), (255, 184, 64), (244, 120, 40), (196, 64, 40), (120, 44, 56), (66, 52, 72)]
_VELOS = {}


def velo(color, nivel, tam):
    """
    Una capa de puntitos 'color' que cubre 'nivel' dieciseisavos de la superficie (0 = nada, 16 = todo),
    repartidos en la trama de 4x4 de siempre. Reemplaza a las transparencias: así los fundidos y destellos
    también se hacen con píxeles enteros.
    """
    clave = (color, nivel, tam)
    if clave not in _VELOS:
        parche = pygame.Surface((4, 4), pygame.SRCALPHA)
        for y in range(4):
            for x in range(4):
                if BAYER[y][x] < nivel:
                    parche.set_at((x, y), color)
        capa = pygame.Surface(tam, pygame.SRCALPHA)
        for y in range(0, tam[1], 4):
            for x in range(0, tam[0], 4):
                capa.blit(parche, (x, y))
        _VELOS[clave] = capa
    return _VELOS[clave]


disco_tramado = arte16.disco_tramado


def _umbral_local(x, y):
    """El umbral de la trama de puntitos de 4x4 (0 a 1)."""
    return (BAYER[y % 4][x % 4] + 0.5) / 16


class EstadoIntro(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        self.t = 0.0
        self.sono = False
        self.azar = random.Random(4)
        self.escena = pygame.Surface((ANCHO, ALTO_ESCENA))
        self.nave = self._crear_nave()
        # Ángulos y retrasos fijos para las chispas y el humo del impacto
        azar = random.Random(7)
        self.chispas = [(azar.uniform(math.pi, 2 * math.pi), azar.uniform(40, 90)) for _ in range(16)]
        self.humo = [(azar.uniform(-14, 14), azar.uniform(0.0, 1.2)) for _ in range(12)]

    @staticmethod
    def _crear_nave():
        """El transbordador, mirando hacia la IZQUIERDA (porque cae yendo hacia la izquierda)."""
        return pygame.transform.flip(arte16.transbordador_vuelo(), True, False)

    # ---------- Control ----------

    def entrar(self):
        self.t = 0.0
        self.sono = False

    def salir(self):
        self.juego.sonidos.detener_efectos()     # por si se salta la intro con el sonido a medias

    def manejar_evento(self, evento):
        # Un clic o tecla saltan la intro (pasada media seg., para no saltarla sin querer)
        if self.t > 0.5 and evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self._empezar_juego()

    def actualizar(self, dt):
        self.t += dt
        # El audio de frenada y choque tiene el golpe a los GOLPE_EN_AUDIO segundos: arranca antes
        # para que el golpe caiga justo en el impacto de la nave.
        if not self.sono and self.t >= CAIDA - GOLPE_EN_AUDIO:
            self.sono = True
            self.juego.sonidos.reproducir("intro_choque", volumen=VOLUMEN_CHOQUE)
        if self.t >= DURACION:
            self._empezar_juego()

    def _empezar_juego(self):
        self.juego.cambiar_estado("JUGANDO")

    # ---------- Recorrido de la nave ----------

    @staticmethod
    def _posicion(t):
        """Va de INICIO a IMPACTO acelerando (cae cada vez más rápido)."""
        p = max(0.0, min(1.0, t / CAIDA))
        e = 1 - (1 - p) ** 2            # entra rápido y se va frenando (el paracaídas hace de freno)
        return (INICIO[0] + (IMPACTO[0] - INICIO[0]) * e,
                INICIO[1] + (IMPACTO[1] - INICIO[1]) * e)

    # ---------- Dibujo ----------

    def dibujar(self, sup):
        t = self.t
        esc = self.escena
        esc.blit(self.juego.escenas["choque"].fondo, (0, 0))
        impacto = t - CAIDA        # segundos desde el impacto (negativo = todavía cae)

        if impacto < 0:
            self._dibujar_caida(esc, t)
        else:
            self._dibujar_choque(esc, impacto)

        # Temblor de pantalla justo después del impacto
        ox = oy = 0
        if 0 <= impacto < 0.7:
            fuerza = 3 * (1 - impacto / 0.7)
            ox, oy = self.azar.uniform(-fuerza, fuerza), self.azar.uniform(-fuerza, fuerza)
        sup.fill((0, 0, 0))
        sup.blit(esc, (int(ox), BARRA + int(oy)))

        # Textos en las barras negras
        fuentes = self.juego.fuentes
        if impacto < 0 and int(t * 4) % 2 == 0:
            texto(sup, "¡ALERTA! IMPACTO INMINENTE", fuentes["normal"], (255, 90, 90),
                  (ANCHO // 2, BARRA // 2), ancla="center")
        if impacto > 1.2:
            texto(sup, "Kepler-7. Sin señal de rescate.", fuentes["normal"], BLANCO,
                  (ANCHO // 2, ALTO - BARRA // 2), ancla="center")
        texto(sup, "clic para saltar", fuentes["chica"], GRIS, (ANCHO - 4, ALTO - 3), ancla="bottomright")

        # Fundido a negro al final, con trama (8 escalones)
        if t > DURACION - 1.0:
            nivel = min(16, int(17 * (t - (DURACION - 1.0))))
            sup.blit(velo((0, 0, 0), nivel, (ANCHO, ALTO)), (0, 0))

    def _dibujar_caida(self, esc, t):
        p = t / CAIDA
        escala = 1.25                                  # tamaño constante: cruza la pantalla de costado, no viene de frente
        x, y = self._posicion(t)

        # La nave planea casi horizontal: baja el morro de a poco hasta el ángulo con el que queda clavada
        angulo = 3 + 12 * p ** 2 + math.sin(t * 9) * 1.0
        rad = math.radians(angulo)
        ux, uy = -math.cos(rad), math.sin(rad)         # hacia dónde apunta la nariz (izquierda y un poco abajo)
        px_, py_ = -uy, ux                             # "arriba" del transbordador (perpendicular al avance)
        tam = (max(1, round(self.nave.get_width() * escala)), max(1, round(self.nave.get_height() * escala)))
        largo = 160 * escala                           # largo del fuselaje en pantalla
        # El eje del fuselaje queda 14 px (sin escalar) arriba del centro de la imagen (por la aleta de la cola)
        ex, ey = x + px_ * 14 * escala, y + py_ * 14 * escala
        nariz = (ex + ux * 85 * escala, ey + uy * 85 * escala)       # la punta exacta de la nariz

        self._dibujar_paracaidas(esc, t, p, escala, (x, y), (ux, uy), largo)

        # El fuego va por DETRÁS de la nave, rodeándola: así se ve entera la silueta, con la nariz puntiaguda
        self._plasma(esc, t, escala, nariz, (ux, uy), (px_, py_), p, angulo)

        # La nave, girada sin suavizar (píxeles enteros)
        nave = pygame.transform.rotate(pygame.transform.scale(self.nave, tam), angulo)
        esc.blit(nave, nave.get_rect(center=(int(x), int(y))))

    @staticmethod
    def _plasma(esc, t, escala, nariz, u, perp, p, angulo=0.0):
        """
        La nariz recibe todo el calor de la fricción: una capa incandescente pegada al morro, una onda de choque azul
        y blanca por delante y llamas que se echan hacia atrás por arriba y por abajo del casco, cada vez más finas y
        rojas (no hay estela detrás de la cola).

        Las llamas se pintan RELLENAS (no como hilos): cada punto tiene un "calor" que baja con la distancia a la nariz
        y al casco, y se elige el color de una rampa (blanco, amarillo, naranja, rojo, rojo oscuro) con trama de puntitos
        entre un color y el siguiente. Los bordes tiemblan con ondas que cambian en el tiempo. Se dibujan en una imagen
        propia, con la nariz a la izquierda, y después se gira igual que la nave.
        """
        medio = 14.5 * escala                                         # medio alto del fuselaje
        largo_llama = 150 * escala
        ancho_max = 17 * escala
        margen = int(24 * escala)                                     # lugar para la capa del morro (adelante de la nariz)
        W = int(largo_llama) + margen + 8
        H = int(2 * (medio + ancho_max + 8))
        capa = pygame.Surface((W, H), pygame.SRCALPHA)
        cx, cy = margen, H // 2                                       # la nariz, dentro de la imagen
        ramp = FUEGO[:6]

        def pinta(x, y, calor):
            """Pone un punto de la rampa según el calor (1 = blanco, 0 = rojo oscuro); con trama entre colores."""
            if calor <= 0.04:
                return
            pos = (1 - min(1.0, calor)) * (len(ramp) - 1)
            i = int(pos)
            idx = i + 1 if (pos - i) > _umbral_local(x, y) and i + 1 < len(ramp) else i
            capa.set_at((x, y), ramp[idx])

        # 1) Capa incandescente delante del morro: un óvalo que se enciende y titila
        for x in range(0, margen + 6):
            for y in range(cy - int(medio * 1.1), cy + int(medio * 1.1) + 1):
                rx = (x - (margen - 2)) / (margen * 0.95)
                ry = (y - cy) / (medio * 1.05)
                r = math.hypot(rx, ry)
                if r < 1.0:
                    ruido = 0.12 * math.sin(y * 0.9 + t * 30) + 0.08 * math.sin(x * 0.7 - t * 22)
                    pinta(x, y, 1.05 - 0.85 * r + ruido)
        # 2) Llamas hacia atrás por los dos costados
        for lado in (1, -1):
            for sx in range(0, int(largo_llama)):
                f = sx / largo_llama
                lengueta = (math.sin(sx * 0.23 - t * 21 + lado * 1.3) * 0.5 + math.sin(sx * 0.51 - t * 33 + lado) * 0.3
                            + math.sin(sx * 0.09 - t * 9) * 0.4)
                grosor = ancho_max * (f ** 0.28) * (1 - f) ** 0.8 * (1.0 + 0.45 * lengueta)
                base = medio * 0.97
                # Se pinta desde el eje del fuselaje hacia afuera: lo que queda debajo del casco lo tapa la nave, y donde
                # el casco se afina (la nariz) la llama queda pegada, sin huecos
                for d in range(0, int(base + grosor) + 1):
                    g = max(0.0, d - base) / max(1.0, grosor)
                    calor = 1.08 - 0.74 * f - 0.62 * g + 0.1 * lengueta
                    y = cy - lado * d
                    if 0 <= y < H:
                        pinta(margen + sx, y, calor)
        # Se gira como la nave y se pega con la nariz en su lugar
        rot = pygame.transform.rotate(capa, angulo)
        rad = math.radians(angulo)
        vx, vy = cx - W / 2, cy - H / 2                               # de la mitad de la imagen a la nariz
        wx, wy = vx * math.cos(rad) + vy * math.sin(rad), -vx * math.sin(rad) + vy * math.cos(rad)
        esc.blit(rot, rot.get_rect(center=(int(nariz[0] - wx), int(nariz[1] - wy))))

        # 3) La onda de choque: arcos azules y blancos por delante de la nariz, que se abren hacia los costados
        for k, color in enumerate(((236, 244, 255), (130, 176, 255), (66, 86, 226))):
            d = (7 + 5 * k) * escala
            for grado in range(-84, 85, 3):
                th = math.radians(grado)
                if (grado // 3 + k) % 4 == 0 and k > 0:                 # los arcos de afuera, entrecortados
                    continue
                fx = u[0] * (d * math.cos(th) + 2 * escala) + perp[0] * (medio * 1.5 * math.sin(th))
                fy = u[1] * (d * math.cos(th) + 2 * escala) + perp[1] * (medio * 1.5 * math.sin(th))
                px, py = int(nariz[0] + fx), int(nariz[1] + fy)
                pygame.draw.rect(esc, color, (px, py, 2, 2))
        # 4) Algunas brasas que salen disparadas hacia atrás
        for k in range(10):
            tt = (t * 3 + k * 0.37) % 1.0
            lado = 1 if k % 2 else -1
            dist = (30 + 70 * tt) * escala
            lateral = lado * (medio * 1.1 + 6 * tt * escala)
            esc.set_at((int(nariz[0] - u[0] * dist + perp[0] * lateral), int(nariz[1] - u[1] * dist + perp[1] * lateral)),
                       FUEGO[1] if tt < 0.4 else FUEGO[3])

    @staticmethod
    def _dibujar_paracaidas(esc, t, p, escala, centro, u, largo):
        """
        Un paracaídas naranja y blanco atado a la cola. El viento lo arrastra hacia ATRÁS: queda tirante detrás de
        la nave, más arriba y con el domo inflado en contra del avance. Aletea un poco. Antes del choque se corta
        y se va para atrás y hacia abajo.
        """
        suelto = max(0.0, (p - 0.88) / 0.1)
        if p < 0.4 or suelto >= 1.0:
            return
        apertura = min(1.0, (p - 0.4) / 0.12)                        # se va abriendo
        ancho = max(4, int((34 * apertura + 6) * escala))
        alto = max(3, int((13 * apertura + 4) * escala))
        cola = (centro[0] - u[0] * largo * 0.46, centro[1] - u[1] * largo * 0.46 - 3 * escala)
        # Dirección en la que lo estira el viento: hacia atrás y un poco arriba, con un temblor
        aleteo = math.sin(t * 5.0) * 0.12
        dx, dy = -u[0], -u[1] - 0.5 + aleteo
        norma = math.hypot(dx, dy)
        dx, dy = dx / norma, dy / norma
        dist = (16 + 10 * apertura) * escala
        bx = cola[0] + dx * dist + suelto * 60 * escala
        by = cola[1] + dy * dist + suelto * 26 * escala
        fi = math.atan2(-dx, -dy)                                     # cuánto se gira el domo (la punta mira contra el avance)
        co, si = math.cos(fi), math.sin(fi)

        def girar(px, py):                                            # gira un punto local (domo derecho) y lo lleva a pantalla
            return (bx + px * co + py * si, by - px * si + py * co)

        medio = ancho / 2
        if suelto == 0:                                               # cuerdas tirantes del borde del domo a la cola
            for k in range(5):
                ex, ey = girar(-medio + ancho * k / 4, 0)
                pygame.draw.line(esc, (216, 208, 196), (int(ex), int(ey)), (int(cola[0]), int(cola[1])))
        # Domo derecho en una superficie aparte (gajos naranjas y blancos, sombra a la derecha) y se rota sin suavizar
        lado = ancho + 4
        capa = pygame.Surface((lado, alto + 4), pygame.SRCALPHA)
        for ddx in range(-int(medio), int(medio) + 1):
            f = ddx / medio if medio else 0
            h = int(alto * math.sqrt(max(0.0, 1 - f * f)))
            if h <= 0:
                continue
            gajo = int((ddx + medio) / max(1, ancho / 6))
            color = (250, 140, 48) if gajo % 2 == 0 else (244, 236, 220)
            if f > 0.45:
                color = (196, 96, 40) if gajo % 2 == 0 else (184, 176, 170)
            xx = lado // 2 + ddx
            pygame.draw.line(capa, color, (xx, alto + 2 - h), (xx, alto + 2))
            capa.set_at((xx, alto + 2 - h), (60, 36, 40))
        pygame.draw.line(capa, (60, 36, 40), (lado // 2 - int(medio), alto + 2), (lado // 2 + int(medio), alto + 2))
        capa = pygame.transform.rotate(capa, math.degrees(fi))
        # El centro de la base del domo está en (lado/2, alto+2) de la capa original: se lo reubica tras rotar
        cx0, cy0 = lado / 2, alto + 2
        ox, oy = cx0 - lado / 2, cy0 - (alto + 4) / 2                  # base respecto del centro de la capa
        rx, ry = ox * co + oy * si, -ox * si + oy * co                  # el mismo vector, ya rotado
        esc.blit(capa, capa.get_rect(center=(int(bx - rx), int(by - ry))))

    def _dibujar_choque(self, esc, impacto):
        # Cráter y nave estrellada
        pygame.draw.ellipse(esc, (110, 44, 36), (RECT_NAVE.x + 4, RECT_NAVE.bottom - 10, RECT_NAVE.w - 8, 14))
        dibujar_objeto(esc, self.juego.sprites, "capsula", RECT_NAVE)
        if impacto > 0.4:                                   # el humo de la nave, igual que después en el juego
            arte16.humo_animado(esc, *arte16.ORIGEN_HUMO_NAVE, self.t, bolas=10, altura=30, escala=1.5)

        # Chispas que salen disparadas
        if impacto < 1.0:
            for angulo, velocidad in self.chispas:
                x = NARIZ[0] + math.cos(angulo) * velocidad * impacto
                y = NARIZ[1] + math.sin(angulo) * velocidad * impacto + 120 * impacto ** 2
                color = FUEGO[0] if impacto < 0.35 else FUEGO[1] if impacto < 0.6 else FUEGO[3]
                esc.set_at((int(x), int(y)), color)
                esc.set_at((int(x) + 1, int(y)), color)

        # Humo que sube y se va deshaciendo en puntitos (sin transparencias)
        for desvio, retraso in self.humo:
            edad = impacto - retraso
            if edad <= 0:
                continue
            x = int(NARIZ[0] + 10 + desvio + math.sin(edad * 2 + desvio) * 4)
            y = int(NARIZ[1] - 6 - edad * 14)
            radio = int(3 + edad * 3.5)
            disco_tramado(esc, x, y, radio, (86, 78, 96), hueco=min(0.95, edad * 0.22))
            disco_tramado(esc, x - 1, y - 1, max(1, radio - 2), (150, 140, 158), hueco=min(0.98, 0.3 + edad * 0.3))

        # Destello del golpe: blanco pleno un instante y después se apaga por escalones, con trama
        if impacto < 0.06:
            esc.fill((255, 255, 255))
        elif impacto < 0.35:
            nivel = int(14 * (1 - (impacto - 0.06) / 0.29))
            esc.blit(velo((255, 255, 255), nivel, (ANCHO, ALTO_ESCENA)), (0, 0))
