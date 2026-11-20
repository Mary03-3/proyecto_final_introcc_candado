# conocer.py  ---  paso 3: que mundo nos toco
# Uso:  python3 semana1/conocer.py MUNDO
#
# No resuelve nada. Solo le hace al mundo las primeras preguntas del
# contrato y muestra las respuestas.
import sys
from comun import abrir

mundo, nombre = abrir(sys.argv)
caso = mundo.cargar(1)                      # el nivel 1, el mas pequeno
estado = mundo.inicio(caso)                 # el estado antes de decidir nada
opciones = mundo.opciones(caso, estado)     # lo que se puede decidir ahora

print("MUNDO:", caso["titulo"])
print("NIVELES:", mundo.casos())
print()
print("LO QUE SE SABE DEL NIVEL 1:")
for pista in mundo.pistas(caso):
    print("  -", pista)
print()
print("ESTADO INICIAL:")
print("  ", estado)
print()
print("OPCIONES EN EL ESTADO INICIAL:", len(opciones))
for d in opciones[:3]:
    print("   %-28r %s" % (d, mundo.decir(caso, d)))
if len(opciones) > 3:
    print("   ... y %d mas" % (len(opciones) - 3))
