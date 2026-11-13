# generar_casos_bodega.py  ---  fabrica y verifica los niveles de la bodega (lo corre el profesor)
#
# Uso:  python3 generar_casos_bodega.py            busca niveles nuevos y escribe casos_bodega.py
#       python3 generar_casos_bodega.py verificar  solo verifica los niveles que ya estan escritos
#
# Como se fabrica un nivel. Se arma una bodega al azar (paredes, cajas, muelles y Pixie) y se
# recorre con una busqueda a lo ancho TODO lo que se puede hacer con empujes. Un acomodo es
# (donde estan las cajas, en que zona puede caminar Pixie). La busqueda da el numero minimo de
# empujes para despachar la carga, y ese numero es el turno del nivel. Ademas cuenta por cuantos
# caminos distintos de ese largo se llega: el nivel se acepta solo si hay UNO.
#
# Por que eso basta para que el nivel tenga exactamente una solucion. Con el turno igual al minimo,
# toda solucion tiene exactamente ese largo, asi que es un camino mas corto del grafo de acomodos:
# no repite acomodos y no deja cajas arrinconadas (una caja arrinconada no vuelve a moverse). Cada
# empuje distinto lleva a un acomodo distinto, de modo que contar caminos es contar soluciones.
#
# Despues se miden las tres generaciones del agente sobre el nivel, para escoger niveles donde
# los numeros cuenten la historia (G1 mucho mas que G2, G2 tropieza mas que G3).
import os
import pprint
import random
import sys
import time
from collections import deque

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, os.path.join(RAIZ, "mundos", "bodega"))
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))
sys.path.insert(0, os.path.join(RAIZ, "referencia", "bodega"))

import mundo                      # noqa: E402
from bitacora import Bitacora     # noqa: E402
import g1_a_ciegas                # noqa: E402
import g2_con_hilo                # noqa: E402
import g3_bodega                  # noqa: E402

LADOS = ("N", "E", "S", "O")


# ----------------------------------------------------------------- el grafo de acomodos
def vecinos(caso, cajas, pixie):
    """Los acomodos a los que se llega con un empuje: lista de (empuje, cajas, pixie)."""
    zona = mundo.alcanza(caso, set(cajas), pixie)
    salen = []
    for caja in cajas:
        for lado in LADOS:
            adelante = mundo.mover(caja, lado)
            df, dc = mundo.LADOS[lado]
            detras = (caja[0] - df, caja[1] - dc)
            if detras in zona and not mundo.pared(caso, adelante) and adelante not in cajas:
                nuevas = tuple(sorted(adelante if x == caja else x for x in cajas))
                salen.append(((caja, lado), nuevas, caja))
    return salen


def contar(caso, tope=40):
    """Busqueda a lo ancho. Devuelve (minimo de empujes, cuantos caminos de ese largo, acomodos vistos)
    o (None, 0, vistos) si no se despacha en 'tope' empujes."""
    cajas = tuple(sorted(caso["cajas"]))
    raiz = mundo.acomodo(caso, cajas, caso["entrada"])
    dist = {raiz: 0}
    caminos = {raiz: 1}
    donde = {raiz: caso["entrada"]}                  # una casilla de Pixie en esa zona
    capa = [raiz]
    for d in range(tope + 1):
        listos = [a for a in capa if all(mundo.es_meta(caso, x) for x in a[0])]
        if listos:
            return d, sum(caminos[a] for a in listos), len(dist)
        siguiente = []
        for a in capa:
            for (_, nuevas, pixie) in vecinos(caso, a[0], donde[a]):
                b = mundo.acomodo(caso, nuevas, pixie)
                if b not in dist:
                    dist[b] = d + 1
                    caminos[b] = caminos[a]
                    donde[b] = pixie
                    siguiente.append(b)
                elif dist[b] == d + 1:
                    caminos[b] = caminos[b] + caminos[a]
        capa = siguiente
        if not capa:
            break
    return None, 0, len(dist)


# ----------------------------------------------------------------- medir las generaciones
def medir(caso, tope_g1=3000000):
    filas = []
    for g in (g2_con_hilo, g3_bodega, g1_a_ciegas):
        bit = Bitacora(g.__name__, grabar=False)
        if g is g1_a_ciegas:
            bit.tope = tope_g1
        t = time.perf_counter()
        try:
            s = g.resolver(mundo, caso, bit)
        except StopIteration:
            s = None
        filas.append((g.__name__, s, bit.cuenta["avanzar"], bit.cuenta["rechazar"], bit.cuenta["deducir"],
                      bit.cuenta["podar"], time.perf_counter() - t, bit.total()))
    return [filas[2], filas[0], filas[1]]


# ----------------------------------------------------------------- fabricar
def bodega_al_azar(filas, columnas, cajas, densidad, rnd):
    g = [["#"] * columnas for _ in range(filas)]
    for f in range(1, filas - 1):
        for c in range(1, columnas - 1):
            g[f][c] = "#" if rnd.random() < densidad else "."
    piso = [(f, c) for f in range(filas) for c in range(columnas) if g[f][c] == "."]
    if len(piso) < cajas * 2 + 4:
        return None
    # todo el piso conectado
    vistas = {piso[0]}
    cola = deque([piso[0]])
    while cola:
        f, c = cola.popleft()
        for (a, b) in ((f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)):
            if g[a][b] == "." and (a, b) not in vistas:
                vistas.add((a, b))
                cola.append((a, b))
    if len(vistas) != len(piso):
        return None
    rnd.shuffle(piso)
    metas = piso[:cajas]
    resto = piso[cajas:]
    datos = {"mapa": ["".join(r) for r in g]}
    caso = mundo.preparar(datos)
    candidatas = [x for x in resto if not mundo.esquina(caso, x)]
    if len(candidatas) < cajas + 1:
        return None
    puestas = candidatas[:cajas]
    pixie = candidatas[cajas]
    for (f, c) in metas:
        g[f][c] = "M"
    for (f, c) in puestas:
        g[f][c] = "C"
    g[pixie[0]][pixie[1]] = "P"
    return ["".join(r) for r in g]


def valido(mapa):
    """¿El piso esta todo conectado y ninguna caja empieza en una esquina?"""
    caso = mundo.preparar({"mapa": mapa})
    piso = [(f, c) for f in range(caso["filas"]) for c in range(caso["columnas"]) if (f, c) not in caso["paredes"]]
    if not piso or any(mundo.esquina(caso, x) for x in caso["cajas"]):
        return False
    return len(mundo.alcanza(caso, set(), piso[0])) == len(piso)


def mutar(mapa, rnd):
    """Un cambio pequeño: una pared que se pone o se quita, o una caja, un muelle o Pixie que se mudan."""
    g = [list(fila) for fila in mapa]
    filas, columnas = len(g), len(g[0])
    adentro = [(f, c) for f in range(1, filas - 1) for c in range(1, columnas - 1)]
    vacias = [x for x in adentro if g[x[0]][x[1]] == "."]
    tipo = rnd.choice("##CMP")
    if tipo == "#":
        f, c = rnd.choice([x for x in adentro if g[x[0]][x[1]] in "#."])
        g[f][c] = "." if g[f][c] == "#" else "#"
    else:
        cuales = [x for x in adentro if g[x[0]][x[1]] == tipo]
        if not cuales or not vacias:
            return None
        a, b = rnd.choice(cuales), rnd.choice(vacias)
        g[a[0]][a[1]], g[b[0]][b[1]] = ".", tipo
    nuevo = ["".join(r) for r in g]
    return nuevo if valido(nuevo) else None


def puntaje(mapa, bmax):
    """Mas alto es mejor: turnos largos con una sola solucion. -1 si no se despacha dentro de bmax."""
    caso = mundo.preparar({"mapa": mapa, "turno": 99})
    b, n, _ = contar(caso, bmax)
    if b is None:
        return -1, None, 0
    return b * 10 - 6 * (n - 1) ** 0.5, b, n


def fabricar(nivel, plan, semilla, intentos):
    """Busqueda local: se parte de una bodega al azar y se la va cambiando de a poco, quedandose con
    los cambios que alargan el turno sin abrir caminos alternos. Cuando un nivel tiene una sola
    solucion con un turno en el rango buscado, se miden las generaciones y se decide."""
    filas, columnas, cajas, densidad, bmin, bmax, tope_g1, criterio = plan
    rnd = random.Random(semilla)
    for _ in range(intentos):
        mapa = bodega_al_azar(filas, columnas, cajas, densidad, rnd)
        if mapa is None or not valido(mapa):
            continue
        actual, b, n = puntaje(mapa, bmax)
        for _ in range(400):
            otro = mutar(mapa, rnd)
            if otro is None:
                continue
            p, b2, n2 = puntaje(otro, bmax)
            if p < actual:
                continue
            mapa, actual, b, n = otro, p, b2, n2
            if n == 1 and bmin <= b <= bmax:
                caso = mundo.preparar({"mapa": mapa, "turno": b})
                medidas = medir(caso, tope_g1)
                print("   probado: turno %d, G1 %s pasos %d, G2 pasos %d trop %d, G3 trop %d"
                      % (b, medidas[0][1], medidas[0][2], medidas[1][2], medidas[1][3], medidas[2][3]), flush=True)
                if criterio(medidas):
                    return mapa, b, medidas
    return None


def g1_g2(m):
    return m[0][1] == 1 and m[1][1] == 1 and m[2][1] == 1


PLANES = {   # nivel: (filas, columnas, cajas, densidad de paredes, turno minimo, turno maximo, criterio)
    1: (6, 6, 2, 0.10, 5, 6, 300000, lambda m: g1_g2(m) and m[0][6] < 3 and m[0][2] >= 6 * m[1][2]),
    2: (7, 7, 2, 0.14, 7, 9, 100000, lambda m: g1_g2(m) and m[0][6] < 10 and m[0][2] >= 2000 and m[1][2] >= 25 and m[0][2] >= 8 * m[1][2] and m[1][3] >= 2 * m[2][3]),
    3: (7, 8, 2, 0.15, 9, 11, 300000, lambda m: g1_g2(m) and m[0][6] < 30 and m[0][2] >= 15000 and m[1][2] >= 40
        and m[1][7] <= 1250
        and m[0][2] >= 10 * m[1][2] and m[1][3] >= 3 * m[2][3] and m[2][4] >= 3 and m[2][5] >= 3),
    4: (8, 8, 3, 0.18, 9, 12, 600000, lambda m: g1_g2(m) and m[0][2] >= 60000 and m[1][2] >= 80
        and m[0][2] >= 10 * m[1][2] and m[1][3] >= 3 * m[2][3]),
}


def escribir(casos):
    with open(os.path.join(RAIZ, "mundos", "bodega", "casos_bodega.py"), "w", encoding="utf-8") as f:
        f.write("# casos_bodega.py  ---  los niveles de la bodega (datos, no programa)\n"
                "# '#' pared, '.' piso, 'P' Pixie, 'C' caja, 'M' muelle de carga. 'turno' es cuantos empujes alcanza el turno.\n"
                "# En cada nivel hay una sola manera de despachar la carga sin pasarse del turno\n"
                "# (lo verifica herramientas/generar_casos_bodega.py).\n"
                "CASOS = " + pprint.pformat(casos, width=60, sort_dicts=False) + "\n")


def verificar():
    """Comprueba con la busqueda a lo ancho que cada nivel escrito tiene UNA solucion con su turno."""
    bien = True
    for nivel in mundo.casos():
        caso = mundo.cargar(nivel)
        b, n, vistos = contar(caso, caso["turno"])
        ok = b == caso["turno"] and n == 1
        bien = bien and ok
        print("nivel %d: turno %d, mínimo %s, soluciones de ese largo %d, acomodos explorados %d  %s"
              % (nivel, caso["turno"], b, n, vistos, "bien" if ok else "MAL"))
    return bien


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        sys.exit(0 if verificar() else 1)
    SEMILLAS = {1: 11, 2: 22, 3: 33, 4: 44}
    elegidos = [int(x) for x in sys.argv[1:]] or sorted(PLANES)
    casos = {}
    try:
        from casos_bodega import CASOS as VIEJOS
        casos.update(VIEJOS)
    except ImportError:
        pass
    for nivel in elegidos:
        r = fabricar(nivel, PLANES[nivel], SEMILLAS[nivel], 20000)
        if r is None:
            print("nivel", nivel, ": no se encontró un nivel que cumpla")
            continue
        mapa, turno, medidas = r
        casos[nivel] = {"titulo": "La bodega · nivel %d" % nivel, "mapa": mapa, "turno": turno}
        print("nivel", nivel, "turno", turno)
        print("\n".join("   " + fila for fila in mapa))
        for fila in medidas:
            print("   %-14s soluciones %s  pasos %d  tropiezos %d  deduce %d  poda %d  (%.2f s, %d eventos)" % fila)
    escribir(dict(sorted(casos.items())))
    import importlib
    import casos_bodega
    mundo.CASOS = importlib.reload(casos_bodega).CASOS
    verificar()
