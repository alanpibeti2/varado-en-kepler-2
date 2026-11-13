"""
kepler/estados/dialogo.py
Estado DIALOGO: muestra una conversación del engine (Dialogo) y deja
elegir opciones con el mouse (o con las teclas 1, 2, 3...).
"""

import pygame

from engine import Estado, texto, panel, envolver_texto, oscurecer
from kepler.config import ANCHO, ALTO, BLANCO, AMARILLO, CIAN, GRIS, UI_FONDO, UI_LUZ, UI_SOMBRA


class EstadoDialogo(Estado):
    MARGEN = 6           # separación del panel con los bordes de la pantalla
    ALTO_OPCION = 12

    def __init__(self, juego):
        super().__init__(juego)
        self.dialogo = None
        self._nodo_sonado = None
        self._voz_actual = None

    def empezar(self, dialogo):
        self.dialogo = dialogo
        self._nodo_sonado = None      # el último nodo que ya se tuvo en cuenta para la voz
        self._voz_actual = None       # la voz que está sonando ahora

    @staticmethod
    def _nombre_voz(hablante):
        """'Minero' -> 'voz_minero'; 'R-7' -> 'voz_r_7' (letras y números, el resto pasa a '_')."""
        limpio = "".join(c if c.isalnum() else "_" for c in hablante.lower())
        return "voz_" + limpio

    def actualizar(self, dt):
        # La voz del personaje suena en bucle mientras dura la charla (si hay un archivo para ella).
        # Sigue de corrido entre una línea y otra; solo cambia si empieza a hablar otro personaje.
        nodo = self.dialogo.actual
        if nodo is not self._nodo_sonado:
            self._nodo_sonado = nodo
            voz = self._nombre_voz(nodo.hablante)
            if voz != self._voz_actual:
                self.juego.sonidos.detener_efectos()
                self._voz_actual = voz
                self.juego.sonidos.reproducir(voz, bucle=True)

    def salir(self):
        self.juego.sonidos.detener_efectos()     # que la voz pare cuando termina la charla
        self._voz_actual = None

    # ---------- Distribución en pantalla ----------

    def _distribucion(self):
        """
        Calcula el panel, las líneas del texto y el rectángulo de cada opción.
        El panel mide lo justo para su contenido y queda pegado abajo,
        así se sigue viendo el escenario.
        """
        fuente = self.juego.fuentes["normal"]
        alto_linea = fuente.get_height()
        ancho = ANCHO - 2 * self.MARGEN
        lineas = envolver_texto(self.dialogo.actual.texto, fuente, ancho - 16)
        opciones = self.dialogo.opciones_disponibles()

        alto = 20 + len(lineas) * alto_linea + 6 + 8
        alto += len(opciones) * self.ALTO_OPCION if opciones else 10   # 10 = lugar para "(clic para seguir)"
        caja = pygame.Rect(self.MARGEN, ALTO - self.MARGEN - alto, ancho, alto)

        y = caja.y + 20 + len(lineas) * alto_linea + 6
        rects = []
        for opcion in opciones:
            rects.append((opcion, pygame.Rect(caja.x + 8, y, caja.w - 16, self.ALTO_OPCION)))
            y += self.ALTO_OPCION
        return caja, lineas, rects

    # ---------- Eventos ----------

    def manejar_evento(self, evento):
        _, _, rects = self._distribucion()
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
            if not rects:                       # nodo sin opciones: un clic sigue
                self.dialogo.continuar()
            for opcion, rect in rects:
                if rect.collidepoint(evento.pos):
                    self.dialogo.elegir(opcion)
                    break
            self._revisar_fin()
        elif evento.type == pygame.KEYDOWN:
            numero = evento.key - pygame.K_1     # tecla 1 -> 0, tecla 2 -> 1...
            if not rects and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.dialogo.continuar()
            elif 0 <= numero < len(rects):
                self.dialogo.elegir(rects[numero][0])
            self._revisar_fin()

    def _revisar_fin(self):
        # Si la charla terminó, volvemos al juego... salvo que una opción
        # ya nos haya mandado a otro estado (ej: la consola lanza el FINAL).
        if self.dialogo.terminado and self.juego.nombre_estado == "DIALOGO":
            self.juego.cambiar_estado("JUGANDO")

    # ---------- Dibujo ----------

    def dibujar(self, sup):
        fuentes = self.juego.fuentes
        self.juego.estados["JUGANDO"].dibujar(sup)
        oscurecer(sup, 90)

        caja, lineas, rects = self._distribucion()
        panel(sup, caja, UI_FONDO, UI_LUZ, UI_SOMBRA)
        texto(sup, self.dialogo.actual.hablante, fuentes["normal"], CIAN, (caja.x + 8, caja.y + 6))
        alto = fuentes["normal"].get_height()
        for i, linea in enumerate(lineas):
            texto(sup, linea, fuentes["normal"], BLANCO, (caja.x + 8, caja.y + 20 + i * alto))

        mouse = pygame.mouse.get_pos()
        for i, (opcion, rect) in enumerate(rects):
            encima = rect.collidepoint(mouse)
            color = AMARILLO if encima else (200, 190, 230)
            marca = ">" if encima else " "
            texto(sup, f"{marca} {i + 1}. {opcion.texto}", fuentes["normal"], color, rect.topleft)

        if not rects:
            texto(sup, "(clic para seguir)", fuentes["chica"], GRIS,
                  (caja.right - 8, caja.bottom - 5), ancla="bottomright")
