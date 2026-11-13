"""
engine/dialogo.py
Conversaciones con opciones múltiples, armadas como un ÁRBOL DE NODOS.

  - Un Nodo es lo que dice un personaje en un momento de la charla.
  - Cada Nodo tiene Opciones: lo que el jugador puede responder.
  - Cada Opción lleva a otro nodo (por su nombre) o termina la charla (None).

Ejemplo:
    nodos = {
        "inicio": Nodo("Robot", "¡Hola! ¿Qué querés saber?", [
            Opcion("¿Quién sos?", "quien"),
            Opcion("Chau.", None),
        ]),
        "quien": Nodo("Robot", "Soy un robot minero.", siguiente="inicio"),
    }
    charla = Dialogo(nodos, "inicio")

Las opciones pueden tener:
  - condicion: función que devuelve True/False (si es False, la opción no aparece).
  - accion: función que se ejecuta al elegirla (ej: el robot te da un ítem).
"""


class Opcion:
    def __init__(self, texto, siguiente=None, condicion=None, accion=None):
        self.texto = texto            # lo que dice el jugador
        self.siguiente = siguiente    # nombre del próximo nodo, o None para terminar
        self.condicion = condicion
        self.accion = accion

    @property
    def disponible(self):
        return self.condicion is None or self.condicion()


class Nodo:
    def __init__(self, hablante, texto, opciones=None, siguiente=None):
        self.hablante = hablante      # quién habla (se muestra arriba del texto)
        self.texto = texto
        self.opciones = opciones or []
        self.siguiente = siguiente    # si no hay opciones: a qué nodo seguir (None = fin)


class Dialogo:
    def __init__(self, nodos, inicio):
        self.nodos = nodos
        self.actual = nodos[inicio]
        self.terminado = False

    def opciones_disponibles(self):
        """Las opciones del nodo actual que cumplen su condición."""
        return [opcion for opcion in self.actual.opciones if opcion.disponible]

    def elegir(self, opcion):
        """El jugador eligió una opción: se ejecuta su acción y se avanza."""
        if opcion.accion:
            opcion.accion()
        self._ir_a(opcion.siguiente)

    def continuar(self):
        """Para nodos sin opciones: pasa al nodo siguiente (o termina)."""
        self._ir_a(self.actual.siguiente)

    def _ir_a(self, nombre):
        if nombre is None:
            self.terminado = True
        else:
            self.actual = self.nodos[nombre]
