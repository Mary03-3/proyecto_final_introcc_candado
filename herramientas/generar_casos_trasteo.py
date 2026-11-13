# generar_casos_trasteo.py  ---  fabrica y verifica los niveles del trasteo (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_trasteo.py            fabrica los cuatro niveles y los escribe
#       python3 herramientas/generar_casos_trasteo.py verificar  solo verifica los niveles ya escritos
#
# Como se fabrica un nivel:
#   1. Se elige un camion de filas x columnas y se ocupan al azar algunas casillas (bultos ajenos).
#   2. Se eligen muebles de FORMAS DISTINTAS cuyas casillas sumen exactamente las libres.
#   3. Se cuentan TODAS las maneras de acomodarlos (hasta 2) con una busqueda exacta:
#      siempre se cubre la primera casilla vacia, leyendo de arriba a abajo. Esa busqueda
#      cuenta cada acomodo una sola vez, porque cada acomodo cubre esa casilla con un
#      unico mueble en una unica posicion.
#   4. Se acepta el nivel si hay exactamente UNA manera y si la generacion 1 (que prueba
#      todas las combinaciones) da un numero de pasos dentro del rango pedido.
#
# Como se cuentan las soluciones. Una solucion es una asignacion mueble -> casillas.
# Como no hay dos muebles con la misma forma, cambiar dos muebles de lugar nunca da el
# mismo camion; y como los giros que caen en las mismas casillas se cuentan una vez
# (mundo.posiciones), un mueble simetrico no multiplica las soluciones. Asi, "una
# solucion" quiere decir "un solo camion lleno posible".
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "..", "mundos", "trasteo")
sys.path.insert(0, os.path.join(AQUI, "..", "Recursos"))
sys.path.insert(0, CARPETA)

import mundo                     # noqa: E402
import casos_trasteo             # noqa: E402

# nivel: (filas, columnas, bultos ajenos, muebles, pasos de G1 minimos y maximos, semilla)
PEDIDO = {
    1: (3, 4, 1, 3, 200, 20000, 11),
    2: (4, 4, 2, 4, 5000, 120000, 22),
    3: (4, 5, 2, 5, 150000, 900000, 33),
    4: (5, 5, 3, 6, 600000, 4000000, 44),
}
TITULO = "El trasteo · nivel %d"
# El catalogo en un orden fijo: el azar elige por posicion en esta lista, asi que cambiarle
# el orden (o renombrar un mueble y reordenar) fabrica otros niveles con la misma semilla.
CATALOGO = ["el armario", "el baúl", "el comedor", "el escritorio", "el piano", "el sofá",
            "el sofá grande", "la biblioteca", "la cama", "la estantería", "el modular"]


def caso_de(datos):
    casos_trasteo.CASOS[99] = dict(datos, titulo="prueba")
    return mundo.cargar(99)


def contar(caso, tope=2):
    """Cuantas maneras hay de llenar el camion (se detiene al llegar a tope)."""
    por_casilla = {}
    for m in caso["orden"]:
        for casillas in caso["posiciones"][m]:
            por_casilla.setdefault(casillas[0], []).append((m, casillas))
    libres = caso["libres"]
    llenas = set()
    usados = set()
    cuenta = [0]
    halladas = []

    def bus():
        if cuenta[0] >= tope:
            return
        primera = None
        for x in libres:
            if x not in llenas:
                primera = x
                break
        if primera is None:
            cuenta[0] += 1
            halladas.append({m: c for (m, c) in pila})
            return
        for (m, casillas) in por_casilla.get(primera, []):
            if m in usados or any(x in llenas for x in casillas):
                continue
            usados.add(m)
            llenas.update(casillas)
            pila.append((m, casillas))
            bus()
            pila.pop()
            llenas.difference_update(casillas)
            usados.discard(m)

    pila = []
    bus()
    return cuenta[0], halladas


def pasos_g1(caso):
    """Los pasos (avanzar) de la generacion 1: prueba todas las posiciones de cada mueble, en orden."""
    total, producto = 0, 1
    for m in caso["orden"]:
        producto = producto * len(caso["posiciones"][m])
        total = total + producto
    return total


def fabricar(nivel):
    filas, columnas, bultos, n, minimo, maximo, semilla = PEDIDO[nivel]
    rnd = random.Random(semilla)
    nombres = list(CATALOGO)
    assert sorted(nombres) == sorted(mundo.FORMAS), "el catalogo no coincide con mundo.FORMAS"
    intentos = 0
    while True:
        intentos += 1
        celdas = [(f, c) for f in range(filas) for c in range(columnas)]
        tapadas = set(rnd.sample(celdas, bultos))
        camion = ["".join("#" if (f, c) in tapadas else "." for c in range(columnas)) for f in range(filas)]
        libres = filas * columnas - bultos
        elegidos = rnd.sample(nombres, n)
        if sum(mundo.tamano(m) for m in elegidos) != libres:
            continue
        rnd.shuffle(elegidos)
        elegidos.sort(key=lambda m: -mundo.tamano(m))      # lo grande sale primero de la casa
        datos = {"camion": camion, "muebles": elegidos}
        caso = caso_de(datos)
        if any(len(caso["posiciones"][m]) == 0 for m in elegidos):
            continue
        g1 = pasos_g1(caso)
        if not (minimo <= g1 <= maximo):
            continue
        cuantas, halladas = contar(caso)
        if cuantas != 1:
            continue
        sol = {m: [list(x) for x in halladas[0][m]] for m in elegidos}
        print("nivel %d: %d intentos, camion %dx%d, %d muebles, G1 hara %d pasos" % (nivel, intentos, filas, columnas, n, g1))
        return dict(titulo=TITULO % nivel, camion=camion, muebles=elegidos, solucion=sol)


def verificar(casos):
    bien = True
    for nivel in sorted(casos):
        casos_trasteo.CASOS[nivel] = casos[nivel]
        caso = mundo.cargar(nivel)
        formas = [frozenset(mundo.giros(mundo.FORMAS[m])) for m in caso["orden"]]
        distintas = len(set(formas)) == len(formas)
        suma = sum(mundo.tamano(m) for m in caso["orden"]) == len(caso["libres"])
        cuantas, halladas = contar(caso, tope=10)
        guardada = {m: tuple(tuple(x) for x in casos[nivel]["solucion"][m]) for m in caso["orden"]}
        coincide = cuantas == 1 and {m: tuple(halladas[0][m]) for m in halladas[0]} == guardada
        estado = {"puestos": guardada}
        valida = mundo.completo(caso, estado) and mundo.viola(caso, estado) == ""
        ok = distintas and suma and cuantas == 1 and coincide and valida
        bien = bien and ok
        print("nivel %d: soluciones %d | formas distintas %s | suma exacta %s | coincide con la guardada %s | G1 hara %d pasos  %s"
              % (nivel, cuantas, distintas, suma, coincide and valida, pasos_g1(caso), "OK" if ok else "FALLA"))
    return bien


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        sys.exit(0 if verificar(dict(casos_trasteo.CASOS)) else 1)
    nuevos = {nivel: fabricar(nivel) for nivel in sorted(PEDIDO)}
    texto = ("# casos_trasteo.py  ---  los niveles del trasteo (datos, no programa)\n"
             "# Cada caso tiene una sola manera de llenar el camion. Lo fabrico herramientas/generar_casos_trasteo.py.\n"
             "# camion: '.' casilla libre, '#' bulto ajeno (ahi no cabe nada). La fila 1 es la del fondo, junto a la cabina.\n"
             "# muebles: en el orden en que salen de la casa. solucion: las casillas de cada mueble (fila, columna desde 0).\n"
             "CASOS = " + pprint.pformat(nuevos, width=110, sort_dicts=False) + "\n")
    with open(os.path.join(CARPETA, "casos_trasteo.py"), "w", encoding="utf-8") as f:
        f.write(texto)
    print("Escrito mundos/trasteo/casos_trasteo.py")
    if not verificar(nuevos):
        sys.exit(1)
