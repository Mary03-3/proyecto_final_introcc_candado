# correr.py  ---  corre las generaciones del agente y arma la pelicula
# Uso:  python3 correr.py          pelicula del nivel 1
#       python3 correr.py 3        pelicula del nivel 3
#       python3 correr.py tabla    la tabla de todos los niveles
import os
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "Recursos"))
sys.path.insert(0, os.path.join(AQUI, "..", "mundos", "hacienda"))     # <- cambiar de mundo es cambiar esta linea

import mundo
from bitacora import Bitacora
from animar3d import animar3d
import g1_a_ciegas
import g2_con_hilo
import g3_detective

GENERACIONES = [
    (g1_a_ciegas, "Generación 1 · a ciegas", "Ubica a todos sin mirar nada y solo al final pregunta si acertó."),
    (g2_con_hilo, "Generación 2 · con hilo", "Revisa las reglas después de cada decisión y se devuelve apenas una falla."),
    (g3_detective, "Generación 3 · detective", "Antes de probar, deduce: tacha las casillas imposibles y ubica primero al más acorralado."),
]

if len(sys.argv) > 1 and sys.argv[1] == "tabla":
    print("%-6s %-26s %10s %10s %10s %8s %8s %10s" % ("nivel", "generacion", "soluciones", "estados", "rechazos", "deduce", "poda", "segundos"))
    for nivel in mundo.casos():
        caso = mundo.cargar(nivel)
        for (g, nombre, _) in GENERACIONES:
            if g is g1_a_ciegas and nivel > 2:
                print("%-6s %-26s %s" % (nivel, nombre, "no termina en un tiempo razonable"))
                continue
            bit = Bitacora(nombre, grabar=False)
            t = time.perf_counter()
            s = g.resolver(mundo, caso, bit)
            c = bit.cuenta
            print("%-6s %-26s %10d %10d %10d %8d %8d %10.2f" % (nivel, nombre, s, c["avanzar"], c["rechazar"],
                                                              c["deducir"], c["podar"], time.perf_counter() - t))
    sys.exit(0)

nivel = int(sys.argv[1]) if len(sys.argv) > 1 else 1
caso = mundo.cargar(nivel)
capitulos = []
for (g, nombre, descripcion) in GENERACIONES:
    bit = Bitacora(nombre)
    if g is g1_a_ciegas and nivel > 1:
        bit.tope = 400                      # en niveles grandes no termina: solo se graba el comienzo
    try:
        soluciones = g.resolver(mundo, caso, bit)
        print("%-28s %d solución, %d eventos" % (nombre, soluciones, bit.total()))
    except StopIteration:
        print("%-28s se detuvo a los %d eventos (no termina)" % (nombre, bit.total()))
    capitulos.append((bit, nombre, descripcion))

animar3d(capitulos, lambda estado: mundo.dibujar(caso, estado),
         os.path.join(AQUI, "pelicula_nivel%d.html" % nivel),
         titulo=caso["titulo"], max_eventos=400,
         pregunta="Cada uno dejó una pista. ¿Quién quedó a solas con el cofre?")
