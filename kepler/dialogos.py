"""
kepler/dialogos.py
Los árboles de diálogo del juego, armados con Dialogo, Nodo y Opcion del engine.

Se crean con una función cada vez que empieza una charla, así siempre
arrancan desde el principio y las condiciones se evalúan con el progreso actual.
"""

from engine import Dialogo, Nodo, Opcion
from kepler.glifos import glifos

CODIGO_COMPUERTA = "471"      # el código de la compuerta de la mina (dígitos; en pantalla se ve con símbolos)


def dialogo_robot(juego):
    """Charla con R-7, el robot de la mina: dice para qué sirve y, si le preguntás, la contraseña de la compuerta."""
    progreso = juego.progreso

    # ---- Acción que se ejecuta al elegir la opción de la mina ----
    def saber_codigo():
        progreso["sabe_codigo"] = True       # (la linterna no se da sola: hay que agarrarla del pecho de R-7)

    opciones = [
        Opcion("¿Cuál es tu función?", "funcion"),
        # La primera vez, además del código, dice dónde está la linterna; después, solo repite el código
        # Recién después de preguntarle cómo se consiguen keplesos (los cristales de la mina)
        Opcion("¿Cómo puedo entrar a la mina?", "mina",
               condicion=lambda: progreso["pregunto_keplesos"] and not progreso["sabe_codigo"], accion=saber_codigo),
        Opcion("¿Cómo puedo entrar a la mina?", "mina_otra_vez",
               condicion=lambda: progreso["pregunto_keplesos"] and progreso["sabe_codigo"]),
        Opcion("¿Sabes cómo salir de este planeta?", "salida"),
        # Aparece después de hablar con el boletero (ahí se entera de que el boleto cuesta plata)
        Opcion("¿Cómo consigo keplesos?", "keplesos", condicion=lambda: progreso["hablo_con_boletero"],
               accion=lambda: progreso.__setitem__("pregunto_keplesos", True)),
        # Después de preguntarle al boletero a qué planeta ir (ya con el boleto): R-7 la escanea
        Opcion("¿De qué planeta soy?", "escaner", condicion=lambda: progreso["pregunto_planeta"]),
        Opcion("Te pareces mucho a Wall-E.", "walle"),
        Opcion("Nada, gracias. Chau.", None),
    ]

    nodos = {
        "inicio": Nodo("R-7", "¡Sistemas en línea! Gracias por las monedas, astronauta. ¿En qué te ayudo?",
                       opciones),
        "menu": Nodo("R-7", "¿Algo más, astronauta?", opciones),
        "funcion": Nodo("R-7", "Soy un robot que ayudaba en la mina, con IA asistente integrada.",
                        siguiente="menu"),
        "mina": Nodo("R-7", "Al costado de la puerta tenés un tablero para poner un código. "
                            f"Llevo tiempo apagado, pero la contraseña era {glifos(CODIGO_COMPUERTA)}.",
                     siguiente="pecho"),
        "pecho": Nodo("R-7", "En mi pecho hay un compartimiento con una linterna. Agarrala, porque está oscuro.",
                      siguiente="menu"),
        "mina_otra_vez": Nodo("R-7", f"La contraseña era {glifos(CODIGO_COMPUERTA)}.", siguiente="menu"),
        "salida": Nodo("R-7", "A la izquierda hay una plataforma, si mal no recuerdo.", siguiente="menu"),
        "keplesos": Nodo("R-7", "Los cristales de esta mina se venden a buen precio en el mercado.", siguiente="menu"),
        "escaner": Nodo("R-7", "Escaneando... Listo. Sos del planeta azul.", siguiente="menu"),
        "walle": Nodo("R-7", "¿A quién?", siguiente="menu"),
    }

    inicio = "menu" if progreso["hablo_con_robot"] else "inicio"
    progreso["hablo_con_robot"] = True
    return Dialogo(nodos, inicio)


def en_alien(jerga, traduccion):
    """El minero habla en alien; la traducción va entre paréntesis."""
    return f"{jerga} ({traduccion})"


def alien(traduccion):
    """Arma una jerga alien (Zip, zap, zup...) con más o menos tantas palabras como el texto, y le pone la traducción."""
    palabras = traduccion.split()
    silabas = ("zip", "zap", "zup", "zip", "zup", "zap", "zap", "zip")
    n = max(1, round(len(palabras) * 0.8))
    jerga = " ".join(silabas[(i * 3 + len(traduccion)) % len(silabas)] for i in range(n))
    jerga = jerga[0].upper() + jerga[1:]
    if traduccion.rstrip().endswith("?"):
        jerga += "?"
    elif traduccion.rstrip().endswith("!"):
        jerga += "!"
    return en_alien(jerga, traduccion)


def en_jerga(nodos, excepto=("...",)):
    """Hace que todo lo que dicen los nodos salga en jerga alien con la traducción (menos los silencios)."""
    for nodo in nodos.values():
        if nodo.texto not in excepto:
            nodo.texto = alien(nodo.texto)
    return nodos


def dialogo_minero(juego):
    """Charla con el minero: está de vago en su silla, contesta lo justo y habla en español."""
    progreso = juego.progreso
    ya_hablo = progreso["hablo_con_minero"]
    estado = {"saludo": False}          # el "Hola." se ofrece solo una vez, al empezar

    def saludar():
        estado["saludo"] = True

    opciones = [
        Opcion("Hola.", "hola", condicion=lambda: not ya_hablo and not estado["saludo"], accion=saludar),
        Opcion("¿Por qué no estás minando?", "minando"),
        Opcion("¿Sabes la clave de la mina?", "clave"),
        Opcion("¿Estás descansando?", "descanso"),
        # La astronauta solo se interesa por el pico después de comprobar que el cristal es
        # demasiado duro; y deja de tener sentido pedirlo si ya lo tiene o ya sacó el fragmento.
        Opcion("¿Me prestás tu pico?", "pico",
               condicion=lambda: (progreso["intento_romper_cristal"] and not progreso["pico_dado"]
                                  and not progreso["cristal_minado"])),
        Opcion("Nos vemos.", "chau"),
    ]

    nodos = {
        "inicio": Nodo("Minero", "...", opciones),
        "menu": Nodo("Minero", "¿Algo más?", opciones),
        "hola": Nodo("Minero", "Hola.", siguiente="menu"),
        "minando": Nodo("Minero", "¿Acaso sos mi jefe?", siguiente="menu"),
        "clave": Nodo("Minero", "Ni idea, me mataste.", siguiente="menu"),
        "descanso": Nodo("Minero", "Sí, estoy haciendo el pomodoro invertido: 5 minutos de trabajo, 1 hora de descanso.",
                         siguiente="menu"),
        "pico": Nodo("Minero", "Ya que sos terrícola, ¿no tendrías una coca de 3 litros? "
                               "Si me conseguís una, te doy la cabeza del pico.",
                     siguiente="menu"),
        "chau": Nodo("Minero", "Nos vemos."),
    }
    en_jerga(nodos)

    inicio = "menu" if ya_hablo else "inicio"
    progreso["hablo_con_minero"] = True
    return Dialogo(nodos, inicio)


def dialogo_mercader(juego):
    """Charla con la mercader en su puesto, ya rescatada de la playa."""
    progreso = juego.progreso
    ya_hablo = progreso["hablo_con_mercader"]
    estado = {"saludo": False}          # el "Buenas." se ofrece solo la primera vez

    def saludar():
        estado["saludo"] = True

    opciones = [
        Opcion("Buenas.", "buenas", condicion=lambda: not ya_hablo and not estado["saludo"], accion=saludar),
        Opcion("¿Qué vendes?", "vende"),
        Opcion("¿Y ese perro de dónde salió?", "perro"),
        Opcion("La del puesto de al lado es mala onda.", "vecina"),
        Opcion("Solo estaba viendo, gracias.", None),
    ]

    nodos = {
        "inicio": Nodo("Mercader", "¿Qué necesitás?", opciones),
        "menu": Nodo("Mercader", "¿Algo más?", opciones),
        "buenas": Nodo("Mercader", "Gracias por la ayuda, forastero.", siguiente="menu"),
        "vende": Nodo("Mercader", "Compro y vendo cristales de energía, principalmente.", siguiente="menu"),
        "perro": Nodo("Mercader", "No sé, fui a tomarme un descanso a la playa y apareció de repente. "
                                  "Pensé que no la contaba.",
                      siguiente="menu"),
        "vecina": Nodo("Mercader", "Sí, es bastante mala gente.", siguiente="menu"),
    }
    en_jerga(nodos)

    progreso["hablo_con_mercader"] = True
    return Dialogo(nodos, "inicio")


def dialogo_frutero(juego):
    """El frutero del puesto de al lado no quiere clientes: solo te echa. La segunda vez, más seco."""
    progreso = juego.progreso
    if not progreso["hablo_con_frutero"]:
        texto = en_alien("Zap zup zip zap zup zap", "No tenés estómago para estas frutas. Largo de aquí.")
    else:
        texto = en_alien("Zup zap zap!", "Te dije largo.")
    progreso["hablo_con_frutero"] = True
    return Dialogo({"inicio": Nodo("Frutero", texto)}, "inicio")


def dialogo_carnicero(juego):
    """Charla con el carnicero: vende carne, pero no regala nada."""
    progreso = juego.progreso

    opciones = [
        Opcion("¿Qué vendes?", "vende"),
        Opcion("¿Me das un trozo de carne?", "trozo"),
        Opcion("Solo estaba viendo, gracias.", None),
    ]

    nodos = {
        "inicio": Nodo("Carnicero", "¿Qué querés?", opciones),
        "menu": Nodo("Carnicero", "¿Algo más?", opciones),
        "vende": Nodo("Carnicero", "Carnes de todo tipo.", siguiente="menu"),
        "trozo": Nodo("Carnicero", "No hago caridad, me tenés que dar algo a cambio.", siguiente="menu"),
    }
    en_jerga(nodos)

    progreso["hablo_con_carnicero"] = True
    return Dialogo(nodos, "inicio")


def dialogo_boletero(juego):
    """Charla con el boletero (el alien del bigote): pregunta lo que quieras, contesta seco y con mala onda."""
    progreso = juego.progreso

    opciones = [
        Opcion("¿Qué es esto?", "esto"),
        Opcion("¿Cuánto sale el boleto?", "precio"),
        Opcion("¿Qué estás tomando?", "mate"),
        Opcion("¿Cuándo sale el cohete?", "cohete"),
        # Recién cuando ya tiene el boleto: ¿a qué planeta tiene que ir?
        Opcion("¿A qué planeta debería ir?", "planeta", condicion=lambda: progreso["compro_boleto"],
               accion=lambda: progreso.__setitem__("pregunto_planeta", True)),
        Opcion("Solo estaba viendo, gracias.", None),
    ]

    nodos = {
        "inicio": Nodo("Boletero", "¿Qué querés?", opciones),
        "menu": Nodo("Boletero", "¿Algo más?", opciones),
        "esto": Nodo("Boletero", "Una boletería, ¿acaso no sabes leer?", siguiente="menu"),
        "precio": Nodo("Boletero", "200 keplesos, pibe. Ni más ni menos.", siguiente="menu"),
        "mate": Nodo("Boletero", "Mate. Me lo trajo un terrícola una vez y me enganché. "
                                 "Me bajo 15 termos al día.",
                     siguiente="menu"),
        "cohete": Nodo("Boletero", "Es individual: cuando pagues, se va.", siguiente="menu"),
        "planeta": Nodo("Boletero", "Ni idea, no sé de dónde sos.", siguiente="menu"),
    }

    progreso["hablo_con_boletero"] = True
    return Dialogo(nodos, "inicio")


def dialogo_mercader_acorralada(juego):
    """Se le grita a la mercader desde lo alto del barranco: está acorralada por el perro alien."""
    progreso = juego.progreso
    if not progreso["mercader_pidio_ayuda"]:
        texto = en_alien("¡Zip zap zup zup!", "¡Por favor, ayudame! Este bicho no me deja salir de acá.")
    else:
        texto = en_alien("¡Zup zup zap!", "¡No me dejes sola con esta bestia!")
    progreso["mercader_pidio_ayuda"] = True
    return Dialogo({"inicio": Nodo("Mercader", texto)}, "inicio")


def dialogo_mercader_rescatada():
    """La mercader, libre del perro, agradece y se vuelve a su puesto."""
    texto = en_alien("¡Zup zap zip zup zap zip!", "¡Gracias, gracias! Me vuelvo a mi puesto. Pasá a verme cuando quieras.")
    return Dialogo({"inicio": Nodo("Mercader", texto)}, "inicio")


def dialogo_carnicero_trueque():
    """El carnicero cambia unos recortes de carne por la billetera vacía (nunca había visto una)."""
    texto = alien("Uh, interesante, nunca vi una de estas. Te la acepto.")
    return Dialogo({"inicio": Nodo("Carnicero", texto)}, "inicio")


def dialogo_mercader_compra():
    """Charla corta cuando le vendés el cristal de energía al mercader."""
    texto = en_alien("Zup zap zup zup zip zap",
                     "¡Un cristal de energía! Excelente calidad. Tomá, son 200 keplesos. Hecho el trato.")
    return Dialogo({"inicio": Nodo("Mercader", texto)}, "inicio")


def dialogo_minero_recibe_coca():
    """Charla corta cuando le das la coca al minero."""
    texto = en_alien("Zip zup zup zap... ¡glup, glup, glup! ...zap zip",
                     "Ahhh, qué rico. Trato es trato: tomá la cabeza de mi pico.")
    return Dialogo({"inicio": Nodo("Minero", texto)}, "inicio")


def dialogo_minero_recibe_pico(lo_uso):
    """
    Charla cuando intentás devolverle el pico al minero.
    Si todavía no lo usaste (no tenés el fragmento), no lo acepta.
    """
    if lo_uso:
        texto = en_alien("Zap zip zup zip?",
                         "¿Ya lo usaste? ¡Perfecto! Gracias por devolvérmelo, astronauta.")
    else:
        texto = en_alien("Zap zip zup zip?",
                         "¿Ya lo usaste? No parece. Quedátelo y devolvémelo cuando termines.")
    return Dialogo({"inicio": Nodo("Minero", texto)}, "inicio")


def dialogo_consola(juego):
    """La consola usa el mismo sistema de diálogos para elegir el destino (puzle final)."""
    def destino_equivocado(destino):
        return lambda: juego.perder_partida(
            "Elegiste un destino equivocado. El cohete te dejó en cualquier lado.", destino)

    destinos = [
        Opcion("ROJO-1", None, accion=destino_equivocado("ROJO-1")),
        Opcion("AZUL-3", None, accion=juego.terminar_partida),   # el correcto: termina el juego
        Opcion("VERDE-2", None, accion=destino_equivocado("VERDE-2")),
        Opcion("Cancelar", None),
    ]
    nodos = {
        "inicio": Nodo("Consola", "COHETE LISTO. SELECCIONE DESTINO:", destinos),
    }
    return Dialogo(nodos, "inicio")
