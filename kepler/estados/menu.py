"""
kepler/estados/menu.py
Estado MENU: pantalla de inicio.
"""

import pygame

from engine import Estado, Boton, texto, bandas
from kepler import arte
from kepler.config import ANCHO, ALTO, TITULO, AMARILLO, BLANCO, GRIS, COLORES_BOTON


VOLUMEN_MUSICA = 0.3     # volumen de la música del menú (1.0 = el del archivo)


PASO_VOLUMEN = 0.1       # cuánto sube o baja cada clic en - y +


class EstadoMenu(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        fuente = juego.fuentes["normal"]
        x = ANCHO // 2 - 60
        # Según haya o no una partida empezada, el menú muestra "Continuar" o "Nueva partida" (ver entrar)
        self.boton_nueva = Boton((x, 84, 120, 16), "Nueva partida", self.nueva_partida, fuente, COLORES_BOTON)
        self.boton_continuar = Boton((x, 84, 120, 16), "Continuar", self.continuar, fuente, COLORES_BOTON)
        self.boton_salir = Boton((x, 104, 120, 16), "Salir", juego.terminar, fuente, COLORES_BOTON)
        self.botones = [self.boton_nueva, self.boton_salir]
        # Control de volumen: botones - y +, y una barra donde se puede hacer clic o arrastrar
        self.barra = pygame.Rect(ANCHO // 2 - 48, 142, 96, 8)
        self.boton_menos = Boton((ANCHO // 2 - 74, 138, 18, 16), "-", lambda: self.cambiar_volumen(-PASO_VOLUMEN), fuente, COLORES_BOTON)
        self.boton_mas = Boton((ANCHO // 2 + 56, 138, 18, 16), "+", lambda: self.cambiar_volumen(PASO_VOLUMEN), fuente, COLORES_BOTON)
        self.arrastrando = False
        # El fondo es fijo: se dibuja una sola vez
        self.fondo = pygame.Surface((ANCHO, ALTO))
        bandas(self.fondo, (0, 0, ANCHO, ALTO), [(10, 8, 26), (16, 12, 38), (24, 16, 50), (34, 20, 62),
                                                 (46, 24, 72), (60, 28, 80)])
        arte.planeta(self.fondo, (ANCHO // 2, 268), 110, (190, 74, 56), (130, 44, 44), franja=(210, 96, 66))
        arte.planeta(self.fondo, (270, 112), 10, (90, 150, 230), (50, 90, 170), anillo=(200, 210, 240))

    def entrar(self):
        # Al arrancar: "Nueva partida". Con una partida empezada (Esc): "Continuar", sin "Nueva partida".
        primero = self.boton_continuar if self.juego.partida_en_curso else self.boton_nueva
        self.botones = [primero, self.boton_salir]
        # La música suena solo en el menú de inicio
        self.juego.sonidos.reproducir_musica("musica_menu", volumen=VOLUMEN_MUSICA)

    def salir(self):
        self.juego.sonidos.detener_musica()

    def nueva_partida(self):
        self.juego.nueva_partida()
        self.juego.partida_en_curso = True
        self.juego.cambiar_estado("INTRO")      # la cápsula se estrella; después sigue el juego

    def continuar(self):
        self.juego.cambiar_estado("JUGANDO")

    # ---------- Volumen ----------

    def cambiar_volumen(self, delta):
        self.poner_volumen(round((self.juego.sonidos.volumen_general + delta) * 10) / 10)

    def poner_volumen(self, valor):
        self.juego.sonidos.poner_volumen_general(valor)
        self.juego.guardar_ajustes()

    def _volumen_en(self, x):
        """El volumen que corresponde a un clic en la posición x de la barra (de 0 a 1, de a 5 %)."""
        return round(max(0.0, min(1.0, (x - self.barra.x) / self.barra.w)) * 20) / 20

    def manejar_evento(self, evento):
        if self.boton_menos.manejar_evento(evento) or self.boton_mas.manejar_evento(evento):
            return
        if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and self.barra.inflate(8, 12).collidepoint(evento.pos):
            self.arrastrando = True
            self.poner_volumen(self._volumen_en(evento.pos[0]))
            return
        if evento.type == pygame.MOUSEMOTION and self.arrastrando:
            self.poner_volumen(self._volumen_en(evento.pos[0]))
            return
        if evento.type == pygame.MOUSEBUTTONUP:
            self.arrastrando = False
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_LEFT, pygame.K_RIGHT):
            self.cambiar_volumen(PASO_VOLUMEN if evento.key == pygame.K_RIGHT else -PASO_VOLUMEN)
            return
        for boton in self.botones:
            if boton.manejar_evento(evento):
                return
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE and self.juego.partida_en_curso:
            self.continuar()                     # Esc otra vez cierra el menú y sigue el juego (no cierra el juego)

    def dibujar(self, sup):
        sup.blit(self.fondo, (0, 0))
        arte.estrellas(sup, (0, 0, ANCHO, 150), 70, semilla=1, tiempo=self.juego.tiempo)
        fuentes = self.juego.fuentes
        texto(sup, TITULO.upper(), fuentes["titulo"], AMARILLO, (ANCHO // 2, 40), ancla="center",
              sombra=(90, 30, 40))
        texto(sup, "Una aventura gráfica espacial", fuentes["normal"], BLANCO, (ANCHO // 2, 62), ancla="center")
        for boton in self.botones:
            boton.dibujar(sup)
        # Control de volumen
        volumen = self.juego.sonidos.volumen_general
        texto(sup, f"Volumen: {round(volumen * 100)}%", fuentes["normal"], BLANCO, (ANCHO // 2, 130), ancla="center")
        self.boton_menos.dibujar(sup)
        self.boton_mas.dibujar(sup)
        pygame.draw.rect(sup, (20, 14, 34), self.barra.inflate(2, 2))
        pygame.draw.rect(sup, (60, 50, 90), self.barra)
        relleno = pygame.Rect(self.barra.x, self.barra.y, int(self.barra.w * volumen), self.barra.h)
        pygame.draw.rect(sup, AMARILLO, relleno)
        pygame.draw.rect(sup, BLANCO, (self.barra.x + int(self.barra.w * volumen) - 1, self.barra.y - 2, 3, self.barra.h + 4))
        texto(sup, "Flechas: volumen", fuentes["chica"], GRIS, (ANCHO // 2, 166), ancla="center")
        texto(sup, "F11: pantalla completa", fuentes["chica"], GRIS, (ANCHO // 2, ALTO - 8), ancla="center")
