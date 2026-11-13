"""
kepler/estados/jugando.py
Estado JUGANDO: la astronauta en el escenario, con el panel de verbos abajo.

Qué pasa con un clic en el escenario:
  - Con un ítem en la mano + objeto -> camina y usa el ítem sobre el objeto.
  - Con un verbo + objeto           -> camina y, al llegar, ejecuta el verbo
                                       (excepto Mirar: se ejecuta al instante, sin caminar).
  - Sin verbo, sobre una salida     -> camina y cambia de escenario
                                       (con doble clic, cambia de golpe sin caminar).
  - Sin verbo, sobre el piso        -> camina hasta ahí.
  - Fuera del piso                  -> no pasa nada.
"""

import pygame

from engine import Estado, Boton, texto, panel, envolver_texto
from kepler.config import (ANCHO, ALTO, ALTO_ESCENA, BLANCO, GRIS, COLORES_BOTON,
                           UI_FONDO, UI_LUZ, UI_SOMBRA, UI_HUNDIDO)


VOLUMEN_MUSICA = 0.75    # volumen de la música ambiente del juego (1.0 = el del archivo)
# Escenas con música propia (el resto usa "musica_juego"). El nombre es el del archivo, sin la extensión.
MUSICA_ESCENA = {
    "mercado": "Elevator music for Aliens - Restless Party track 1",
    "cueva_interior": "Alien Music",                       # adentro de la mina
    "plataforma": "Cornfield Chase - Hans Zimmer - Best Part",    # la zona de despegue
}
MUSICA_PLAYA_PELIGRO = "Pokémon Omega Ruby & Alpha Sapphire - Cobalion, Virizion & Terrakion Battle Music (HQ)"
# Volumen propio de algunos temas (los que no están acá usan VOLUMEN_MUSICA)
VOLUMEN_TEMA = {MUSICA_PLAYA_PELIGRO: 0.5}
DOBLE_CLIC_MS = 350      # dos clics sobre una salida en menos de esto = cambia de pantalla sin caminar


class EstadoJugando(Estado):
    VERBOS = ["Mirar", "Agarrar", "Usar", "Hablar"]

    def __init__(self, juego):
        super().__init__(juego)
        self.verbo = None              # verbo elegido; None = solo caminar
        self.debug = False             # F1 muestra las zonas
        self.objeto_bajo_mouse = None
        self._clic_anterior = (None, 0)    # (objeto, momento en ms) del último clic, para detectar el doble clic

        fuente = juego.fuentes["normal"]
        # Cuatro verbos en una grilla de 2 x 2. 'lambda v=verbo' guarda el verbo de ESE botón.
        self.botones_verbo = {}
        for i, verbo in enumerate(self.VERBOS):
            x = 6 + (i % 2) * 52
            y = ALTO_ESCENA + 14 + (i // 2) * 18
            self.botones_verbo[verbo] = Boton((x, y, 48, 16), verbo, lambda v=verbo: self.elegir_verbo(v),
                                              fuente, COLORES_BOTON)
        self.boton_mochila = Boton((220, ALTO_ESCENA + 14, 94, 34), "Mochila", self.abrir_inventario,
                                   fuente, COLORES_BOTON, icono=juego.sprites["mochila"])

    def entrar(self):
        # Los diálogos y la mochila vuelven acá sin reiniciar la música (si ya suena la de la escena, sigue).
        self.poner_musica()

    def poner_musica(self):
        """La música de la escena actual: la del juego, salvo en las escenas que tienen la suya (el mercado)."""
        escena = self.juego.nombre_escena_actual()
        nombre = MUSICA_ESCENA.get(escena, "musica_juego")
        # En la playa, la música de batalla suena solo mientras la mercader sigue acorralada por el perro
        if escena == "playa" and not self.juego.progreso["perro_ahuyentado"]:
            nombre = MUSICA_PLAYA_PELIGRO
        self.juego.sonidos.reproducir_musica(nombre, volumen=VOLUMEN_TEMA.get(nombre, VOLUMEN_MUSICA))

    # ---------- Acciones de la interfaz ----------

    def elegir_verbo(self, verbo):
        self.juego.item_en_mano = None
        self.verbo = None if self.verbo == verbo else verbo   # si ya estaba elegido, se desmarca

    def abrir_inventario(self):
        self.verbo = None
        self.juego.cambiar_estado("INVENTARIO")

    # ---------- Eventos ----------

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_i:
                self.abrir_inventario()
            elif evento.key == pygame.K_ESCAPE:
                self.juego.cambiar_estado("MENU")
            elif evento.key == pygame.K_F1:
                self.debug = not self.debug

        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 3:                 # clic derecho: cancela verbo e ítem
                self.verbo = None
                self.juego.item_en_mano = None
            elif evento.button == 1:
                if evento.pos[1] >= ALTO_ESCENA:   # clic en el panel de abajo
                    for boton in [*self.botones_verbo.values(), self.boton_mochila]:
                        if boton.manejar_evento(evento):
                            return
                else:
                    self._clic_en_escena(evento.pos)

    def _camara(self):
        """(zoom, x0, y0): cuánto se acerca la escena y desde qué punto se ve. Sin zoom: (1, 0, 0)."""
        escena = self.juego.escena
        zoom = escena.zoom
        if zoom == 1:
            return 1, 0, 0
        ancho, alto = int(ANCHO / zoom), int(ALTO_ESCENA / zoom)
        x0 = max(0, min(ANCHO - ancho, int(self.juego.personaje.x) - ancho // 2))
        y0 = max(0, min(ALTO_ESCENA - alto, escena.zoom_y))
        return zoom, x0, y0

    def _a_escena(self, pos):
        """Pasa un punto de la pantalla a coordenadas de la escena (por el zoom de la cámara)."""
        zoom, x0, y0 = self._camara()
        return (pos[0] / zoom + x0, pos[1] / zoom + y0)

    def _clic_en_escena(self, pos):
        juego = self.juego
        if juego.escena.bloqueada:             # una animación en curso: no se puede hacer otra cosa
            return
        pos = self._a_escena(pos)
        personaje = juego.personaje
        objeto = juego.escena.objeto_en(pos)

        # ¿Es el segundo clic seguido sobre el mismo objeto?
        ahora = pygame.time.get_ticks()
        anterior, momento = self._clic_anterior
        doble_clic = objeto is not None and objeto is anterior and ahora - momento <= DOBLE_CLIC_MS
        self._clic_anterior = (objeto, ahora)

        if objeto is None:
            if juego.escena.zona.contiene(pos):    # clic en el piso: caminar
                personaje.ir_a(pos)
            return                                 # clic fuera del piso: se ignora

        # Guardamos en variables lo que la lambda tiene que "recordar" para cuando llegue
        if juego.item_en_mano:
            item = juego.item_en_mano
            juego.item_en_mano = None
            personaje.ir_a(objeto.punto_interaccion, al_llegar=lambda: self._usar_item(item, objeto))
        elif self.verbo == "Mirar":
            self.verbo = None                      # mirar se hace desde lejos: no hace falta caminar
            personaje.detener()
            self._ejecutar_accion("Mirar", objeto)
        elif self.verbo:
            verbo = self.verbo
            self.verbo = None
            personaje.ir_a(objeto.punto_interaccion, al_llegar=lambda: self._ejecutar_accion(verbo, objeto))
        elif objeto.salida:
            nombre_escena, entrada = objeto.salida
            if doble_clic:                         # doble clic en una salida: se va directo, sin caminar
                self._clic_anterior = (None, 0)
                juego.ir_a_escena(nombre_escena, entrada)    # (ir_a_escena ya detiene al personaje)
            else:
                personaje.ir_a(objeto.punto_interaccion, al_llegar=lambda: juego.ir_a_escena(nombre_escena, entrada))
        else:
            personaje.ir_a(objeto.punto_interaccion)

    def _ejecutar_accion(self, verbo, objeto):
        juego = self.juego
        if verbo == "Agarrar" and objeto.id_item:
            juego.inventario.agregar(objeto.id_item)
            juego.escena.quitar_objeto(objeto)
            juego.personaje.decir("¡Esto me puede servir!")
            return
        respuesta = objeto.responder(verbo)    # texto, o None si el objeto hizo otra cosa
        if respuesta:
            juego.personaje.decir(respuesta)

    def _usar_item(self, item, objeto):
        respuesta = objeto.usar_item(item)
        if respuesta:
            self.juego.personaje.decir(respuesta)

    # ---------- Lógica ----------

    def actualizar(self, dt):
        self.juego.personaje.actualizar(dt, self.juego.escena)
        self.juego.escena.actualizar(dt)
        mouse = pygame.mouse.get_pos()
        self.objeto_bajo_mouse = (self.juego.escena.objeto_en(self._a_escena(mouse))
                                  if mouse[1] < ALTO_ESCENA else None)

    def _linea_de_accion(self):
        """El texto de abajo, estilo Monkey Island: 'Usar Linterna en compuerta'."""
        objeto = self.objeto_bajo_mouse
        nombre = objeto.nombre if objeto else ""
        if self.juego.item_en_mano:
            base = f"Usar {self.juego.catalogo[self.juego.item_en_mano]['nombre']} en"
        elif self.verbo:
            base = self.verbo
        elif objeto and objeto.salida:
            base = "Ir a"
        elif objeto:
            base = ""
        else:
            base = "Caminar"
        return f"{base} {nombre}".strip()

    # ---------- Dibujo ----------

    def dibujar(self, sup):
        juego = self.juego
        fuentes = juego.fuentes

        zoom, x0, y0 = self._camara()
        personaje = juego.personaje
        if zoom == 1:
            juego.escena.dibujar(sup)
            if self.debug:
                juego.escena.dibujar_debug(sup)
            personaje.dibujar(sup, fuentes["normal"])
        else:
            # Con zoom: se dibuja la escena entera aparte, se recorta lo que ve la cámara y se agranda (píxeles enteros)
            completa = pygame.Surface((ANCHO, ALTO_ESCENA))
            juego.escena.dibujar(completa)
            if self.debug:
                juego.escena.dibujar_debug(completa)
            texto_dicho, personaje.texto = personaje.texto, ""        # el texto se dibuja después, sin agrandar
            personaje.dibujar(completa, fuentes["normal"])
            personaje.texto = texto_dicho
            vista = completa.subsurface((x0, y0, int(ANCHO / zoom), int(ALTO_ESCENA / zoom)))
            sup.blit(pygame.transform.scale(vista, (ANCHO, ALTO_ESCENA)), (0, 0))
            if texto_dicho:
                x_real = personaje.x
                personaje.x = (x_real - x0) * zoom
                cabeza = (personaje.y - personaje.cuadros_derecha[0].get_height() - y0) * zoom
                personaje.dibujar_texto(sup, fuentes["normal"], int(cabeza))
                personaje.x = x_real

        # Panel inferior
        panel(sup, (0, ALTO_ESCENA, ANCHO, ALTO - ALTO_ESCENA), UI_FONDO, UI_LUZ, UI_SOMBRA)
        texto(sup, self._linea_de_accion(), fuentes["normal"], BLANCO, (ANCHO // 2, ALTO_ESCENA + 7),
              ancla="center")
        for verbo, boton in self.botones_verbo.items():
            boton.dibujar(sup, activo=(verbo == self.verbo))
        self.boton_mochila.texto = f"Mochila ({len(juego.inventario.items)})"
        self.boton_mochila.dibujar(sup)

        # Recuadro central: muestra el ítem que tenés en la mano
        caja = pygame.Rect(112, ALTO_ESCENA + 14, 102, 34)
        panel(sup, caja, UI_HUNDIDO, UI_SOMBRA, UI_LUZ)      # luz y sombra invertidas = hundido
        if juego.item_en_mano:
            datos = juego.catalogo[juego.item_en_mano]
            sup.blit(datos["icono"], (caja.x + 4, caja.centery - 7))
            lineas = envolver_texto(datos["nombre"], fuentes["chica"], caja.w - 26)
            y = caja.centery - len(lineas) * 5
            for i, linea in enumerate(lineas):
                texto(sup, linea, fuentes["chica"], BLANCO, (caja.x + 22, y + i * 10))
        else:
            texto(sup, "F1: ver zonas", fuentes["chica"], GRIS, caja.center, ancla="center")
