"""
kepler/estados/video.py
Estado VIDEO: un video a pantalla completa (con letterbox) y con su sonido. Se usa después de la animación final.
Clic o cualquier tecla lo saltean (pasada medio segundo, para no saltearlo sin querer). Al terminar, vuelve al FINAL.

El video se decodifica con ffmpeg (ver engine/video.py). Si falta imageio-ffmpeg o el archivo, se saltea sin problemas.
"""

import os
import time

import pygame

from engine import Estado, texto
from engine import video as motor_video
from kepler.config import ANCHO, ALTO, CARPETA_SONIDOS, GRIS, TITULO, AMARILLO, BLANCO

ARCHIVO_VIDEO = os.path.join(CARPETA_SONIDOS, "Green Alien Singing Pompeii.mp4")
NOMBRE_AUDIO = "video_final"          # el audio del video, extraído a sonidos/video_final.ogg


class EstadoVideo(Estado):
    def __init__(self, juego):
        super().__init__(juego)
        self.video = None
        self.t_local = 0.0            # reloj propio (por si el audio no está disponible)
        self.saltear = False
        self.con_audio = False

    def entrar(self):
        self.t_local = 0.0
        self.saltear = False
        self.video = None
        self.con_audio = False
        sonidos = self.juego.sonidos
        if not os.path.exists(ARCHIVO_VIDEO) or not motor_video.disponible():
            self.saltear = True                           # sin video o sin ffmpeg: se sigue de largo
            return
        try:
            self.video = motor_video.Video(ARCHIVO_VIDEO, ANCHO, ALTO)
        except Exception:
            self.saltear = True
            return
        ruta_audio = os.path.join(CARPETA_SONIDOS, NOMBRE_AUDIO + ".ogg")
        if not os.path.exists(ruta_audio):                # la primera vez, se extrae el audio del video
            motor_video.extraer_audio(ARCHIVO_VIDEO, ruta_audio)
        sonidos.detener_musica(fade_ms=200)
        time.sleep(0.25)                                  # que termine el fundido de la música del juego
        sonidos.reproducir_musica(NOMBRE_AUDIO, volumen=1.0, repetir=False)
        self.con_audio = sonidos.disponible and pygame.mixer.music.get_busy()

    def salir(self):
        if self.video is not None:
            self.video.cerrar()
            self.video = None
        self.juego.sonidos.detener_musica(fade_ms=200)

    def manejar_evento(self, evento):
        if self.t_local > 0.5 and evento.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
            self.saltear = True

    def _segundo(self):
        """En qué segundo va el video: el del audio, si está sonando; si no, el del reloj propio."""
        if self.con_audio:
            pos = pygame.mixer.music.get_pos()
            if pos >= 0:
                return pos / 1000.0
        return self.t_local

    def actualizar(self, dt):
        self.t_local += dt
        terminado = self.saltear
        if self.video is not None and not terminado:
            if self.video.terminó():
                terminado = True
            elif self.con_audio and self.t_local > 3 and not pygame.mixer.music.get_busy():
                terminado = True                           # se acabó el audio
        if terminado:
            self.juego.estados["FINAL"].volviendo_del_video = True
            self.juego.cambiar_estado("FINAL")

    def dibujar(self, sup):
        sup.fill((0, 0, 0))
        if self.video is not None:
            imagen = self.video.cuadro(self._segundo())
            if imagen is not None:
                sup.blit(imagen, imagen.get_rect(center=(ANCHO // 2, ALTO // 2)))
        # Créditos sobre el video
        fuentes = self.juego.fuentes
        texto(sup, f"Gracias por jugar {TITULO}", fuentes["normal"], AMARILLO, (ANCHO // 2, 12), ancla="center",
              sombra=(60, 30, 80))
        texto(sup, "Hecho por Alan", fuentes["normal"], BLANCO, (ANCHO // 2, ALTO - 14), ancla="center")
        if self.t_local < 4:
            texto(sup, "clic para saltar", fuentes["chica"], GRIS, (ANCHO - 4, ALTO - 3), ancla="bottomright")
