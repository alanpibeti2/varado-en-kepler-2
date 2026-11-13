"""
engine/estado.py
Clase base para los estados de la máquina de estados.

Todos los estados tienen los mismos métodos. Gracias a eso el bucle
principal no necesita saber en qué estado está: le pasa todo al estado
actual y cada uno responde a su manera.
"""


class Estado:
    def __init__(self, juego):
        self.juego = juego   # referencia al Juego, para cambiar de estado o leer datos

    def entrar(self):
        """Se llama cada vez que el juego ENTRA a este estado."""
        pass

    def salir(self):
        """Se llama cada vez que el juego SALE de este estado."""
        pass

    def manejar_evento(self, evento):
        """Recibe cada evento de pygame (clic, tecla...)."""
        pass

    def actualizar(self, dt):
        """Lógica de un cuadro. 'dt' = segundos desde el cuadro anterior."""
        pass

    def dibujar(self, superficie):
        """Dibuja el estado en pantalla."""
        pass
