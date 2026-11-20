# pelicula.py  ---  paso 9: la primera pelicula del mundo del equipo
# Uso:  python3 semana1/pelicula.py MUNDO          (nivel 1)
#       python3 semana1/pelicula.py MUNDO 2        (otro nivel)
#
# Dos capitulos: la generacion 1 y la generacion 2, sobre el mismo nivel.
# Todavia no hay narrador ni generacion 3: eso llega en las semanas 3 y 4.
# La pelicula queda en la carpeta equipo/.
import os
import sys
from comun import abrir, nivel_pedido, RAIZ

mundo, nombre = abrir(sys.argv)
nivel = nivel_pedido(sys.argv, 1)
from bitacora import Bitacora
from animar3d import animar3d
import g1_a_ciegas
import g2_con_hilo

EQUIPO = os.path.join(RAIZ, "equipo")
if not os.path.isdir(EQUIPO):
    print("No existe la carpeta equipo/. Hagan primero el paso 8 de la guia.")
    sys.exit(1)

caso = mundo.cargar(nivel)
capitulos = []
for (agente, titulo, descripcion, ritmo) in (
        (g1_a_ciegas, "Generación 1 · a ciegas", "Decide todo y solo al final pregunta si rompió una regla.", 25),
        (g2_con_hilo, "Generación 2 · con hilo", "Pregunta después de cada decisión y se devuelve apenas algo falla.", 8)):
    bit = Bitacora(titulo)
    soluciones = agente.resolver(mundo, caso, bit)
    print("%-26s soluciones %d | pasos %d, tropiezos %d" % (titulo, soluciones, bit.cuenta["avanzar"], bit.cuenta["rechazar"]))
    capitulos.append((bit, titulo, descripcion, ritmo))
animar3d(capitulos, lambda estado: mundo.dibujar(caso, estado),
         os.path.join(EQUIPO, "%s_nivel%d.html" % (nombre, nivel)),
         titulo=caso["titulo"], max_eventos=1300)
