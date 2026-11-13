# casos_candado.py  ---  los niveles del candado (datos, no programa)
# Cada caso tiene una sola solucion. Lo fabrico herramientas/generar_casos_candado.py.
# Cada intento es [digitos, luces verdes, luces amarillas]: verde es un digito en su
# sitio; amarilla, un digito que esta en la clave pero en otra rueda.
CASOS = {1: {'titulo': 'El candado · nivel 1',
     'ruedas': 3,
     'digitos': 6,
     'intentos': [[[4, 1, 3], 0, 0], [[3, 4, 2], 0, 1], [[1, 2, 0], 0, 2]],
     'clave': [2, 0, 5]},
 2: {'titulo': 'El candado · nivel 2',
     'ruedas': 3,
     'digitos': 10,
     'intentos': [[[6, 3, 8], 0, 1], [[3, 5, 9], 1, 0], [[4, 9, 6], 0, 1], [[3, 9, 6], 0, 0]],
     'clave': [8, 5, 4]},
 3: {'titulo': 'El candado · nivel 3',
     'ruedas': 4,
     'digitos': 10,
     'intentos': [[[2, 4, 0, 3], 1, 1], [[4, 6, 2, 3], 1, 1], [[8, 2, 4, 5], 0, 0], [[4, 5, 6, 9], 0, 2]],
     'clave': [6, 0, 9, 3]},
 4: {'titulo': 'El candado · nivel 4',
     'ruedas': 5,
     'digitos': 10,
     'intentos': [[[3, 0, 1, 4, 9], 1, 1],
                  [[9, 2, 5, 0, 7], 2, 2],
                  [[3, 6, 4, 9, 8], 0, 0],
                  [[5, 9, 0, 8, 7], 0, 3]],
     'clave': [7, 2, 1, 0, 5]}}
