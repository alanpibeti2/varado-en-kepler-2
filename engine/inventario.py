"""
engine/inventario.py
Inventario genérico con soporte para COMBINAR ítems.

El motor no sabe qué ítems existen: el juego le pasa un CATÁLOGO
(los datos de cada ítem) y un diccionario de RECETAS (qué par de ítems
da qué resultado). Así se separan los DATOS de la LÓGICA.

Ejemplo:
    catalogo = {"bateria": {...}, "cable": {...}, "bateria_con_cable": {...}}
    recetas  = {frozenset({"bateria", "cable"}): "bateria_con_cable"}
    inventario = Inventario(catalogo, recetas)
"""


class Inventario:
    def __init__(self, catalogo, recetas=None, capacidad=10, desarmes=None):
        self.catalogo = catalogo        # id -> datos del ítem (nombre, descripción, ícono...)
        self.recetas = recetas or {}    # frozenset({id_a, id_b}) -> id_resultado
        self.capacidad = capacidad
        self.desarmes = desarmes or {}  # id_item -> (id_a, id_b): lo que queda al desarmarlo
        self.items = []                 # lista de ids, en el orden en que se agarraron

    def agregar(self, id_item):
        """Agrega un ítem. Devuelve False si está lleno o ya lo tiene."""
        if id_item not in self.catalogo:
            raise KeyError(f"El ítem '{id_item}' no está en el catálogo")
        if len(self.items) >= self.capacidad or id_item in self.items:
            return False
        self.items.append(id_item)
        return True

    def quitar(self, id_item):
        if id_item in self.items:
            self.items.remove(id_item)

    def tiene(self, id_item):
        return id_item in self.items

    def datos(self, id_item):
        """Devuelve la información del ítem (nombre, descripción, ícono...)."""
        return self.catalogo[id_item]

    def se_puede_desarmar(self, id_item):
        return id_item in self.desarmes and id_item in self.items

    def desarmar(self, id_item):
        """Separa un ítem armado en sus dos partes. Devuelve (parte_a, parte_b), o None si no se puede."""
        if not self.se_puede_desarmar(id_item):
            return None
        partes = self.desarmes[id_item]
        self.quitar(id_item)
        for parte in partes:
            self.agregar(parte)
        return partes

    def combinar(self, a, b):
        """
        Intenta combinar dos ítems. Si existe la receta, saca los dos
        originales, agrega el resultado y lo devuelve. Si no, devuelve None.
        Usamos frozenset (conjunto sin orden) para que "a + b" y "b + a"
        sean la misma receta.
        """
        resultado = self.recetas.get(frozenset({a, b}))
        if resultado:
            self.quitar(a)
            self.quitar(b)
            self.agregar(resultado)
        return resultado
