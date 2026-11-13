# generar_casos_cueva.py  ---  fabrica los niveles de la cueva (lo corre el profesor)
# Cavernas abiertas. Se buscan cuevas donde el camino seguro mas corto de la entrada al cofre es UNICO;
# el aceite del farol alcanza justo para ese camino. Asi cada nivel tiene una sola solucion.
import os, pprint, random, sys
from collections import deque
AQUI = os.path.dirname(os.path.abspath(__file__))

def vecinas(g, n, x):
    f, c = x
    return [(a, b) for a, b in ((f - 1, c), (f, c + 1), (f + 1, c), (f, c - 1)) if 0 <= a < n and 0 <= b < n and g[a][b] != "#"]

def intento(n, densidad, pozos, rnd):
    g = [["#"] * n for _ in range(n)]
    for f in range(1, n - 1):
        for c in range(1, n - 1):
            g[f][c] = "#" if rnd.random() < densidad else "."
    ent = (n - 2, 1); g[ent[0]][ent[1]] = "."
    # distancias desde la entrada sin pozos
    def bfs(prohibidas):
        d = {ent: 0}; cuenta = {ent: 1}; q = deque([ent])
        while q:
            x = q.popleft()
            for v in vecinas(g, n, x):
                if v in prohibidas: continue
                if v not in d: d[v] = d[x] + 1; cuenta[v] = cuenta[x]; q.append(v)
                elif d[v] == d[x] + 1: cuenta[v] += cuenta[x]
        return d, cuenta
    d, _ = bfs(set())
    if len(d) < (n - 2) * (n - 2) * 0.55: return None
    cofre = max(d, key=lambda x: (d[x], x))
    if d[cofre] < n: return None
    libres = [x for x in d if x not in (ent, cofre) and d[x] >= 2]
    rnd.shuffle(libres)
    pz = set()
    for x in libres:
        if len(pz) == pozos: break
        if all(abs(x[0] - y[0]) + abs(x[1] - y[1]) >= 2 for y in pz) and abs(x[0] - cofre[0]) + abs(x[1] - cofre[1]) >= 2:
            pz.add(x)
    if len(pz) < pozos: return None
    d2, cuenta = bfs(pz)
    if cofre not in d2 or cuenta[cofre] != 1: return None
    # que el camino pase junto a algun pozo (que haya brisa en el camino) y que los pozos estorben
    ruta = []; x = cofre
    while x != ent:
        ruta.append(x); x = [v for v in vecinas(g, n, x) if v in d2 and d2[v] == d2[x] - 1][0]
    brisas = sum(1 for x in ruta if any(v in pz for v in vecinas(g, n, x)))
    if brisas < max(1, pozos // 2): return None
    for (f, c) in pz: g[f][c] = "O"
    g[ent[0]][ent[1]] = "E"; g[cofre[0]][cofre[1]] = "C"
    return ["".join(r) for r in g], d2[cofre]

def fabricar(n, densidad, pozos, semilla):
    rnd = random.Random(semilla)
    while True:
        r = intento(n, densidad, pozos, rnd)
        if r: return r

if __name__ == "__main__":
    casos = {}
    planes = [(7, 0.2, 2, 3), (8, 0.22, 3, 1), (9, 0.24, 4, 4), (11, 0.26, 6, 2)]
    for nivel, (n, dens, pozos, semilla) in enumerate(planes, 1):
        mapa, pasos = fabricar(n, dens, pozos, semilla)
        casos[nivel] = {"titulo": "La cueva · nivel %d" % nivel, "mapa": mapa, "aceite": pasos}
        print("nivel", nivel, "aceite", pasos); print("\n".join("   " + r for r in mapa))
    with open(os.path.join(AQUI, "..", "mundos", "cueva", "casos_cueva.py"), "w", encoding="utf-8") as f:
        f.write("# casos_cueva.py  ---  los niveles de la cueva (datos, no programa)\n"
                "# '#' roca, '.' piso, 'E' entrada, 'C' cofre, 'O' pozo. 'aceite' es para cuantos pasos alcanza el farol.\n"
                "# En cada nivel hay un solo camino que llega al cofre sin caer y sin que se apague el farol.\n"
                "CASOS = " + pprint.pformat(casos, width=60, sort_dicts=False) + "\n")
