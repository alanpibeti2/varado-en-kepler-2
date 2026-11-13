"""
engine/actor.py
Un Actor es un personaje que puede CAMINAR por la zona caminable y HABLAR.

Tiene su propia mini máquina de estados:
    QUIETO  <-->  CAMINANDO

El motor resuelve el movimiento; CÓMO se ve el personaje lo decide el
juego, creando una subclase que implementa dibujar().
"""

import math

from engine.ui import envolver_texto, texto


class Actor:
    QUIETO = "QUIETO"
    CAMINANDO = "CAMINANDO"

    def __init__(self, x, y, velocidad=70, color_texto=(255, 230, 130)):
        # (x, y) es la posición de los PIES: es lo que importa para saber
        # si está parado dentro de la zona caminable.
        self.x = float(x)
        self.y = float(y)
        self.velocidad = velocidad      # píxeles por segundo
        self.estado = Actor.QUIETO
        self.destino = None
        self.al_llegar = None           # función a ejecutar al llegar al destino
        self.mirando_derecha = True
        self.tiempo_animacion = 0.0     # avanza mientras camina (para alternar cuadros)
        self.texto = ""                 # lo que está diciendo
        self.tiempo_texto = 0.0
        self.color_texto = color_texto

    # ---------- Órdenes ----------

    def ir_a(self, destino, al_llegar=None):
        """
        Empieza a caminar hacia 'destino'.
        'al_llegar' es una función que se ejecuta SOLO cuando llega
        (por ejemplo: agarrar el objeto). Así el personaje primero camina
        y después actúa, como en todas las aventuras gráficas.
        """
        self.destino = destino
        self.al_llegar = al_llegar
        self.estado = Actor.CAMINANDO

    def detener(self):
        self.estado = Actor.QUIETO
        self.destino = None
        self.al_llegar = None
        self.tiempo_animacion = 0.0

    def decir(self, contenido):
        """Muestra un texto sobre la cabeza. Dura más cuanto más largo es."""
        self.texto = contenido
        self.tiempo_texto = 1.5 + len(contenido) * 0.05

    @property
    def caminando(self):
        return self.estado == Actor.CAMINANDO

    # ---------- Lógica ----------

    def actualizar(self, dt, escena):
        if self.tiempo_texto > 0:
            self.tiempo_texto -= dt
            if self.tiempo_texto <= 0:
                self.texto = ""

        if self.estado == Actor.CAMINANDO:
            self._caminar(dt, escena)

    def _caminar(self, dt, escena):
        dx = self.destino[0] - self.x
        dy = self.destino[1] - self.y
        distancia = math.hypot(dx, dy)
        paso = self.velocidad * dt      # cuántos píxeles avanza en este cuadro

        if distancia <= paso:
            # Llegó: se para en el destino y ejecuta la acción pendiente
            self.x, self.y = self.destino
            accion = self.al_llegar     # se guarda ANTES de detener(), que la borra
            self.detener()
            if accion:
                accion()
            return

        # Avanzamos un "paso" hacia el destino (vector normalizado * paso)
        nuevo_x = self.x + dx / distancia * paso
        nuevo_y = self.y + dy / distancia * paso

        # Si el paso nos saca de la zona caminable, nos frenamos
        if not escena.zona.contiene((nuevo_x, nuevo_y)):
            self.detener()
            return

        self.x, self.y = nuevo_x, nuevo_y
        if abs(dx) > 1:
            self.mirando_derecha = dx > 0
        self.tiempo_animacion += dt

    # ---------- Dibujo ----------

    def dibujar(self, superficie, fuente):
        """Cada juego lo implementa en su subclase (cómo se ve el personaje)."""
        raise NotImplementedError

    def dibujar_texto(self, superficie, fuente, y_cabeza, ancho_max=200):
        """Dibuja lo que dice el actor, centrado sobre su cabeza."""
        if not self.texto:
            return
        lineas = envolver_texto(self.texto, fuente, ancho_max)
        alto_linea = fuente.get_height()
        y = max(2, y_cabeza - 4 - alto_linea * len(lineas))
        mitad = ancho_max // 2 + 4
        # Que el texto no se salga de la pantalla por los costados
        centro_x = max(mitad, min(superficie.get_width() - mitad, int(self.x)))
        for i, linea in enumerate(lineas):
            texto(superficie, linea, fuente, self.color_texto,
                  (centro_x, y + i * alto_linea), ancla="midtop")
