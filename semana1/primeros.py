# primeros.py  ---  paso 6: los primeros eventos de la generacion 2
# Uso:  python3 semana1/primeros.py MUNDO          (los primeros 12)
#       python3 semana1/primeros.py MUNDO 30       (los primeros 30)
#
# Corre la generacion 2 sobre el nivel 1 y muestra las primeras filas de
# su bitacora. La columna 'pila' dice cuantas decisiones hay tomadas.
import sys
from comun import abrir, nivel_pedido

mundo, nombre = abrir(sys.argv)
cuantos = nivel_pedido(sys.argv, 12)
from bitacora import Bitacora
import g2_con_hilo

EN_PANTALLA = {"avanzar": "avanza", "rechazar": "tropieza", "deducir": "deduce",
               "podar": "poda", "retroceder": "retrocede", "solucion": "SOLUCION"}
caso = mundo.cargar(1)
bit = Bitacora("Generacion 2")
g2_con_hilo.resolver(mundo, caso, bit)

print("evento  pila  que hizo    nota")
numero = 0
for (tipo, estado, nota, pila) in bit.eventos[:cuantos]:
    numero = numero + 1
    print("%5d  %4d  %-10s  %s" % (numero, pila, EN_PANTALLA[tipo], nota))
print("... la bitacora completa tiene %d eventos." % bit.total())
