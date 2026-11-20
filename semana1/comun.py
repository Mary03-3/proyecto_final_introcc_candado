# comun.py  ---  lo que comparten los programas de la semana 1
#
# Cada programa de esta carpeta se corre desde la carpeta principal del
# repositorio y recibe el nombre de la carpeta del mundo:
#     python3 semana1/conocer.py bodega
# Esta funcion busca el mundo, lo importa y lo devuelve.
import os
import sys

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
MUNDOS = sorted(os.listdir(os.path.join(RAIZ, "mundos")))


def abrir(argumentos):
    """Devuelve (mundo, nombre) segun lo escrito en la terminal."""
    if len(argumentos) < 2 or argumentos[1] not in MUNDOS:
        print("Falta el nombre del mundo. Por ejemplo:")
        print("    python3 %s bodega" % argumentos[0])
        print("Los mundos son: " + ", ".join(MUNDOS))
        sys.exit(1)
    nombre = argumentos[1]
    sys.path.insert(0, os.path.join(RAIZ, "Recursos"))           # el motor
    sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))   # las generaciones 1 y 2
    sys.path.insert(0, os.path.join(RAIZ, "mundos", nombre))     # <- el mundo
    import mundo
    return mundo, nombre


def nivel_pedido(argumentos, por_defecto=1):
    """El nivel escrito despues del mundo, o el nivel por defecto."""
    if len(argumentos) > 2 and argumentos[2].isdigit():
        return int(argumentos[2])
    return por_defecto
