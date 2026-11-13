# casos_apagon.py  ---  los niveles del apagón (datos, no programa)
# Cada caso tiene una sola solución. Lo fabricó herramientas/generar_casos_apagon.py.
# En el mapa: '.' es piso, '#' es un muro sin número y un dígito es un muro que dice
# cuántos faroles lo tocan. 'faroles' es cuántos faroles hay que poner.
CASOS = {1: {'faroles': 4, 'mapa': ['....', '...#', '...#', '.3.#'], 'titulo': 'El apagón · nivel 1'},
 2: {'faroles': 5,
     'mapa': ['.#...', '..#.2', '.....', '2....', '#..##'],
     'titulo': 'El apagón · nivel 2'},
 3: {'faroles': 6,
     'mapa': ['###.1.', '.##...', '.#0.#.', '......', '......', '.3..1.'],
     'titulo': 'El apagón · nivel 3'},
 4: {'faroles': 8,
     'mapa': ['##.####', '.#.#.#0', '...#.#.', '...12..', '......#', '....2.#', '1....##'],
     'titulo': 'El apagón · nivel 4'}}
