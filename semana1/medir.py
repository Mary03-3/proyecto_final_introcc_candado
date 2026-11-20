# medir.py  ---  paso 7: las dos generaciones, en numeros
# Uso:  python3 semana1/medir.py MUNDO
#
# Corre la generacion 1 y la generacion 2 sin grabar la pelicula y cuenta.
# La generacion 1 solo se corre en los niveles 1 y 2: en los niveles altos
# de algunos mundos tarda demasiado.
import sys
import time
from comun import abrir

mundo, nombre = abrir(sys.argv)
from bitacora import Bitacora
import g1_a_ciegas
import g2_con_hilo

print("%-6s %-24s %10s %9s %10s %9s" % ("nivel", "generacion", "soluciones", "pasos", "tropiezos", "segundos"))
for nivel in mundo.casos():
    caso = mundo.cargar(nivel)
    for (agente, titulo) in ((g1_a_ciegas, "Generacion 1 · a ciegas"), (g2_con_hilo, "Generacion 2 · con hilo")):
        if agente is g1_a_ciegas and nivel > 2:
            continue
        bit = Bitacora(titulo, grabar=False)            # grabar=False: solo cuenta
        antes = time.time()
        soluciones = agente.resolver(mundo, caso, bit)
        segundos = time.time() - antes
        print("%-6s %-24s %10d %9d %10d %9.1f" % (nivel, titulo, soluciones, bit.cuenta["avanzar"],
                                                 bit.cuenta["rechazar"], segundos))
