"""
kepler/items.py
DATOS del inventario: qué ítems existen y qué se combina con qué.
El Inventario del engine usa estos diccionarios.
"""


def crear_catalogo(sprites):
    """El catálogo necesita los íconos, por eso se arma después de crear los sprites."""
    return {
        "billetera": {
            "nombre": "Billetera",
            "descripcion": "Mi billetera de siempre, con cambio por las dudas.",
            "icono": sprites["billetera"],
        },
        "billetera_vacia": {
            "nombre": "Billetera vacía",
            "descripcion": "Mi billetera. Ya no me queda cambio.",
            "icono": sprites["billetera"],
        },
        "linterna": {
            "nombre": "Linterna",
            "descripcion": "La linterna de R-7. Ilumina bastante.",
            "icono": sprites["linterna"],
        },
        "coca": {
            "nombre": "Coca de 3L",
            "descripcion": "Una coca de 3 litros. Está medio tibia, pero tiene gas.",
            "icono": sprites["coca"],
        },
        "plata": {
            "nombre": "Billetes (200 keplesos)",
            "descripcion": "Un fajo de billetes de Kepler-7: 200 keplesos.",
            "icono": sprites["plata"],
        },
        "boleto": {
            "nombre": "Boleto",
            "descripcion": "Un boleto para entrar a la plataforma de lanzamiento.",
            "icono": sprites["boleto"],
        },
        "cabeza_pico": {
            "nombre": "Cabeza de pico",
            "descripcion": "La parte de metal del pico del minero. No tiene mango.",
            "icono": sprites["cabeza_pico"],
        },
        "palo": {
            "nombre": "Palo",
            "descripcion": "Un palo de madera, derecho y firme. Sirve para armar cosas.",
            "icono": sprites["palo"],
        },
        "cuerda": {
            "nombre": "Cuerda",
            "descripcion": "Una cuerda resistente, de la caja negra.",
            "icono": sprites["cuerda"],
        },
        "cana": {
            "nombre": "Caña rudimentaria",
            "descripcion": "Un palo con una cuerda atada en la punta. Una caña de pescar muy casera.",
            "icono": sprites["cana"],
        },
        "carne": {
            "nombre": "Carne sobrante",
            "descripcion": "Unos recortes de carne que le sobraron al carnicero. Huelen fuerte.",
            "icono": sprites["carne"],
        },
        "cana_cebo": {
            "nombre": "Caña con cebo",
            "descripcion": "La caña rudimentaria con un buen trozo de carne colgando de la cuerda.",
            "icono": sprites["cana_cebo"],
        },
        "pico": {
            "nombre": "Pico",
            "descripcion": "El pico del minero, otra vez con mango. Sirve para picar roca y cristales duros.",
            "icono": sprites["pico"],
        },
        "cristal": {
            "nombre": "Cristal de energía",
            "descripcion": "Un fragmento de cristal que brilla y está tibio. Tiene muchísima energía.",
            "icono": sprites["cristal"],
        },
    }


# Combinaciones de ítems (se hacen desde la mochila):
#   frozenset({"a", "b"}): "resultado"   (frozenset = conjunto sin orden: a + b == b + a)
RECETAS = {
    frozenset({"cabeza_pico", "palo"}): "pico",
    frozenset({"palo", "cuerda"}): "cana",
    frozenset({"cana", "carne"}): "cana_cebo",
}

# Lo que se puede DESARMAR desde la mochila (al revés de las recetas): el palo sirve tanto para el pico como para la
# caña, así que se pueden armar y desarmar.
DESARMES = {
    "pico": ("cabeza_pico", "palo"),
    "cana": ("palo", "cuerda"),
    "cana_cebo": ("cana", "carne"),
}
