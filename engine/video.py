"""
engine/video.py
Reproducir un video dentro de pygame. Pygame no trae reproductor de video, así que se usa ffmpeg (el programa que
trae el paquete 'imageio-ffmpeg': pip install imageio-ffmpeg) para decodificar el video en cuadros sueltos:

  - ffmpeg corre aparte y va largando los cuadros ya achicados al tamaño que se necesita (RGB, sin comprimir).
  - Un hilo los lee y los deja en una cola (así el juego no se traba esperando).
  - El juego pide "el cuadro que corresponde al segundo t" y lo dibuja como cualquier otra imagen.

El audio no sale por acá: se extrae a un archivo (extraer_audio) y suena por el mezclador de pygame; con la posición
de ese audio se sabe en qué segundo va el video (así imagen y sonido quedan sincronizados).
Si no está imageio-ffmpeg, disponible() devuelve False y el juego se saltea el video.
"""

import queue
import re
import subprocess
import threading

import pygame


def _ffmpeg():
    """La ruta del programa ffmpeg que trae imageio-ffmpeg, o None si no está instalado."""
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return None


def disponible():
    return _ffmpeg() is not None


def extraer_audio(ruta_video, ruta_salida):
    """Guarda el audio del video en un archivo .ogg (suena con el mezclador de pygame). Devuelve True si pudo."""
    exe = _ffmpeg()
    if exe is None:
        return False
    try:
        subprocess.run([exe, "-y", "-i", ruta_video, "-vn", "-c:a", "libvorbis", "-q:a", "4", ruta_salida],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        return True
    except (OSError, subprocess.CalledProcessError):
        return False


def _datos(exe, ruta):
    """(ancho, alto, fps, duración en segundos) del video, leyendo lo que ffmpeg cuenta de él."""
    p = subprocess.run([exe, "-i", ruta], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    texto = p.stderr.decode("utf-8", "replace")
    m = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", texto)
    ancho, alto = (int(m.group(1)), int(m.group(2))) if m else (480, 360)
    m = re.search(r"([\d.]+) fps", texto)
    fps = float(m.group(1)) if m else 30.0
    m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", texto)
    duracion = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + float(m.group(3)) if m else 0.0
    return ancho, alto, fps, duracion


class Video:
    def __init__(self, ruta, ancho_max, alto_max):
        """Abre el video y lo achica para que entre en ancho_max x alto_max (sin deformarlo)."""
        self.exe = _ffmpeg()
        if self.exe is None:
            raise RuntimeError("Falta imageio-ffmpeg")
        ancho, alto, self.fps, self.duracion = _datos(self.exe, ruta)
        escala = min(ancho_max / ancho, alto_max / alto)
        self.ancho = max(2, int(ancho * escala) // 2 * 2)
        self.alto = max(2, int(alto * escala) // 2 * 2)
        self._bytes_cuadro = self.ancho * self.alto * 3
        self._cola = queue.Queue(maxsize=90)
        self._parar = False
        self._terminado = False             # ffmpeg ya largó todos los cuadros
        self._cuadro = None                 # la imagen que se está mostrando
        self._pendiente = None              # el próximo cuadro (ya leído, todavía no le toca)
        self._proceso = subprocess.Popen(
            [self.exe, "-i", ruta, "-an", "-vf", f"scale={self.ancho}:{self.alto}", "-f", "rawvideo",
             "-pix_fmt", "rgb24", "-"],
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=self._bytes_cuadro * 4,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        self._hilo = threading.Thread(target=self._leer, daemon=True)
        self._hilo.start()

    def _leer(self):
        """Hilo: lee los cuadros que va largando ffmpeg y los deja en la cola (espera si la cola está llena)."""
        indice = 0
        try:
            while not self._parar:
                datos = self._proceso.stdout.read(self._bytes_cuadro)
                if len(datos) < self._bytes_cuadro:
                    break
                while not self._parar:
                    try:
                        self._cola.put((indice, datos), timeout=0.1)
                        break
                    except queue.Full:
                        pass
                indice += 1
        finally:
            self._terminado = True

    def cuadro(self, t):
        """La imagen (Surface) que corresponde al segundo t. Se salta los cuadros que ya quedaron atrás."""
        objetivo = int(t * self.fps)
        while True:
            if self._pendiente is None:
                try:
                    self._pendiente = self._cola.get_nowait()
                except queue.Empty:
                    break
            indice, datos = self._pendiente
            if indice > objetivo:
                break
            self._cuadro = pygame.image.frombuffer(datos, (self.ancho, self.alto), "RGB")
            self._pendiente = None
        return self._cuadro

    def terminó(self):
        """True cuando ya se largaron y se mostraron todos los cuadros."""
        return self._terminado and self._cola.empty() and self._pendiente is None

    def cerrar(self):
        self._parar = True
        try:
            self._proceso.kill()
        except OSError:
            pass
