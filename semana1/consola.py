# consola.py  ---  paso 4: el mundo abierto, para preguntarle a mano
# Uso:  python3 -i semana1/consola.py MUNDO
#
# La -i deja a Python esperando ordenes despues de correr este archivo.
# Quedan listas cuatro variables: mundo, caso, estado y opciones.
import sys
from comun import abrir

mundo, nombre = abrir(sys.argv)
caso = mundo.cargar(1)
estado = mundo.inicio(caso)
opciones = mundo.opciones(caso, estado)
print("Listo. Tienen: mundo, caso, estado y opciones (%d). Para salir: exit()" % len(opciones))
