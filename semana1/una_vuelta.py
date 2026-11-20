# una_vuelta.py  ---  paso 5: una sola vuelta del agente, hecha despacio
# Uso:  python3 semana1/una_vuelta.py MUNDO
#
# Toma el estado inicial y prueba CADA opcion una vez: la aplica, pregunta
# si rompe una regla y la deshace. Es el primer piso del arbol de busqueda.
import sys
from comun import abrir

mundo, nombre = abrir(sys.argv)
caso = mundo.cargar(1)
estado = mundo.inicio(caso)
opciones = mundo.opciones(caso, estado)

siguen = 0
tropiezan = 0
MOSTRAR = 12                                # con mas opciones, el resto solo se cuenta
print("Desde el estado inicial hay %d opciones." % len(opciones))
print()
numero = 0
for decision in opciones:
    numero = numero + 1
    nuevo = mundo.aplicar(caso, estado, decision)      # un estado NUEVO; 'estado' no cambia
    falla = mundo.viola(caso, nuevo)
    if falla == "":
        siguen = siguen + 1
        resultado = "SIGUE"
    else:
        tropiezan = tropiezan + 1
        resultado = "TROPIEZA: " + falla
    if numero <= MOSTRAR:
        print("%3d. %s" % (numero, mundo.decir(caso, decision)))
        print("       %s" % resultado)
if len(opciones) > MOSTRAR:
    print("     ... (%d opciones mas, que no se muestran)" % (len(opciones) - MOSTRAR))
print()
print("Siguen %d y tropiezan %d." % (siguen, tropiezan))
print("El estado inicial quedo igual:", estado == mundo.inicio(caso))
