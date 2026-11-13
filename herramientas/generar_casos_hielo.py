# generar_casos_hielo.py  ---  fabrica y verifica los niveles de la pista de hielo (lo corre el profesor)
#
# Se sortean pistas con rocas y huecos de agua. De cada pista se calcula, con una
# busqueda a lo ancho sobre las casillas donde Pixie puede frenar, cuantos impulsos
# hacen falta como minimo para ir de la entrada a cada casilla, y por cuantos caminos
# distintos. La salida se pone en una casilla a la que se llega por UN SOLO camino
# minimo, y los impulsos alcanzan justo para ese camino. Asi cada nivel tiene una
# sola solucion. Despues se comprueba de otra manera: se cuentan, uno por uno, todos
# los caminos sin repetir casillas que llegan a la salida sin hundirse y sin pasarse
# de impulsos. Tiene que dar 1.
#
# Ademas se corren las tres generaciones y se exige que los numeros cuenten la historia:
# la generacion 1 visita bastantes mas estados que la 2, la 2 tropieza bastante mas que
# la 3, y la 3 encuentra al menos una trampa que deducir.
#
# Uso:  python3 herramientas/generar_casos_hielo.py            fabrica y escribe casos_hielo.py
#       python3 herramientas/generar_casos_hielo.py verificar  solo verifica los niveles guardados
import os
import pprint
import random
import sys
from collections import deque

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, os.path.join(RAIZ, "mundos", "hielo"))
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))
sys.path.insert(0, os.path.join(RAIZ, "referencia", "hielo"))

import mundo                       # noqa: E402
from bitacora import Bitacora      # noqa: E402
import g1_a_ciegas                 # noqa: E402
import g2_con_hilo                 # noqa: E402
import g3_hielo                    # noqa: E402

TOPE_G1 = 400000                   # si la generacion 1 pasa de estos eventos, la pista no sirve


def sortear(n, densidad, aguas, rnd):
    """Una pista de n x n con baranda de roca, rocas sueltas y huecos de agua. Sin entrada ni salida."""
    g = [["#"] * n for _ in range(n)]
    for f in range(1, n - 1):
        for c in range(1, n - 1):
            g[f][c] = "#" if rnd.random() < densidad else "."
    libres = [(f, c) for f in range(1, n - 1) for c in range(1, n - 1) if g[f][c] == "."]
    rnd.shuffle(libres)
    for (f, c) in libres[:aguas]:
        g[f][c] = "O"
    return g


def caso_de(g, entrada, salida, impulsos):
    filas = [list(r) for r in g]
    filas[salida[0]][salida[1]] = "S"
    filas[entrada[0]][entrada[1]] = "E"
    return {"titulo": "", "mapa": ["".join(r) for r in filas], "impulsos": impulsos}


def a_lo_ancho(caso):
    """Impulsos minimos y numero de caminos minimos desde la entrada a cada casilla de frenado (sin agua)."""
    ent = caso["entrada"]
    d = {ent: 0}
    cuenta = {ent: 1}
    q = deque([ent])
    while q:
        x = q.popleft()
        for (_, v) in mundo.destinos(caso, x):
            if v in caso["agua"]:
                continue
            if v not in d:
                d[v] = d[x] + 1
                cuenta[v] = cuenta[x]
                q.append(v)
            elif d[v] == d[x] + 1:
                cuenta[v] += cuenta[x]
    return d, cuenta


def contar_soluciones(caso):
    """Cuenta TODOS los caminos que llegan a la salida sin repetir casilla, sin agua y sin pasarse
    de impulsos. Es independiente de los agentes: lo que debe dar es 1."""
    def dfs(camino):
        aqui = camino[-1]
        if aqui == caso["salida"]:
            return 1
        if len(camino) - 1 >= caso["impulsos"]:
            return 0
        total = 0
        for (_, v) in mundo.destinos(caso, aqui):
            if v in caso["agua"] or v in camino:
                continue
            total += dfs(camino + [v])
        return total
    return dfs([caso["entrada"]])


def medir(caso):
    """Corre las tres generaciones y devuelve sus cuentas (o None si la generacion 1 no termina)."""
    filas = {}
    for nombre, g in (("g1", g1_a_ciegas), ("g2", g2_con_hilo), ("g3", g3_hielo)):
        bit = Bitacora(nombre, grabar=False)
        if nombre == "g1":
            bit.tope = TOPE_G1
        try:
            s = g.resolver(mundo, caso, bit)
        except StopIteration:
            return None
        filas[nombre] = dict(bit.cuenta, soluciones=s)
    return filas


def intento(n, densidad, aguas, largo, rnd):
    g = sortear(n, densidad, aguas, rnd)
    libres = [(f, c) for f in range(1, n - 1) for c in range(1, n - 1) if g[f][c] == "."]
    ent = (n - 2, rnd.randint(1, 2))                      # la entrada, abajo a la izquierda
    if g[ent[0]][ent[1]] != ".":
        return None
    provisional = mundo.preparar(caso_de(g, ent, ent, 99))      # la salida aun no esta puesta
    provisional["entrada"], provisional["salida"] = ent, None
    d, cuenta = a_lo_ancho(provisional)
    candidatas = [x for x in d if d[x] == largo and cuenta[x] == 1 and x != ent]
    if not candidatas or len(d) < len(libres) * 0.35:
        return None
    sal = rnd.choice(candidatas)
    datos = caso_de(g, ent, sal, largo)
    caso = mundo.preparar(datos)
    if contar_soluciones(caso) != 1:
        return None
    return datos, caso


def bueno(filas, nivel):
    g1, g2, g3 = filas["g1"], filas["g2"], filas["g3"]
    if not (g1["soluciones"] == g2["soluciones"] == g3["soluciones"] == 1):
        return False
    razon = {1: 3, 2: 4, 3: 6, 4: 6}[nivel]
    if g1["avanzar"] < razon * g2["avanzar"]:
        return False
    if g2["rechazar"] < 3 * max(1, g3["rechazar"]) or g3["deducir"] < (1 if nivel == 1 else 2):
        return False
    if nivel == 1 and g1["avanzar"] > 400:
        return False
    if nivel == 3 and not (g1["avanzar"] < 6000 and 10 <= g3["avanzar"] + g3["podar"] <= 45):
        return False
    return True


def fabricar(nivel, n, densidad, aguas, largo, semilla):
    rnd = random.Random(semilla)
    for vuelta in range(200000):
        r = intento(n, densidad, aguas, largo, rnd)
        if r is None:
            continue
        datos, caso = r
        filas = medir(caso)
        if filas and bueno(filas, nivel):
            return datos, filas
    raise RuntimeError("no se hallo una pista para el nivel %d" % nivel)


def mostrar(nivel, datos, filas):
    print("nivel", nivel, "impulsos", datos["impulsos"])
    print("\n".join("   " + r for r in datos["mapa"]))
    for k in ("g1", "g2", "g3"):
        f = filas[k]
        print("   %s  soluciones %d  pasos %d  tropiezos %d  deduce %d  poda %d"
              % (k, f["soluciones"], f["avanzar"], f["rechazar"], f["deducir"], f["podar"]))


PLANES = [   # (nivel, lado, densidad de rocas, huecos de agua, impulsos, semilla)
    (1, 7, 0.16, 2, 5, 1),
    (2, 8, 0.16, 3, 6, 2),
    (3, 9, 0.15, 4, 8, 3),
    (4, 10, 0.15, 5, 10, 4),
]

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        for nivel in mundo.casos():
            caso = mundo.cargar(nivel)
            d, cuenta = a_lo_ancho(caso)
            print("nivel %d: camino minimo %d impulsos (hay %d), caminos minimos %d, soluciones contadas una por una %d"
                  % (nivel, d[caso["salida"]], caso["impulsos"], cuenta[caso["salida"]], contar_soluciones(caso)))
        sys.exit(0)
    casos = {}
    for (nivel, n, dens, aguas, largo, semilla) in PLANES:
        datos, filas = fabricar(nivel, n, dens, aguas, largo, semilla)
        datos["titulo"] = "La pista de hielo · nivel %d" % nivel
        casos[nivel] = datos
        mostrar(nivel, datos, filas)
    with open(os.path.join(RAIZ, "mundos", "hielo", "casos_hielo.py"), "w", encoding="utf-8") as f:
        f.write("# casos_hielo.py  ---  los niveles de la pista de hielo (datos, no programa)\n"
                "# '#' roca o baranda, '.' hielo, 'E' entrada, 'S' salida, 'O' hueco de agua.\n"
                "# 'impulsos' es cuantas veces puede tomar impulso Pixie. Lo fabrico herramientas/generar_casos_hielo.py.\n"
                "# En cada nivel hay un solo camino que llega a la salida sin hundirse y sin pasarse de impulsos.\n"
                "CASOS = " + pprint.pformat(casos, width=60, sort_dicts=False) + "\n")
