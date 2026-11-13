# Encargo: construir un mundo para el proyecto final

Este documento es para una sesión de Claude Code que construye **un** mundo nuevo. Léelo completo antes de escribir código.

## Contexto en cuatro frases

Es el proyecto final de *Introducción a las Ciencias de la Computación* (UNAL Manizales, primer semestre, 34 estudiantes en 9 grupos). Cada grupo recibe un mundo construido por nosotros y programa un agente de búsqueda en tres generaciones: a ciegas, con retroceso y con inferencia. La búsqueda se cuenta en una película 3D con narrador, al estilo de los videos de AI Warehouse. Tu trabajo es construir el mundo; el agente que lo resuelve lo escriben los estudiantes.

## Lee esto primero, en este orden

1. `CONTRATO.md`: las funciones que todo mundo debe ofrecer y las condiciones que debe cumplir.
2. `MANUAL_PILOTO.md`: cómo se construyó la cueva, paso por paso.
3. `mundos/cueva/mundo.py` y `mundos/cueva/casos_cueva.py`: el mundo de referencia cuando un personaje camina.
4. `mundos/hacienda/mundo.py`: el mundo de referencia cuando se deduce una escena (ubicar cosas en casillas).
5. `ejemplo_hacienda/g1_a_ciegas.py` y `g2_con_hilo.py`: las generaciones genéricas. **No las modifiques.**
6. `ejemplo_cueva/g3_rastreador.py`: un ejemplo de generación 3 con reglas como implicaciones.
7. `Recursos/escena.py`: las órdenes disponibles para dibujar.

## Qué entregas

```
mundos/NOMBRE/mundo.py                el mundo, con el contrato completo
mundos/NOMBRE/casos_NOMBRE.py         cuatro niveles como datos, de tamaño creciente
herramientas/generar_casos_NOMBRE.py  cómo se fabricaron y verificaron los niveles
referencia/NOMBRE/g3_NOMBRE.py        la generación 3 de referencia (no se entrega a estudiantes)
referencia/NOMBRE/correr.py           copia del de ejemplo_cueva, apuntando a tu mundo (ver nota)
referencia/NOMBRE/cifras.txt          la salida de `python3 correr.py tabla`
referencia/NOMBRE/NOTAS.md            ver abajo
```

**Nota sobre `correr.py`.** Al copiarlo a `referencia/NOMBRE/`, la raíz del repositorio queda dos niveles arriba: cambia cada `os.path.join(AQUI, "..", ...)` por `os.path.join(AQUI, "..", "..", ...)`, apunta la ruta del mundo a `mundos/NOMBRE`, importa tu G3 y nombra la película `NOMBRE_sala_nivelN.html`.

`NOTAS.md` tiene cuatro secciones cortas: la pregunta de la ficción, las reglas de inferencia de tu G3 escritas como implicaciones, lo que salió mal mientras construías el mundo (verdadero, no inventado), y las piezas visuales que te faltaron (ver «La escena»).

## Condiciones de aceptación

Todas se comprueban corriendo código. No declares el mundo terminado sin haber visto cada una.

1. `python3 correr.py tabla` termina y en los **cuatro** niveles las tres generaciones hallan el mismo número de soluciones (o el mismo óptimo, si el mundo es de optimización).
2. Cada nivel tiene exactamente una solución, comprobado por `generar_casos_NOMBRE.py`, no a ojo.
3. G1 y G2 de `ejemplo_hacienda/` corren sobre tu mundo **sin cambiarles una línea**: solo cambia la ruta que elige el mundo en `correr.py`.
4. Los números cuentan la historia: G1 visita claramente más estados que G2, y G2 tropieza claramente más que G3. Como guía, en el nivel 3 G1 debería ser al menos 5 veces G2 en pasos. Si G1 y G2 dan parecido, el problema está en los niveles (ver la sección 5 del manual), no en el agente.
5. G1 termina en el nivel 1 en menos de 10 segundos. Si deja de terminar en niveles altos, `correr.py tabla` lo dice en vez de colgarse.
6. G3 anota `deducir` o `podar` cada vez que usa una regla, y sus reglas están en el encabezado como implicaciones («Si ..., entonces ...»).
7. `python3 correr.py 3` produce una película que abre sin errores en la consola del navegador. Verifícalo con Playwright (ver abajo) y mira al menos dos capturas: una de G2 a mitad de camino y una de G3 deduciendo.
8. Solo biblioteca estándar de Python 3.9. Identificadores sin tildes; textos en pantalla con tildes y en buen español.

## La escena

- Usa `ambiente="sala"` y una `pared` de un color propio de tu mundo (no repitas azul `#4061B0`, que es la cueva, ni vino `#8f1d30`, que es la hacienda).
- Si alguien camina, ese alguien es Pixie: `e.conejo(f, c)`. Pixie es blanco con una cruz de ceniza en la frente; no le cambies el aspecto. Si tu mundo necesita un segundo personaje, es un conejo **gris**; anótalo en «piezas que faltaron», no lo construyas tú.
- Usa `e.salida` y `e.meta` cuando tenga sentido, `e.hilo(camino)` si hay un camino, y `e.medidor` si algo se gasta (aceite, tiempo, combustible).
- La pantalla es compacta: mientras se reproduce solo se ve lo esencial. No agregues paneles de texto. Si necesitas mostrar pistas (como la hacienda), usa `e.panel` con frases cortas.
- **No edites `Recursos/`** (ni `escena.py`, ni `visor_cine.html`, ni `animar3d.py`). Varias sesiones trabajan a la vez y se pisarían. Si te falta una pieza (un puente, una lámpara, una carpa), dibújala de forma provisional con lo que existe (`mueble` con un tipo nuevo cae en una caja genérica; `caja`, `ficha`, `luz`, `equis`) y descríbela en `NOTAS.md`. El integrador la agrega después.

## El narrador

Escribe un `guion.py` de ejemplo para el nivel 3, con 8 a 10 líneas, en segunda persona, hablándole al agente como un entrenador burlón pero de su lado. No generes voces: eso lo hace el integrador con la voz elegida (Nilton).

## Cómo verificar la película

```bash
cd referencia/NOMBRE && python3 correr.py 3
node -e "
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ args: ['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'] });
  const p = await b.newPage({ viewport: { width: 1300, height: 760 } });
  const errs = []; p.on('pageerror', e => errs.push(String(e)));
  await p.goto('file://' + process.cwd() + '/NOMBRE_sala_nivel3.html'); await p.waitForTimeout(900);
  await p.evaluate(() => { cartel = null; irCap(1); ir(30); }); await p.waitForTimeout(1500);
  await p.screenshot({ path: 'captura_g2.png' });
  await p.evaluate(() => { cartel = null; irCap(2); ir(12); }); await p.waitForTimeout(1500);
  await p.screenshot({ path: 'captura_g3.png' });
  console.log('errores:', JSON.stringify(errs)); await b.close();
})();"
```

Mira las capturas. Si algo se ve mal, corrígelo en tu `dibujar`, no en el visor.

## Los mundos

Elige el que te asignaron. La pregunta de la ficción es lo que la `respuesta` debe contestar.

| Mundo | Pregunta | Tipo | Inferencia esperada en G3 |
|---|---|---|---|
| **La bodega** (cajas, estilo Sokoban) | ¿Cómo despacha Pixie la carga? | camina y empuja | Una caja en una esquina que no es meta pierde el nivel |
| **El cofre** (llaves y puertas) | ¿En qué orden abre Pixie las puertas? | camina | Una llave gastada en la puerta equivocada cierra el camino |
| **El candado** (código con pistas) | ¿Cuál es la clave? | deduce | Cada intento fallido descarta familias de códigos |
| **El vecindario** (la cebra) | ¿Quién tiene el conejo? | deduce | Cada pista es una implicación que se propaga |
| **El puente de noche** | ¿Cruzan todos antes de que se apague la linterna? | optimiza | Si el tiempo que queda no alcanza ni en el mejor caso, se abandona |
| **La mula cafetera** | ¿Qué ruta entrega más café? | optimiza | Si ni el mejor caso supera la mejor ruta hallada, se abandona |
| **La fiesta** (sentar invitados) | ¿Cómo se arma la mesa sin peleas? | deduce | Sentar a uno tacha sillas para sus enemigos |
| **El apagón** (faroles) | ¿Dónde van las lámparas? | deduce | Una lámpara puesta descarta las casillas que alumbra |
| **El campamento** (carpas y árboles) | ¿Dónde armó su carpa cada excursionista? | deduce | Una fila con el cupo lleno deja el resto en pasto |
| **El archipiélago** (puentes) | ¿Cómo se conectan todas las islas? | deduce | Una isla que necesita tantos puentes como vecinas libres los usa todos |
| **La pista de hielo** | ¿Cómo llega Pixie a la salida si solo frena al chocar? | camina | Una casilla desde la que ningún deslizamiento alcanza la meta no se pisa |
| **El trasteo** (encajar muebles) | ¿Cabe todo en el camión? | deduce | Un hueco aislado más pequeño que cualquier mueble pierde la carga |

Para los mundos de optimización, la `respuesta` da el valor óptimo y la condición 1 se lee como «las tres generaciones hallan el mismo óptimo». La mula cafetera tiene datos ya calculados en el material del curso (`fisica_mula.py`, `costos_mula.csv`); si no los tienes, pídelos en vez de inventar cifras.

## Al terminar

Haz un commit con solo los archivos de tu mundo (`mundos/NOMBRE/`, `herramientas/generar_casos_NOMBRE.py`, `referencia/NOMBRE/`) y un mensaje que diga el mundo y las cifras del nivel 3. No toques archivos de otros mundos.
