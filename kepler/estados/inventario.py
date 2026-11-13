"""
kepler/estados/inventario.py
Estado INVENTARIO: la mochila se abre "encima" del juego.

  - Clic en un ítem        -> lo selecciona y muestra su descripción.
  - Clic en OTRO ítem      -> intenta combinarlos.
  - Clic en el mismo ítem  -> lo deselecciona.
  - Botón Usar             -> vuelve al juego con el ítem en la mano.
  - I / Esc / Cerrar       -> vuelve al juego.
"""

import pygame

from engine import Estado, Boton, texto, panel, envolver_texto, oscurecer, escalar
from kepler.config import (ANCHO, ALTO, BLANCO, AMARILLO, GRIS, TEXTO_HABLA, COLORES_BOTON,
                           UI_FONDO, UI_LUZ, UI_SOMBRA, UI_HUNDIDO)


class EstadoInventario(Estado):
    COLUMNAS, FILAS = 5, 2
    TAM, SEP = 44, 8
    MENSAJE_INICIAL = "Elegí un objeto. Elegí otro para combinarlos."

    def __init__(self, juego):
        super().__init__(juego)
        self.panel = pygame.Rect(16, 10, 288, 180)
        x0 = ANCHO // 2 - (self.COLUMNAS * self.TAM + (self.COLUMNAS - 1) * self.SEP) // 2
        self.casillas = []
        for fila in range(self.FILAS):
            for col in range(self.COLUMNAS):
                self.casillas.append(pygame.Rect(x0 + col * (self.TAM + self.SEP),
                                                 34 + fila * (self.TAM + self.SEP), self.TAM, self.TAM))
        fuente = juego.fuentes["normal"]
        self.boton_usar = Boton((x0, 168, 70, 16), "Usar", self.usar, fuente, COLORES_BOTON)
        self.boton_desarmar = Boton((ANCHO // 2 - 35, 168, 70, 16), "Desarmar", self.desarmar, fuente, COLORES_BOTON)
        self.boton_cerrar = Boton((ANCHO - x0 - 70, 168, 70, 16), "Cerrar", self.volver, fuente, COLORES_BOTON)
        # Íconos al doble de tamaño para la mochila (escalado entero: no se deforman los píxeles)
        self.iconos = {id_item: escalar(datos["icono"], 2) for id_item, datos in juego.catalogo.items()}
        self.seleccionado = None
        self.mensaje = ""

    def entrar(self):
        self.seleccionado = None
        self.mensaje = self.MENSAJE_INICIAL

    def volver(self):
        self.juego.cambiar_estado("JUGANDO")

    def desarmar(self):
        """Separa el ítem elegido en sus partes (por ejemplo, la caña en palo y cuerda)."""
        inventario = self.juego.inventario
        elegido = self.seleccionado
        partes = inventario.desarmar(elegido) if elegido else None
        if partes:
            nombres = " y ".join(inventario.datos(parte)["nombre"] for parte in partes)
            self.mensaje = f"Lo desarmé: ahora tengo {nombres}."
        self.seleccionado = None

    def usar(self):
        """Vuelve al escenario con el ítem en la mano para usarlo sobre algo."""
        self.juego.item_en_mano = self.seleccionado
        self.volver()

    # ---------- Eventos ----------

    def manejar_evento(self, evento):
        if evento.type == pygame.KEYDOWN and evento.key in (pygame.K_i, pygame.K_ESCAPE):
            self.volver()
        elif evento.type == pygame.MOUSEBUTTONDOWN:
            if evento.button == 3:
                self.seleccionado = None
                self.mensaje = self.MENSAJE_INICIAL
            elif evento.button == 1:
                if (self.boton_usar.manejar_evento(evento) or self.boton_desarmar.manejar_evento(evento)
                        or self.boton_cerrar.manejar_evento(evento)):
                    return
                self._clic_en_casilla(evento.pos)

    def _clic_en_casilla(self, pos):
        items = self.juego.inventario.items
        for i, casilla in enumerate(self.casillas):
            if casilla.collidepoint(pos):
                if i < len(items):
                    self._clic_en_item(items[i])
                return

    def _clic_en_item(self, id_item):
        inventario = self.juego.inventario
        nombre = inventario.datos(id_item)["nombre"]
        if self.seleccionado is None:
            self.seleccionado = id_item
            self.mensaje = f"{nombre}: {inventario.datos(id_item)['descripcion']}"
        elif self.seleccionado == id_item:
            self.seleccionado = None
            self.mensaje = self.MENSAJE_INICIAL
        else:
            primero = inventario.datos(self.seleccionado)["nombre"]
            resultado = inventario.combinar(self.seleccionado, id_item)
            if resultado:
                self.mensaje = f"¡Combiné {primero} y {nombre}! Ahora tengo: {inventario.datos(resultado)['nombre']}."
            else:
                self.mensaje = f"No se me ocurre cómo combinar {primero} con {nombre}."
            self.seleccionado = None

    # ---------- Dibujo ----------

    def dibujar(self, sup):
        fuentes = self.juego.fuentes
        inventario = self.juego.inventario

        self.juego.estados["JUGANDO"].dibujar(sup)    # el juego congelado de fondo...
        oscurecer(sup, 150)                           # ...oscurecido...
        panel(sup, self.panel, UI_FONDO, UI_LUZ, UI_SOMBRA)   # ...y la mochila encima
        texto(sup, "MOCHILA", fuentes["normal"], AMARILLO, (ANCHO // 2, 22), ancla="center")

        mouse = pygame.mouse.get_pos()
        for i, casilla in enumerate(self.casillas):
            id_item = inventario.items[i] if i < len(inventario.items) else None
            elegida = id_item is not None and id_item == self.seleccionado
            encima = id_item is not None and casilla.collidepoint(mouse)
            panel(sup, casilla, UI_HUNDIDO, UI_SOMBRA, UI_LUZ)
            if elegida or encima:
                pygame.draw.rect(sup, AMARILLO if elegida else GRIS, casilla, 1)
            if id_item:
                icono = self.iconos[id_item]
                sup.blit(icono, icono.get_rect(center=casilla.center))

        y = 136
        for linea in envolver_texto(self.mensaje, fuentes["normal"], self.panel.w - 20)[:2]:
            texto(sup, linea, fuentes["normal"], TEXTO_HABLA, (ANCHO // 2, y), ancla="midtop")
            y += fuentes["normal"].get_height()

        self.boton_usar.habilitado = self.seleccionado is not None
        self.boton_desarmar.habilitado = self.seleccionado is not None and inventario.se_puede_desarmar(self.seleccionado)
        self.boton_usar.dibujar(sup)
        self.boton_desarmar.dibujar(sup)
        self.boton_cerrar.dibujar(sup)
        texto(sup, "Clic der.: soltar", fuentes["chica"], GRIS, (self.panel.right - 6, 22), ancla="midright")
