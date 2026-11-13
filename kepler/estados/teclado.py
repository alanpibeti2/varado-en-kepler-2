"""
kepler/estados/teclado.py
Estado TECLADO: el tablero de la compuerta, encima del juego.

Las teclas no tienen números sino SÍMBOLOS alienígenas (ver glifos.py), en un orden que no sigue
los números. Hay que teclear el código a mano, con el mouse, buscando los símbolos que dijo R-7.
Retroceso borra, Enter acepta y Esc cierra. Si el código es correcto, se ejecuta la acción que
pidió el tablero (abrir la compuerta); si no, el tablero se sacude y se borra.
"""

import math

import pygame

from engine import Estado, Boton, texto, panel, oscurecer
from kepler.config import BLANCO, GRIS, COLORES_BOTON, UI_FONDO, UI_LUZ, UI_SOMBRA, UI_HUNDIDO
from kepler.glifos import imagen_glifo

VERDE = (110, 240, 140)
ROJO = (240, 90, 90)
CIAN = (110, 230, 245)

# Qué ocupa cada casilla del tablero, de izquierda a derecha y de arriba abajo:
# un número (que se ve como símbolo) o una acción. Los números están mezclados a propósito.
DISPOSICION = [7, 2, 9,
               0, 5, 1,
               8, 3, 6,
               "Borrar", 4, "OK"]


class EstadoTeclado(Estado):
    PANEL = pygame.Rect(101, 14, 118, 172)      # centrado en la pantalla (320 de ancho)
    TAM_TECLA = (32, 18)
    SEP = 4

    def __init__(self, juego):
        super().__init__(juego)
        self.codigo = ""
        self.titulo = ""
        self.al_acertar = None
        self.digitos = ""
        self.resultado = None          # None, "ok" o "error"
        self.espera = 0.0              # cuánto se queda el mensaje de resultado en pantalla
        self.tiempo = 0.0

        fuente = juego.fuentes["normal"]
        ancho, alto = self.TAM_TECLA
        x0 = self.PANEL.centerx - (3 * ancho + 2 * self.SEP) // 2
        y0 = self.PANEL.y + 60
        self.botones = []
        for i, casilla in enumerate(DISPOSICION):
            fila, col = divmod(i, 3)
            rect = (x0 + col * (ancho + self.SEP), y0 + fila * (alto + self.SEP), ancho, alto)
            etiqueta = casilla if isinstance(casilla, str) else ""          # los números se dibujan como símbolo
            clave = casilla if isinstance(casilla, str) else str(casilla)
            self.botones.append(Boton(rect, etiqueta, lambda c=clave: self._tecla(c), juego.fuentes["chica"], COLORES_BOTON))
        self.boton_cerrar = Boton((self.PANEL.centerx - 22, self.PANEL.y + 150, 44, 14), "Cerrar", self.cerrar,
                                  juego.fuentes["chica"], COLORES_BOTON)

    # ---------- Entrada ----------

    def empezar(self, codigo, al_acertar, titulo="TABLERO"):
        """Prepara el tablero: 'codigo' son los dígitos que hay que teclear y 'al_acertar' lo que pasa si se acierta."""
        self.codigo = codigo
        self.al_acertar = al_acertar
        self.titulo = titulo
        self.digitos = ""
        self.resultado = None
        self.espera = 0.0

    def entrar(self):
        self.tiempo = 0.0

    def cerrar(self):
        self.juego.cambiar_estado("JUGANDO")

    def _tecla(self, clave):
        if self.resultado is not None:         # mientras muestra "correcto/incorrecto" no recibe nada
            return
        if clave == "Borrar":
            self.digitos = self.digitos[:-1]
        elif clave == "OK":
            self._aceptar()
        elif len(self.digitos) < len(self.codigo):
            self.digitos += clave

    def _aceptar(self):
        if len(self.digitos) < len(self.codigo):
            return                              # todavía faltan símbolos
        self.resultado = "ok" if self.digitos == self.codigo else "error"
        self.espera = 0.9

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_ESCAPE:
                self.cerrar()
            elif evento.key == pygame.K_BACKSPACE:
                self._tecla("Borrar")
            elif evento.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._tecla("OK")
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 3:
                self.cerrar()
            elif evento.button == 1:
                if self.boton_cerrar.manejar_evento(evento):
                    return
                for boton in self.botones:
                    if boton.manejar_evento(evento):
                        return

    # ---------- Lógica ----------

    def actualizar(self, dt):
        self.tiempo += dt
        self._habilitar_botones()
        if self.resultado is None:
            return
        self.espera -= dt
        if self.espera > 0:
            return
        if self.resultado == "ok":
            accion = self.al_acertar
            self.cerrar()
            if accion:
                accion()
        else:                                   # incorrecto: se borra y se puede volver a probar
            self.digitos = ""
            self.resultado = None
            self._habilitar_botones()

    def _habilitar_botones(self):
        """Mientras muestra "correcto" o "incorrecto", las teclas no responden."""
        for boton in self.botones:
            boton.habilitado = self.resultado is None

    # ---------- Dibujo ----------

    def dibujar(self, sup):
        fuentes = self.juego.fuentes
        self.juego.estados["JUGANDO"].dibujar(sup)
        oscurecer(sup, 150)

        # Si se equivocó, el tablero tiembla un instante
        temblor = 0
        if self.resultado == "error":
            temblor = round(3 * math.sin(self.tiempo * 60) * max(0.0, self.espera / 0.9))
        marco = self.PANEL.move(temblor, 0)
        panel(sup, marco, UI_FONDO, UI_LUZ, UI_SOMBRA)
        texto(sup, self.titulo, fuentes["normal"], CIAN, (marco.centerx, marco.y + 10), ancla="center")
        self.boton_cerrar.rect.topleft = (marco.centerx - 22, marco.y + 150)
        self.boton_cerrar.dibujar(sup)

        # Pantallita con los símbolos tecleados (rayitas donde faltan)
        pantalla = pygame.Rect(marco.x + 10, marco.y + 20, marco.w - 20, 26)
        panel(sup, pantalla, UI_HUNDIDO, UI_SOMBRA, UI_LUZ)
        color = {None: CIAN, "ok": VERDE, "error": ROJO}[self.resultado]
        ancho_celda = pantalla.w // len(self.codigo)
        for i in range(len(self.codigo)):
            centro = (pantalla.x + ancho_celda * i + ancho_celda // 2, pantalla.centery)
            if i < len(self.digitos):
                imagen = imagen_glifo(self.digitos[i], color, 3)
                sup.blit(imagen, imagen.get_rect(center=centro))
            else:
                pygame.draw.line(sup, GRIS, (centro[0] - 6, centro[1] + 9), (centro[0] + 6, centro[1] + 9), 2)
        mensaje = {None: "Ingresá el código", "ok": "ACCESO CONCEDIDO", "error": "CÓDIGO INCORRECTO"}[self.resultado]
        texto(sup, mensaje, fuentes["chica"], color if self.resultado else BLANCO,
              (marco.centerx, pantalla.bottom + 8), ancla="center")

        # Las teclas se mueven junto con el tablero cuando tiembla
        ancho, alto = self.TAM_TECLA
        x0 = marco.centerx - (3 * ancho + 2 * self.SEP) // 2
        y0 = marco.y + 60
        for i, (boton, casilla) in enumerate(zip(self.botones, DISPOSICION)):
            fila, col = divmod(i, 3)
            boton.rect.topleft = (x0 + col * (ancho + self.SEP), y0 + fila * (alto + self.SEP))
            boton.dibujar(sup)
            if not isinstance(casilla, str):                # una tecla de símbolo: se dibuja encima del botón
                encima = boton.habilitado and boton.rect.collidepoint(pygame.mouse.get_pos())
                tinta = (255, 220, 110) if encima else (235, 230, 255)
                if not boton.habilitado:
                    tinta = (110, 100, 140)
                imagen = imagen_glifo(casilla, tinta, 2)
                sup.blit(imagen, imagen.get_rect(center=boton.rect.center))
