"""
engine/juego.py
El corazón del motor: la clase Juego.

Se encarga de:
  1. Crear una ventana PIXELADA: se dibuja todo en una superficie chica
     (por ejemplo 320x200, como los juegos de 16 bits) y pygame la agranda
     multiplicando cada píxel, sin suavizar.
  2. Ejecutar el BUCLE PRINCIPAL (game loop).
  3. Manejar la MÁQUINA DE ESTADOS FINITOS.

Cómo se usa (desde el juego):
    class MiJuego(Juego):
        def __init__(self):
            super().__init__(320, 200, "Mi juego")
            self.registrar_estado("MENU", EstadoMenu(self))
            self.cambiar_estado("MENU")

    MiJuego().ejecutar()
"""

import os

import pygame

# Le pedimos a SDL (la librería que usa pygame por debajo) que al agrandar
# la imagen use "vecino más cercano": cada píxel se vuelve un cuadrado nítido.
os.environ.setdefault("SDL_RENDER_SCALE_QUALITY", "0")


class Juego:
    def __init__(self, ancho, alto, titulo, fps=60):
        pygame.init()
        self.ancho = ancho
        self.alto = alto
        # pygame.SCALED: trabajamos en 'ancho x alto' píxeles "lógicos" y pygame
        # agranda la ventana a un múltiplo entero que entre en el monitor.
        # Bonus: las posiciones del mouse ya llegan convertidas a esos píxeles.
        self.pantalla = pygame.display.set_mode((ancho, alto), pygame.SCALED)
        pygame.display.set_caption(titulo)
        self.reloj = pygame.time.Clock()
        self.fps = fps
        self.corriendo = False
        self.tiempo = 0.0          # segundos desde que arrancó (sirve para animaciones)

        # --- Máquina de estados ---
        self.estados = {}          # nombre -> objeto Estado
        self.estado_actual = None
        self.nombre_estado = None

    # ------------------------------------------------------------------ #
    #  Máquina de estados
    # ------------------------------------------------------------------ #
    def registrar_estado(self, nombre, estado):
        """Agrega un estado. Se crea una sola vez y se reutiliza."""
        self.estados[nombre] = estado

    def cambiar_estado(self, nombre):
        """Transición: sale del estado actual y entra al nuevo."""
        if nombre not in self.estados:
            raise KeyError(f"No existe el estado '{nombre}'")
        if self.estado_actual is not None:
            self.estado_actual.salir()
        self.nombre_estado = nombre
        self.estado_actual = self.estados[nombre]
        self.estado_actual.entrar()

    def terminar(self):
        """Pide cerrar el juego al terminar el cuadro actual."""
        self.corriendo = False

    def actualizar_general(self, dt):
        """Se llama en cada cuadro, sea cual sea el estado. El juego lo sobrescribe si lo necesita."""
        pass

    # ------------------------------------------------------------------ #
    #  Bucle principal
    # ------------------------------------------------------------------ #
    def ejecutar(self):
        """Eventos -> actualizar -> dibujar, 'fps' veces por segundo."""
        if self.estado_actual is None:
            raise RuntimeError("Llamá a cambiar_estado() antes de ejecutar()")

        self.corriendo = True
        while self.corriendo:
            dt = self.reloj.tick(self.fps) / 1000   # segundos desde el cuadro anterior
            self.tiempo += dt

            # 1) Eventos
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    self.terminar()
                elif evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                    pygame.display.toggle_fullscreen()   # F11: pantalla completa
                else:
                    self.estado_actual.manejar_evento(evento)

            # 2) Lógica
            self.estado_actual.actualizar(dt)
            self.actualizar_general(dt)

            # 3) Dibujo
            self.estado_actual.dibujar(self.pantalla)
            pygame.display.flip()

        pygame.quit()
