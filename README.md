# Varado en Kepler — Aventura gráfica espacial en estilo 16 bits

Tu cápsula de escape se estrelló en un planeta rojo. Para volver a casa tenés que
reactivar a un robot minero, conseguir un cristal de energía en una cueva oscura
y hacer despegar un cohete abandonado.

## Cómo ejecutarlo
1. Instalar pygame (con Python 3.14 usar pygame-ce):
   `python -m pip install pygame-ce`
2. Desde esta carpeta (la que tiene `jugar.py`):
   `python jugar.py`

## Controles
| Acción | Cómo |
|---|---|
| Caminar | Clic izquierdo en el piso |
| Elegir verbo | Clic en **Mirar**, **Coger**, **Usar** o **Hablar** |
| Usar el verbo | Con el verbo elegido, clic en un objeto |
| Cambiar de escenario | Clic en las flechas amarillas de los bordes |
| Abrir la mochila | Botón **Mochila** o tecla **I** |
| Combinar ítems | En la mochila: clic en un ítem y después en otro |
| Usar un ítem en algo | En la mochila: elegir ítem → **Usar** → clic en el objeto |
| Elegir en un diálogo | Clic en la opción o teclas 1, 2, 3... |
| Cancelar verbo o ítem | Clic derecho |
| Ver zonas caminables | **F1** |
| Pantalla completa | **F11** |
| Volver al menú | **Esc** |

## Hoja de sprites (texturas y sprites)
Los personajes, los ítems, las texturas y los objetos grandes de los escenarios
(cápsula, caja, compuerta, cohete, consola, cartel, flechas) están en una sola imagen:
`kepler/assets/hoja_sprites.png`. Al lado está `hoja_sprites.json`, que guarda
el nombre y la posición `[x, y, ancho, alto]` de cada sprite.

Los **fondos** de cada escenario son imágenes aparte, porque son grandes y no se
repiten: `kepler/assets/fondos/choque.png`, `cueva.png` y `plataforma.png`.

- **Retocar los gráficos:** abrir el PNG con un programa de pixel art (Aseprite,
  Piskel, GIMP...) y editarlo sin cambiar el tamaño ni la posición de cada dibujo.
  El juego lo carga solo.
- **Regenerar los assets** a partir de los dibujos de código (`kepler/sprites.py`
  y `kepler/arte.py`): `python -m kepler.generar_hoja`. Arma la hoja y los fondos.
  **Ojo:** esto pisa lo que hayas editado en esos PNG.
- Los efectos que se mueven (luces que titilan, líneas de la consola, la flecha) no
  están en la hoja: se dibujan encima en cada cuadro.
- Si se borra la carpeta `assets/`, el juego vuelve a dibujar todo con código, y los fondos con el código de cada escenario.
- Las texturas de los pisos (`textura_suelo_marte`, `textura_suelo_cueva`,
  `textura_piso_metal`) miden 16x16 y se repiten como baldosas con `rellenar_textura`.

## Solución
1. **Sitio del choque:** Usar la caja → Coger la batería → Coger el cable →
   en la mochila combinar batería + cable → Usar la batería con cable en el robot.
2. Hablar con el robot: preguntar "¿Cómo salgo de este planeta?" y después
   "¿Dónde consigo un cristal?" (te da el código 4-7-1 y la linterna).
   "¿De qué planeta vengo?" da la pista del final.
3. **Cueva** (flecha derecha): Usar la compuerta → Usar la linterna en la compuerta →
   Coger el cristal.
4. **Plataforma** (desde el sitio del choque, flecha izquierda): Usar el cristal en el
   cohete → Usar la consola → elegir **AZUL-3**.

## Requisitos del enunciado
| Requisito | Dónde está |
|---|---|
| Interfaz point-and-click con verbos | `kepler/estados/jugando.py` (Mirar, Coger, Usar, Hablar) |
| Inventario para guardar y combinar | `engine/inventario.py` + `kepler/estados/inventario.py` |
| 3 escenarios interconectados con zonas navegables | `kepler/escenas/` (choque, cueva, plataforma) + `engine/navegacion.py` |
| Diálogos con opciones múltiples con NPCs | `engine/dialogo.py` + `kepler/dialogos.py` (robot R-7) |
| Al menos 2 puzles | 3 puzles: robot, compuerta/cueva, cohete/consola |
| Máquina de estados finitos | `engine/juego.py` + `engine/estado.py` (MENU, JUGANDO, INVENTARIO, DIALOGO, FINAL) |
| Polígonos de navegación | `engine/navegacion.py` (ray casting) |

## Estructura
```
proyecto_kepler/
├── jugar.py                 -> arranca el juego
├── engine/                  -> MOTOR: genérico, sirve para cualquier aventura gráfica
│   ├── juego.py             -> ventana pixelada (320x200), bucle y máquina de estados
│   ├── estado.py            -> clase base de los estados
│   ├── navegacion.py        -> polígono caminable (ray casting)
│   ├── actor.py             -> personaje que camina y habla (QUIETO / CAMINANDO)
│   ├── escena.py            -> escenario y objetos con respuestas a cada verbo
│   ├── inventario.py        -> inventario con recetas para combinar
│   ├── dialogo.py           -> árboles de diálogo con opciones
│   ├── pixelart.py          -> sprites dibujados con letras
│   ├── spritesheet.py       -> hoja de sprites (PNG + JSON), recortes y texturas repetidas
│   └── ui.py                -> botones, paneles, textos pixelados
└── kepler/                  -> JUEGO: el contenido concreto
    ├── main.py              -> clase VaradoEnKepler(Juego)
    ├── config.py            -> resolución, colores, progreso de la historia
    ├── sprites.py           -> astronauta, robot, ítems y texturas en pixel art
    ├── generar_hoja.py      -> arma assets/hoja_sprites.png desde sprites.py
    ├── assets/              -> hoja_sprites.png + hoja_sprites.json
    ├── items.py             -> catálogo de ítems y recetas
    ├── arte.py              -> dibujos de los objetos grandes (cápsula, cohete...)
    ├── protagonista.py      -> Astronauta(Actor)
    ├── dialogos.py          -> charla con el robot y la consola
    ├── escenas/             -> choque.py, cueva.py, plataforma.py
    └── estados/             -> menu, jugando, inventario, dialogo, final
```

**Regla:** `engine/` nunca importa nada de `kepler/`. El juego usa al motor, el motor no conoce al juego.
