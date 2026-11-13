# casos_archipielago.py  ---  los niveles del archipielago (datos, no programa)
# '.' es agua; un digito es una isla y dice cuantos puentes salen de ella.
# Cada mapa tiene una sola manera de tender los puentes. Lo fabrico
# herramientas/generar_casos_archipielago.py, que tambien lo verifica.
CASOS = {1: {'titulo': 'El archipiélago · nivel 1',
     'mapa': ['3.4.3', '.....', '..1..', '4...3'],
     'solucion': [1, 2, 2, 1, 1, 2]},
 2: {'titulo': 'El archipiélago · nivel 2',
     'mapa': ['2..4.4', '......', '5.2...', '......', '4..3..', '.....2'],
     'solucion': [1, 1, 2, 1, 2, 2, 2, 2]},
 3: {'titulo': 'El archipiélago · nivel 3',
     'mapa': ['2..4..3', '.......', '.1.5.4.', '.......', '2..3..2', '.....2.'],
     'solucion': [2, 0, 1, 1, 2, 1, 2, 1, 2, 2, 0]},
 4: {'titulo': 'El archipiélago · nivel 4',
     'mapa': ['.....2.2', '........', '2....5.4', '..1.....', '.......4', '........', '3.3..2..', '.......2'],
     'solucion': [1, 1, 1, 1, 1, 1, 2, 2, 1, 2, 2, 0]}}
