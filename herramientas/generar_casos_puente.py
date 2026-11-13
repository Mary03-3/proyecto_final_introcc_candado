# generar_casos_puente.py  ---  fabrica y verifica los niveles del puente de noche (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_puente.py            verifica los niveles que ya estan en casos_puente.py
#       python3 herramientas/generar_casos_puente.py buscar     busca niveles nuevos y reescribe casos_puente.py
#
# Como se fabrica un nivel:
#   1. Se sortean los minutos de cada uno (todos distintos; Pixie es la mas rapida), quien es
#      miedoso y que parejas pelean.
#   2. Se calcula el plan mas corto con Dijkstra sobre los repartos (quien esta en cada orilla
#      y donde esta la linterna), contando de paso CUANTOS planes logran ese minimo.
#   3. Si hay exactamente un plan optimo, la linterna dura justo ese minimo. Asi la unica forma
#      de que crucen todos es ese plan, y el nivel tiene una sola solucion.
#   4. Se confirma con un conteo independiente: un recorrido exhaustivo de todos los planes sin
#      repartos repetidos que caben en la bateria (el mismo arbol que recorre la generacion 2).
#   5. Se miden las tres generaciones y se elige el nivel que cuenta mejor la historia.
# Cada nivel tiene una sola solucion; el archivo que escribe queda congelado en el repositorio.
import heapq
import os
import pprint
import random
import sys
import time
from itertools import combinations

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, os.path.join(RAIZ, "mundos", "puente"))
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))
sys.path.insert(0, os.path.join(RAIZ, "referencia", "puente"))

import mundo                 # noqa: E402
import casos_puente          # noqa: E402
from bitacora import Bitacora   # noqa: E402

NOMBRES = ["Pixie", "Rosa", "Toño", "Inés", "Lucho", "Chela", "Manuel"]
ARCHIVO = os.path.join(RAIZ, "mundos", "puente", "casos_puente.py")

# lo que se busca en cada nivel: (personas, miedosos, parejas peleadas, minutos posibles, semilla)
PEDIDO = {1: (3, 1, 1, range(1, 10), 11),
          2: (4, 1, 2, range(1, 13), 12),
          3: (5, 1, 2, range(1, 16), 13),
          4: (6, 2, 2, range(1, 16), 14)}


def caso_de(datos):
    casos_puente.CASOS[99] = datos
    return mundo.cargar(99)


def movidas(caso, alla, linterna_alla):
    """Los viajes legales desde un reparto: grupos de uno o dos, sin dejar mal a nadie en el monte."""
    orilla = [p for p in caso["nombres"] if (p in alla) == linterna_alla]
    for t in (1, 2):
        for g in combinations(orilla, t):
            nuevo = (alla - set(g)) if linterna_alla else (alla | set(g))
            nuevo = (frozenset(nuevo), not linterna_alla)
            if not mundo.a_oscuras(caso, *nuevo):
                yield g, nuevo


def optimo(caso):
    """Dijkstra sobre los repartos. Devuelve (minutos del mejor plan, cuantos planes lo logran)."""
    ini = (frozenset(), False)
    fin = (frozenset(caso["nombres"]), True)
    dist, cuantos, hechos, cola, k = {ini: 0}, {ini: 1}, set(), [(0, 0, ini)], 0
    while cola:
        d, _, r = heapq.heappop(cola)
        if r in hechos:
            continue
        hechos.add(r)
        for g, nuevo in movidas(caso, *r):
            nd = d + mundo.duracion(caso, g)
            if nd < dist.get(nuevo, 10 ** 9):
                dist[nuevo], cuantos[nuevo] = nd, cuantos[r]
                k += 1
                heapq.heappush(cola, (nd, k, nuevo))
            elif nd == dist[nuevo]:
                cuantos[nuevo] += cuantos[r]
    return dist.get(fin), cuantos.get(fin, 0)


def contar_exhaustivo(caso, tope):
    """Cuenta TODOS los planes legales, sin repartos repetidos, que cruzan a todos en <= tope minutos."""
    fin = frozenset(caso["nombres"])

    def rec(r, gastado, vistos):
        if r[0] == fin:
            return 1
        total = 0
        for g, nuevo in movidas(caso, *r):
            ng = gastado + mundo.duracion(caso, g)
            if ng <= tope and nuevo not in vistos:
                vistos.add(nuevo)
                total += rec(nuevo, ng, vistos)
                vistos.remove(nuevo)
        return total
    ini = (frozenset(), False)
    return rec(ini, 0, {ini})


def medir(caso, agente, tope):
    bit = Bitacora("medir", grabar=False)
    bit.tope = tope
    t = time.perf_counter()
    try:
        s = agente.resolver(mundo, caso, bit)
    except StopIteration:
        s = None
    c = bit.cuenta
    return {"sol": s, "pasos": c["avanzar"], "tropiezos": c["rechazar"], "deduce": c["deducir"],
            "poda": c["podar"], "eventos": bit.total(), "seg": time.perf_counter() - t}


def sortear(nivel, rnd):
    n, nm, npel, rango, _ = PEDIDO[nivel]
    minutos = sorted(rnd.sample(list(rango), n))
    nombres = NOMBRES[:n]
    miedosos = rnd.sample(nombres[1:], nm)
    parejas = list(combinations(nombres[1:], 2))
    peleados = rnd.sample(parejas, npel)
    return {"titulo": "El puente de noche · nivel %d" % nivel, "gente": list(zip(nombres, minutos)),
            "miedosos": miedosos, "peleados": peleados, "linterna": 0}


def buscar(nivel, intentos=400):
    import g1_a_ciegas
    import g2_con_hilo
    import g3_puente
    rnd = random.Random(PEDIDO[nivel][4])
    mejor = None
    for _ in range(intentos):
        datos = sortear(nivel, rnd)
        caso = caso_de(datos)
        t, k = optimo(caso)
        if k != 1:
            continue
        datos["linterna"] = t
        caso = caso_de(datos)
        g2 = medir(caso, g2_con_hilo, 400000)
        g3 = medir(caso, g3_puente, 400000)
        if g2["sol"] != 1 or g3["sol"] != 1:
            continue
        g1 = medir(caso, g1_a_ciegas, 300000 if nivel < 4 else 20000)
        # lo que se busca: G2 tropieza mucho mas que G3, y G1 (si termina) da muchos mas pasos que G2.
        # En el nivel 3 (el de la pelicula) la G2 entera cabe en la pelicula (menos de 1400 eventos).
        if nivel == 3 and g2["eventos"] > 1400:
            continue
        if nivel >= 3 and g1["sol"] is not None and g1["pasos"] < 5 * g2["pasos"]:
            continue
        nota = g2["tropiezos"] - 3 * g3["tropiezos"] + (g3["deduce"] > 0) * 50 + len(caso_de(datos)["gente"])
        if nivel == 3:
            nota += min(g1["pasos"] // max(1, g2["pasos"]), 40)
        if mejor is None or nota > mejor[0]:
            mejor = (nota, datos, g1, g2, g3)
    return mejor


def verificar(casos):
    import g1_a_ciegas
    import g2_con_hilo
    import g3_puente
    bien = True
    for nivel in sorted(casos):
        caso = caso_de(dict(casos[nivel]))
        t, k = optimo(caso)
        e = contar_exhaustivo(caso, caso["linterna"])
        mas = contar_exhaustivo(caso, caso["linterna"] - 1)
        g = [medir(caso, a, t) for (a, t) in ((g1_a_ciegas, 300000), (g2_con_hilo, 2000000), (g3_puente, 2000000))]
        ok = (t == caso["linterna"] and k == 1 and e == 1 and mas == 0)
        bien = bien and ok
        print("nivel %d: %d personas, linterna %d min | Dijkstra: óptimo %s min, %d plan(es) | exhaustivo: %d plan(es) "
              "en %d min, %d en %d min  -> %s"
              % (nivel, len(caso["gente"]), caso["linterna"], t, k, e, caso["linterna"], mas, caso["linterna"] - 1,
                 "UNA SOLUCIÓN" if ok else "MAL"))
        for nombre, m in zip(("G1", "G2", "G3"), g):
            print("    %s  soluciones %-5s pasos %7d  tropiezos %7d  deduce %3d  poda %4d  eventos %7d  %.1f s"
                  % (nombre, m["sol"] if m["sol"] is not None else "tope", m["pasos"], m["tropiezos"], m["deduce"],
                     m["poda"], m["eventos"], m["seg"]))
    return bien


def escribir(casos):
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write("# casos_puente.py  ---  los niveles del puente de noche (datos, no programa)\n")
        f.write("# 'gente': (nombre, minutos que tarda en cruzar). 'linterna': minutos de bateria.\n")
        f.write("# 'miedosos': no se quedan SOLOS en el monte sin linterna. 'peleados': no se quedan JUNTOS\n")
        f.write("# en el monte sin linterna. La bateria alcanza justo para el mejor plan, y ese plan es unico.\n")
        f.write("# Fabricados y verificados con herramientas/generar_casos_puente.py.\n")
        f.write("CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "buscar":
        nuevos = {}
        for nivel in sorted(PEDIDO):
            r = buscar(nivel)
            if r is None:
                sys.exit("No encontré un nivel %d que sirva." % nivel)
            nota, datos, g1, g2, g3 = r
            print("nivel %d: %s  G1 %s  G2 %s  G3 %s" % (nivel, datos, g1, g2, g3), flush=True)
            nuevos[nivel] = datos
        escribir(nuevos)
        casos_puente.CASOS.clear()
        casos_puente.CASOS.update(nuevos)
    casos = {k: v for k, v in casos_puente.CASOS.items() if k != 99}
    sys.exit(0 if verificar(casos) else 1)
