# Manual del piloto: cómo hicimos la cueva de Pixie

Este manual cuenta, paso por paso, cómo se construyó el ejemplo del curso: un agente que guía a Pixie por una cueva con pozos invisibles, en tres generaciones, contado en una película con narrador. Ustedes harán lo mismo con el mundo que les toque. Cada paso dice qué se escribió, qué se corrió en la terminal y qué salió. También cuenta lo que salió mal en el camino, porque a ustedes les va a pasar algo parecido.

La regla de lectura es sencilla. Todo lo que está en un recuadro gris se escribe tal cual en la terminal, desde la carpeta que se indica. Lo que aparece debajo con la palabra **Sale** es lo que la terminal respondió cuando lo corrimos nosotros.

---

## 0. Qué hace quién

El proyecto tiene dos mitades.

**El mundo lo damos nosotros.** Cada mundo es una carpeta dentro de `mundos/` con sus reglas, sus cuatro niveles y su escena en 3D. Ustedes no tienen que dibujar nada ni saber de gráficos.

**El agente lo escriben ustedes.** El agente es el programa que decide qué hacer: por dónde camina Pixie, cuándo se devuelve y qué deduce. Lo construyen en tres generaciones, y cada una trabaja menos que la anterior. La película muestra esas tres generaciones una tras otra.

El agente habla con el mundo por medio de unas pocas funciones, que llamamos el **contrato**. Como todos los mundos cumplen el mismo contrato, un agente que solo usa esas funciones sirve en cualquier mundo. Esto va a importar en la semana 2.

---

## 1. Preparar el computador

Necesitan Python 3.9 o posterior, git y un navegador (Chrome o Firefox). Para saber si ya tienen Python:

```bash
python3 --version
```

**Sale:** `Python 3.11.4` o algo parecido. Si dice que el comando no existe, en Windows prueben `python --version`; si tampoco existe, instálenlo desde python.org y marquen la casilla *Add Python to PATH*.

Después clonan el repositorio de su equipo (el fork) y entran a la carpeta del ejemplo:

```bash
git clone https://github.com/USUARIO-DEL-EQUIPO/proyecto_final_introcc.git
cd proyecto_final_introcc/ejemplo_cueva
python3 correr.py
```

**Sale:**

```
Generación 1 · a ciegas      soluciones 1 | pasos 486, tropiezos 210, deduce 0, poda 0
Generación 2 · con hilo      soluciones 1 | pasos 68, tropiezos 62, deduce 0, poda 0
Generación 3 · rastreador    soluciones 1 | pasos 15, tropiezos 2, deduce 2, poda 10
Pelicula lista: cueva_sala_nivel3.html (3 capitulos, 520 escenas distintas, 2257 kB). Abrala con doble clic.
  Narrador: 10 lineas, 10 con voz.
```

Abran `cueva_sala_nivel3.html` con doble clic y denle a **Reproducir**. Esa película es lo que ustedes van a entregar, con su propio mundo. Si la ven y la oyen, el computador está listo.

---

## 2. Conocer el mundo antes de programar

Antes de escribir una línea del agente, abrimos el mundo y le hicimos preguntas a mano. Esto se hace en la consola interactiva de Python, desde la carpeta principal del repositorio:

```bash
cd ..
python3
```

Dentro de Python escribimos esto:

```python
import sys
sys.path[:0] = ["Recursos", "mundos/cueva"]
import mundo

caso = mundo.cargar(1)
estado = mundo.inicio(caso)
estado
```

**Sale:** `{'camino': [(5, 1)]}`

Un **estado** de la cueva es un diccionario con el camino que lleva Pixie, en orden. La última casilla es donde está parado. Al empezar, el camino tiene una sola casilla: la entrada, en la fila 5 y la columna 1.

> **Ojo con la numeración.** En el código, filas y columnas se cuentan desde 0, como en las listas de Python. En la pantalla y en el narrador se cuentan desde 1, como las contaría una persona. Por eso la casilla `(4, 1)` del código aparece en pantalla como «fila 5, columna 2».

Luego preguntamos qué puede hacer Pixie desde ahí:

```python
mundo.opciones(caso, estado)
```

**Sale:** `[(4, 1), (5, 2)]`

Hay dos pasos posibles: hacia el norte o hacia el este. `opciones` no revisa ninguna regla; solo dice qué casillas vecinas se pueden pisar. Un pozo también se puede pisar, y ese es el problema.

Dimos un paso y preguntamos si rompía alguna regla:

```python
paso1 = mundo.aplicar(caso, estado, (4, 1))
mundo.viola(caso, paso1)
```

**Sale:** `''`

La cadena vacía quiere decir que nada se rompió. Dimos otro paso hacia el norte:

```python
paso2 = mundo.aplicar(caso, paso1, (3, 1))
mundo.viola(caso, paso2)
```

**Sale:** `'cayó en un pozo'`

Fíjense en que `aplicar` no cambia el estado anterior: devuelve uno **nuevo**. Por eso `paso1` sigue intacto y podemos volver a él. Esa es la base del retroceso: devolverse es simplemente volver a usar el estado de antes.

Por último, preguntamos lo que Pixie percibe:

```python
mundo.brisa(caso, (5, 1)), mundo.brisa(caso, (4, 1))
```

**Sale:** `(False, True)`

En la entrada no hay brisa; un paso al norte, sí. Con esto ya teníamos claras las reglas. Para salir de Python se escribe `exit()`.

### Las funciones del contrato

Estas son todas las funciones que el agente puede usar. Están descritas con detalle en `CONTRATO.md`.

| Función | Qué devuelve |
|---|---|
| `cargar(nivel)` | El caso: todo lo del nivel |
| `inicio(caso)` | El estado antes de decidir nada |
| `completo(caso, estado)` | `True` si ya no queda nada por decidir |
| `opciones(caso, estado)` | Las decisiones posibles ahora, sin mirar las reglas |
| `aplicar(caso, estado, d)` | Un estado **nuevo** con la decisión `d` tomada |
| `viola(caso, estado)` | `""` si nada se rompió; si no, la regla rota, en palabras |
| `decir(caso, d)` | La decisión `d` en palabras, para la película |
| `respuesta(caso, estado)` | La respuesta a la pregunta del mundo, cuando el estado es solución |

Además, cada mundo tiene consultas propias. En la cueva son `vecinas`, `brisa`, `distancia` y `aceite`. Esas no sirven en otros mundos, y solo las usa la generación 3.

---

## 3. El árbol a mano

Antes de programar, dibujamos en papel el árbol de búsqueda del nivel 1. Este es el mapa (`#` roca, `E` entrada, `C` cofre, `O` pozo):

```
#######
#..#C.#
##..#.#
#O.##.#
#.O...#
#E..#.#
#######
```

La raíz del árbol es la entrada. De cada casilla salen tantas ramas como pasos posibles. Cuando una rama cae en un pozo, se marca con una equis y no sigue. Cuando llega al cofre, se marca con un círculo.

Hacer el árbol a mano sirve para dos cosas. La primera es entender el problema sin computador. La segunda es tener un número contra el cual comprobar el programa: los nodos del dibujo, sin contar la raíz, deben coincidir con el contador de pasos de la generación 2 en el nivel 1. A nosotros nos dio 10 pasos y 5 tropiezos.

> **Ojo al dibujarlo.** Pixie no puede volver a una casilla por la que ya pasó en ese mismo camino. Si se olvida esa regla, el árbol no termina nunca. En el código la regla está en `opciones`, que solo ofrece casillas que no estén ya en el camino.

---

## 4. Generación 1: a ciegas

La primera generación camina sin preguntar nada. Solo cuando ya no puede dar más pasos pregunta si sigue vivo. Es lenta a propósito, porque es la línea base contra la que se miden las otras dos.

El archivo es `ejemplo_hacienda/g1_a_ciegas.py`. Está en la carpeta de la hacienda porque lo escribimos para ese mundo primero y después descubrimos que servía igual en la cueva. Esta es la función completa:

```python
def resolver(mundo, caso, bit):
    return generar(mundo, caso, mundo.inicio(caso), bit)


def generar(mundo, caso, estado, bit):
    if mundo.completo(caso, estado):                       # caso base: todo decidido
        falla = mundo.viola(caso, estado)
        if falla == "":
            bit.registrar("solucion", estado, mundo.respuesta(caso, estado))
            return 1
        bit.registrar("rechazar", estado, falla)
        return 0
    total = 0
    for decision in mundo.opciones(caso, estado):
        nuevo = mundo.aplicar(caso, estado, decision)      # decide sin revisar
        bit.registrar("avanzar", nuevo, mundo.decir(caso, decision))
        total = total + generar(mundo, caso, nuevo, bit)
        bit.registrar("retroceder", estado)
    return total
```

Tres cosas hay que entender aquí.

**Es recursiva.** `generar` se llama a sí misma con un estado que tiene un paso más. El caso base es cuando no quedan decisiones.

**La bitácora.** `bit` es una bitácora: cada vez que el agente hace algo, lo anota con `bit.registrar(tipo, estado, nota)`. Es la tabla de seguimiento de clase, pero la escribe el programa. La película se arma a partir de esa bitácora. Solo hay seis tipos de evento:

| Evento | Cuándo se anota |
|---|---|
| `avanzar` | Tomé una decisión y el estado creció |
| `rechazar` | Probé algo y rompe una regla (en pantalla: «tropieza») |
| `deducir` | Sin probar, concluí algo |
| `podar` | Sin probar, concluí que por aquí no hay solución |
| `retroceder` | Deshice la última decisión |
| `solucion` | Llegué y todo se cumple |

**Cada `avanzar` necesita su `retroceder`.** Si falta uno, la pila de la película no vuelve a cero y la revisión automática se queja.

En el nivel 3, esta generación da 486 pasos y 210 tropiezos para hallar una sola solución.

---

## 5. Generación 2: con hilo

La segunda generación cambia una sola cosa: **dónde** pregunta por las reglas. En vez de preguntar al final, pregunta después de cada paso. Si el paso ya rompe una regla, no sigue por ahí.

El archivo es `ejemplo_hacienda/g2_con_hilo.py`. Comparen el ciclo con el de la generación 1:

```python
    for decision in mundo.opciones(caso, estado):
        nuevo = mundo.aplicar(caso, estado, decision)
        falla = mundo.viola(caso, nuevo)                   # pregunta YA
        if falla == "":
            bit.registrar("avanzar", nuevo, mundo.decir(caso, decision))
            total = total + buscar(mundo, caso, nuevo, bit)
            bit.registrar("retroceder", estado)            # el hilo: volver a donde estaba
        else:
            bit.registrar("rechazar", nuevo, falla)
```

La línea `bit.registrar("retroceder", estado)` es el hilo de Ariadna. Cuando la llamada recursiva termina, el programa vuelve a `estado`, que nunca se modificó, y prueba la siguiente opción. En la película se ve como el hilo naranja que se encoge.

En el nivel 3 pasa de 486 pasos a 68. Los tropiezos siguen siendo muchos (62), porque esta generación no tiene memoria: si dos caminos distintos llevan al mismo pozo, cae en los dos.

> **Lo que nos pasó.** La primera versión de la cueva era un laberinto sin ciclos, con un solo camino entre dos casillas cualesquiera. En ese laberinto, la generación 1 y la 2 hacían casi lo mismo, porque caminar a ciegas no explotaba. Tuvimos que rediseñar la cueva con cavernas abiertas y aceite contado para que la diferencia se viera. Si en su mundo las dos primeras generaciones dan números parecidos, el problema puede estar en los niveles y no en su código.

---

## 6. Generación 3: con inferencia

La tercera generación es la única que conoce la cueva. Usa lo que Pixie percibe para **deducir** antes de pisar. Está en `ejemplo_cueva/g3_rastreador.py`.

Lo primero que hicimos fue escribir las reglas de inferencia como implicaciones, en el encabezado del archivo, antes de programarlas:

```
Regla 1 (sin brisa).  Si aquí NO hay brisa, entonces todas las vecinas son seguras.
Regla 2 (la brisa).   Si aquí hay brisa, alguna vecina es un pozo. Si de las vecinas
                      solo UNA no está anotada como segura, el pozo está ahí.
Regla 3 (el aceite).  Si desde una casilla el cofre queda más lejos que los pasos
                      de aceite que sobran, entonces por ahí no se llega.
Regla 4 (la caída).   Si cayó en una casilla, ahí hay un pozo.
```

La regla 2 es un *modus tollens* encadenado con un descarte, como los de la clase de inferencia. La regla 3 es una cota: no prueba nada, solo demuestra que no vale la pena probar.

Lo segundo fue darle al agente una **libreta**: un diccionario con las casillas que sabe seguras y las que sabe que son pozos. La libreta es distinta del estado en algo fundamental. El estado se deshace al retroceder; la libreta no, porque lo que dice es verdad de la cueva. Por eso Pixie aprende de un intento al siguiente.

En el código, cada regla anota su evento:

```python
        if paso in libreta["pozos"]:                                              # Regla 2 o 4
            bit.registrar("podar", foto(estado, libreta), "ahí hay un pozo: no da ese paso")
            continue
        if mundo.distancia(paso, caso["cofre"]) > mundo.aceite(caso, estado) - 1:  # Regla 3
            bit.registrar("podar", foto(estado, libreta), "por ahí no alcanza el aceite")
            continue
```

La función `foto` agrega a la escena dos datos opcionales: `peligro` (los pozos deducidos, que se ven como runas rojas) y `seguras` (que se ven como cuadros verdes). El mundo los dibuja si están y los ignora si no.

En el nivel 3, esta generación da 15 pasos, 2 tropiezos, 2 deducciones y 10 podas.

### La tabla completa

```bash
cd ejemplo_cueva
python3 correr.py tabla
```

**Sale:**

```
nivel  generacion                   soluciones    pasos  tropiezos   deduce   poda
1      Generación 1 · a ciegas               1       94         28        0      0
1      Generación 2 · con hilo               1       10          5        0      0
1      Generación 3 · rastreador             1       10          2        0      3
2      Generación 1 · a ciegas               1      157         60        0      0
2      Generación 2 · con hilo               1       24         15        0      0
2      Generación 3 · rastreador             1       16          2        1     10
3      Generación 1 · a ciegas               1      486        210        0      0
3      Generación 2 · con hilo               1       68         62        0      0
3      Generación 3 · rastreador             1       15          2        2     10
4      Generación 1 · a ciegas               1     2284       1039        0      0
4      Generación 2 · con hilo               1       36         26        0      0
4      Generación 3 · rastreador             1       20          1        3     14
```

Lo primero que se mira en esta tabla es la columna **soluciones**. Las tres generaciones deben encontrar lo mismo en todos los niveles. Si una generación corre más rápido porque pierde soluciones, la poda está mal y no vale. Es el error más fácil de cometer en la generación 3.

> **Cuidado con la libreta.** Si la libreta se copiara en cada llamada recursiva, como el estado, el programa seguiría funcionando, pero Pixie olvidaría todo al retroceder y caería dos veces en el mismo pozo, igual que la generación 2. Por eso todas las llamadas reciben la misma libreta, sin copiarla. Distinguir qué se deshace al retroceder y qué no es la decisión más importante de la generación 3.

---

## 7. La película

`correr.py` hace tres cosas: corre las tres generaciones sobre el mismo nivel, guarda la bitácora de cada una y le pasa las tres a `animar3d`, que escribe la película.

```bash
python3 correr.py          # el nivel del guion (3), con narrador
python3 correr.py 2        # otro nivel, sin narrador
python3 correr.py cueva    # el mismo nivel con la cueva oscura
```

La película tiene una portada, un capítulo por generación y una tabla final. Mientras se reproduce, la pantalla muestra poco a propósito: el nombre de la generación, los dos contadores de la pared, el aceite y lo que dice el narrador.

**Al pausar aparece el detalle**: el título, el número de evento, la pila y los contadores de deducciones y podas. El número de evento es el que van a necesitar para el guion y para la sustentación.

Las figuras translúcidas que van quedando son los **fantasmas**: las casillas por donde Pixie ya pasó en ese capítulo. Las blancas siguen en el camino actual; las rojas son ramas de donde se devolvió. Al final de la generación 1 hay muchas rojas, y al final de la 3, casi ninguna. Esa diferencia es lo que se ve de la búsqueda.

Los botones que importan:

| Botón | Para qué |
|---|---|
| Reproducir / Pausar | También con la barra espaciadora |
| ◀ Paso / Paso ▶ | Un evento atrás o adelante (también con las flechas) |
| Al azar | Salta a un evento cualquiera y pausa. Es el que se usa en la sustentación |
| Grabar video | Reproduce todo desde la portada y descarga un video con la voz |

---

## 8. El guion del narrador

El narrador es la voz que comenta la película. Lo escribe el equipo en `guion.py`, y es donde se nota si entendieron lo que hace su agente.

Para escribir cada línea hicimos esto:

1. Reproducir la película y pausar donde pasa algo que vale la pena explicar: una caída, una deducción, el momento en que llega.
2. Mirar el número del evento abajo a la izquierda, por ejemplo «evento 12 de 45».
3. Escribir qué hizo el agente ahí y **por qué**.

Cada línea del guion es `(capítulo, evento, texto)`. El capítulo se cuenta desde 1 y el evento 0 es el comienzo del capítulo. Estas son algunas líneas del nuestro:

```python
GUION = [
    (1, 0, "Hola, Pixie. No sabes nada de esta cueva, así que camina. Ya veremos qué pasa cuando se te apague el farol."),
    (2, 14, "Pixie... ¿otra vez? Tienes hilo, pero no tienes memoria."),
    (3, 12, "¿Sientes la brisa? Solo te queda una casilla vecina sin revisar. El pozo tiene que estar ahí."),
    (3, 14, "Eso. No diste el paso, y lo supiste sin caer."),
]
```

**El tono.** El narrador le habla al agente de tú, como un entrenador: burlón cuando se equivoca, pero de su lado. Lo tomamos de los videos de AI Warehouse, que fueron el referente del proyecto. Un narrador de documental («Pixie avanza hacia el norte») cuenta lo que ya se ve. El que sirve explica lo que no se ve: por qué el agente hizo eso.

**La longitud.** Diez líneas para tres capítulos fue suficiente. Cada línea de más alarga la película, porque la acción se detiene mientras el narrador habla.

> **Lo que nos pasó.** La primera versión del guion hablaba de Pixie en tercera persona y sonaba a documental; la reescribimos de tú. Y una advertencia: los números de evento dependen del nivel y del agente. **Si cambian cualquiera de los dos, el narrador va a hablar en el momento equivocado, así que revisen el guion.**

---

## 9. Las voces con ElevenLabs

El narrador puede quedarse en texto, pero con voz la película cambia mucho. Las voces se generan con ElevenLabs.

### Paso 9.1: la lista de frases

```bash
python3 correr.py guion
```

**Sale:** `Guion escrito en .../ejemplo_cueva/voces/guion.txt`

Ese archivo tiene cada frase con el nombre exacto que debe llevar su audio:

```
g1_e000.mp3
    Hola, Pixie. No sabes nada de esta cueva, así que camina. ...

g3_e012.mp3
    ¿Sientes la brisa? Solo te queda una casilla vecina sin revisar. ...
```

`g3_e012` quiere decir capítulo 3, evento 12.

### Paso 9.2: generar cada frase

Hay dos maneras.

**En la página de ElevenLabs**: entran a *Text to Speech*, eligen una voz, pegan la frase, generan y descargan el MP3. Le cambian el nombre al que dice `guion.txt` y lo guardan en la carpeta `voces/`.

**Con Claude y el conector de ElevenLabs**: le dan el `guion.txt` y le piden que genere cada frase con una voz y guarde los archivos con esos nombres. Así lo hicimos nosotros.

### Paso 9.3: elegir la voz

Escojan la voz oyendo, no leyendo. Las descripciones engañan: la primera voz que elegimos decía «profesional y agradable» y sonó a otra cosa. Lo que funcionó fue generar **una sola frase** con tres voces distintas, oírlas, elegir y solo entonces generar las diez. Nosotros usamos la voz **Nilton**.

Una frase cuesta entre 30 y 110 créditos, según lo larga que sea. Por defecto se generan dos tomas por frase, y las dos cuestan.

### Paso 9.4: volver a armar la película

```bash
python3 correr.py
```

**Sale:** `Narrador: 10 lineas, 10 con voz.`

Si dice menos voces que líneas, a alguna frase le falta el audio o tiene mal el nombre. Los audios quedan metidos dentro del archivo `.html`, así que la película funciona sola, sin la carpeta.

> **Lo que nos pasó.** En la vista previa de un chat la película no sonó. Si no la oyen, descárguenla y ábranla con doble clic en Chrome antes de buscar el error en el código.

---

## 10. Grabar el video

Con la película abierta en Chrome o Firefox, el botón **Grabar video** vuelve a la portada, reproduce todo a la velocidad elegida y, al final, descarga un archivo `.webm` con la imagen y la voz. Si el video sale muy largo, suban la velocidad antes de grabar. Si necesitan MP4, los editores de video y los conversores en línea lo hacen.

---

## 11. Lista de chequeo antes de entregar

- `python3 correr.py tabla` corre sin errores y las tres generaciones hallan lo mismo en los cuatro niveles.
- Los nodos del árbol a mano del nivel 1, sin contar la raíz, coinciden con los pasos de la generación 2.
- Cada regla de la generación 3 está escrita como implicación en el encabezado del archivo.
- La generación 3 anota `deducir` o `podar` cada vez que usa una regla.
- El guion tiene entre 8 y 12 líneas, le habla al agente, y cada línea explica un por qué.
- La película suena descargada y abierta con doble clic.
- Cualquiera del equipo puede pausar en un evento al azar y explicar qué hizo el agente ahí.

---

## 12. La IA en este proyecto

Este piloto se hizo con ayuda de Claude, y así lo pueden hacer ustedes. Lo que no se delega es entender. Tres cosas que nos sirvieron:

- **Pedirle que explique antes que pedirle código.** «¿Por qué mi generación 2 da los mismos números que la 1?» enseña más que «escríbeme la generación 2».
- **Comprobar todo con la tabla.** Cuando la IA propone una regla de inferencia, la tabla dice si pierde soluciones. Es la prueba más rápida y la más honesta.
- **Anotar en la bitácora de IA** qué le pidieron, qué respondió y cómo lo comprobaron. En la sustentación se pregunta por la última columna.
