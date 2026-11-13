"""
engine/sonido.py
Reproduce efectos de sonido, voces y música a partir de archivos en una carpeta.

Se usa por NOMBRE, sin extensión:
    sonidos.reproducir("voz_minero")        # busca voz_minero.ogg, .wav o .mp3 en la carpeta
    sonidos.reproducir_musica("musica_menu")

Si el archivo no existe, o la computadora no tiene audio, no pasa nada: el juego sigue
en silencio. Así se pueden ir agregando sonidos de a uno, sin que se rompa nada.
"""

import os

import pygame

EXTENSIONES = (".ogg", ".wav", ".mp3")


class Sonidos:
    def __init__(self, carpeta):
        self.carpeta = carpeta
        self._cache = {}      # nombre -> Sound (o None si no existe), para no leer el disco cada vez
        self._musica_actual = None
        self._musica_pausada = False      # True mientras la música espera a que termine otro sonido
        self.volumen_general = 1.0        # el volumen de todo el juego (0 a 1): se multiplica con el de cada sonido
        self._volumen_musica = 0.6        # el volumen propio de la música que suena (antes de multiplicar)
        self.disponible = pygame.mixer.get_init() is not None
        if not self.disponible:
            try:
                pygame.mixer.init()
                self.disponible = True
            except pygame.error:
                self.disponible = False

    def _ruta(self, nombre):
        """La ruta del archivo 'nombre' con la primera extensión que exista, o None."""
        for extension in EXTENSIONES:
            ruta = os.path.join(self.carpeta, nombre + extension)
            if os.path.exists(ruta):
                return ruta
        return None

    # ---------- Efectos y voces ----------

    def _cargar(self, nombre):
        if nombre not in self._cache:
            sonido = None
            ruta = self._ruta(nombre)
            if ruta:
                try:
                    sonido = pygame.mixer.Sound(ruta)
                except pygame.error:
                    sonido = None       # archivo roto o formato no soportado
            self._cache[nombre] = sonido
        return self._cache[nombre]

    def reproducir(self, nombre, volumen=1.0, cortar=True, bucle=False):
        """
        Suena 'nombre' una vez (o en bucle, hasta que se lo corte con detener_efectos).
        Con 'cortar', si ya estaba sonando, lo reinicia.
        """
        if not self.disponible:
            return
        sonido = self._cargar(nombre)
        if sonido is None:
            return
        if cortar:
            sonido.stop()
        sonido.set_volume(volumen * self.volumen_general)
        sonido.play(loops=-1 if bucle else 0)

    def detener_efectos(self):
        """Corta todos los efectos y voces que estén sonando (la música sigue)."""
        if self.disponible:
            pygame.mixer.stop()

    def actualizar(self):
        """
        Llamar una vez por cuadro. La música de fondo se PAUSA mientras suena cualquier efecto
        o voz, y sigue desde donde estaba cuando ese sonido termina.
        """
        if not self.disponible:
            return
        hay_efecto = pygame.mixer.get_busy()
        if hay_efecto and not self._musica_pausada and self._musica_actual:
            pygame.mixer.music.pause()
            self._musica_pausada = True
        elif not hay_efecto and self._musica_pausada:
            pygame.mixer.music.unpause()
            self._musica_pausada = False

    # ---------- Volumen general ----------

    def poner_volumen_general(self, valor):
        """Cambia el volumen de todo el juego (0 a 1); la música que suena lo toma al instante."""
        self.volumen_general = max(0.0, min(1.0, valor))
        if self.disponible:
            pygame.mixer.music.set_volume(self._volumen_musica * self.volumen_general)

    # ---------- Música de fondo ----------

    def reproducir_musica(self, nombre, volumen=0.6, repetir=True):
        """
        Empieza la música 'nombre' (una sola a la vez; si suena otra, la reemplaza).
        Con 'repetir', suena en bucle. Si ya está sonando esa misma, no la reinicia.
        """
        if not self.disponible:
            return
        if nombre == self._musica_actual and pygame.mixer.music.get_busy():
            return
        ruta = self._ruta(nombre)
        if ruta is None:
            return
        try:
            pygame.mixer.music.load(ruta)
            self._volumen_musica = volumen
            pygame.mixer.music.set_volume(volumen * self.volumen_general)
            pygame.mixer.music.play(-1 if repetir else 0)
            self._musica_actual = nombre
            self._musica_pausada = False
            if pygame.mixer.get_busy():           # si justo suena un efecto, la música espera
                pygame.mixer.music.pause()
                self._musica_pausada = True
        except pygame.error:
            pass

    def detener_musica(self, fade_ms=500):
        """Baja la música de a poco hasta apagarla."""
        if self.disponible:
            if self._musica_pausada:                # una música pausada no se puede apagar con fundido
                pygame.mixer.music.unpause()
            pygame.mixer.music.fadeout(fade_ms)
        self._musica_actual = None
        self._musica_pausada = False
