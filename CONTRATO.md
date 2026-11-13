# El contrato de un mundo

Todo mundo del proyecto es una carpeta `mundos/NOMBRE/` con un `mundo.py` que ofrece estas funciones. El mundo de referencia es `mundos/hacienda/`; el agente de referencia está en `ejemplo_hacienda/`.

| Función | Qué devuelve |
|---|---|
| `casos()` | Los niveles disponibles, del más fácil al más difícil |
| `cargar(nivel)` | El caso: un diccionario con todo lo del nivel |
| `inicio(caso)` | El estado antes de decidir nada |
| `completo(caso, estado)` | `True` si ya no queda nada por decidir |
| `opciones(caso, estado)` | Las decisiones posibles ahora, **sin mirar las reglas** |
| `aplicar(caso, estado, d)` | Un estado **nuevo** con la decisión `d` tomada (no modifica el anterior) |
| `viola(caso, estado)` | `""` si el estado no rompe ninguna regla; si no, la regla rota, en palabras |
| `decir(caso, d)` | La decisión `d`, en palabras, para la nota de la bitácora |
| `respuesta(caso, estado)` | La respuesta a la pregunta de la ficción, cuando el estado es solución |
| `pistas(caso)` | Las reglas o pistas del nivel, en palabras |
| `dibujar(caso, estado)` | La `Escena` en 3D de ese estado (ver `Recursos/escena.py`) |

Además, cada mundo ofrece las consultas propias que un agente necesita para deducir (en la hacienda: `habitacion_de`, `casillas_libres`, `junto_a_mueble`, `cumple`, `choca`). Esas no son parte del contrato común.

## Condiciones que debe cumplir un mundo

1. **Tiene una pregunta de ficción** que solo se responde resolviendo el caso, y `respuesta` la contesta.
2. **Cuatro niveles** de tamaño creciente, guardados como datos en `casos_NOMBRE.py`. Cada nivel tiene **exactamente una solución** (o un único óptimo), comprobado con un programa.
3. **La generación 1 termina en el nivel 1** y deja de terminar en un tiempo razonable hacia el nivel 2 o 3.
4. **El agente genérico funciona sin tocarlo**: `g1_a_ciegas.py` y `g2_con_hilo.py` de `ejemplo_hacienda/` resuelven el nivel 1 del mundo nuevo cambiando solo la línea que elige el mundo.
5. **Existe una generación 3 de referencia** con reglas de inferencia propias del mundo, escritas como implicaciones en el encabezado, que anota `deducir` y `podar`.
6. **Las tres generaciones hallan lo mismo** en todos los niveles donde terminan.
7. **La escena se entiende sola**: quien mire un cuadro pausado ve dónde está cada cosa, qué se está probando y qué se descartó. Los personajes con nombre se mueven solos entre estados.
8. El estado es un diccionario; el agente puede agregarle claves opcionales para la escena (`foco`, `tachadas` en la hacienda) y `dibujar` debe funcionar con y sin ellas.
9. Solo biblioteca estándar de Python 3.9 o posterior. Sin tildes en identificadores; con tildes en todo texto que salga en pantalla.

## Qué se entrega por mundo

```
mundos/NOMBRE/mundo.py             el mundo
mundos/NOMBRE/casos_NOMBRE.py      los cuatro niveles, como datos
herramientas/generar_casos_NOMBRE.py   cómo se fabricaron y verificaron los niveles
referencia/NOMBRE/g3_*.py          la generación 3 de referencia (solo profesor)
referencia/NOMBRE/cifras.txt       tabla de estados, rechazos, deducciones y podas por nivel y generación
```

Si el mundo necesita una pieza 3D que `escena.py` no tiene, se agrega allí y en `visor3d.html` como una orden nueva, sin cambiar las existentes.
