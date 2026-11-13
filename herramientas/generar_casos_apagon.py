# generar_casos_apagon.py  ---  fabrica los niveles del apagon (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_apagon.py            fabrica, verifica y escribe casos_apagon.py
#       python3 herramientas/generar_casos_apagon.py verificar  solo verifica los niveles ya escritos
#
# Como se fabrica un nivel:
#   1. Se ponen muros al azar en un salon de filas x columnas.
#   2. Se ponen faroles al azar, uno a uno, en casillas que siguen a oscuras, hasta
#      que todo el piso queda alumbrado. Esa es la solucion escondida.
#   3. Cada muro recibe su numero: cuantos faroles de la solucion lo tocan.
#   4. Se borran numeros, en orden al azar, mientras la solucion siga siendo la unica.
#      Asi el nivel dice lo menos posible.
#   5. Se miden la generacion 1 y la 2 sobre el nivel. Entre muchas semillas se queda
#      el nivel donde la generacion 2 mas tiene que devolverse, siempre que la 1 de al
#      menos 8 veces sus pasos y no se pase de su tope.
# La unicidad la comprueba contar(), un buscador aparte que no usa el agente: cuenta
# TODAS las maneras de poner faroles, con cualquier numero de faroles.
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
CARPETA = os.path.join(RAIZ, "mundos", "apagon")
ARCHIVO = os.path.join(CARPETA, "casos_apagon.py")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, CARPETA)
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))

if not os.path.exists(ARCHIVO):
    with open(ARCHIVO, "w", encoding="utf-8") as fh:
        fh.write("CASOS = {}\n")

import casos_apagon      # noqa: E402
import mundo             # noqa: E402
from bitacora import Bitacora   # noqa: E402
import g1_a_ciegas       # noqa: E402
import g2_con_hilo       # noqa: E402

# (filas, columnas, muros, faroles minimos y maximos, tope de pasos de la generacion 1, semillas)
PLANES = {
    1: (4, 4, 4, (3, 4), 2000, range(0, 400)),
    2: (5, 5, 7, (4, 5), 40000, range(0, 400)),
    3: (6, 6, 11, (6, 7), 400000, range(0, 400)),
    4: (7, 7, 20, (7, 8), 6000000, range(0, 3000)),
}


def mapa_de(n, m, muros, numeros):
    filas = []
    for f in range(n):
        fila = ""
        for c in range(m):
            if (f, c) in muros:
                fila += str(numeros[(f, c)]) if (f, c) in numeros else "#"
            else:
                fila += "."
        filas.append(fila)
    return filas


def caso_de(mapa, faroles, titulo="prueba"):
    mundo.CASOS[99] = {"titulo": titulo, "mapa": mapa, "faroles": faroles}
    return mundo.cargar(99)


def contar(mapa, tope=2):
    """Cuantas maneras hay de poner faroles (con cualquier numero de faroles), hasta tope.
    Decide casilla por casilla, en orden de lectura: farol o nada."""
    caso = caso_de(mapa, 0)
    piso, vista, turno = caso["piso"], caso["vista"], caso["turno"]
    num = mundo.numerados(caso)
    junto = caso["junto"]
    # para cada casilla, la ultima casilla (en orden) que podria alumbrarla
    ultima = {x: max([turno[x]] + [turno[v] for v in vista[x]]) for x in piso}
    muro_ultima = {w: max([turno[v] for v in junto[w]] + [-1]) for w in num}
    sol = []
    cuenta = [0]
    puestos = set()
    luz = {}

    def ok_hasta(i):
        # casillas que ya no pueden alumbrarse y muros que ya no pueden completarse
        for x in piso:
            if ultima[x] == i and luz.get(x, 0) == 0:
                return False
        for (w, k) in num.items():
            t = sum(1 for v in junto[w] if v in puestos)
            if t > k:
                return False
            if muro_ultima[w] <= i and t != k:
                return False
        return True

    for w in num:                                   # muros sin piso al lado
        if muro_ultima[w] == -1 and num[w] != 0:
            return 0

    def bus(i):
        if cuenta[0] >= tope:
            return
        if i == len(piso):
            cuenta[0] += 1
            sol.append(sorted(puestos))
            return
        x = piso[i]
        if luz.get(x, 0) == 0:                      # con farol (solo si nadie la alumbra)
            puestos.add(x)
            for v in [x] + vista[x]:
                luz[v] = luz.get(v, 0) + 1
            if ok_hasta(i):
                bus(i + 1)
            for v in [x] + vista[x]:
                luz[v] -= 1
            puestos.discard(x)
        if ok_hasta(i):                             # sin farol
            bus(i + 1)

    bus(0)
    return cuenta[0], sol


def pasos_g1(caso):
    """Los pasos de la generacion 1, contados sin correrla: cuantas maneras hay de poner
    los primeros k faroles en orden dejando sitio para los demas, sumadas sobre k."""
    from math import comb
    w, k = len(caso["piso"]), caso["faroles"]
    return sum(comb(w - k + j, j) for j in range(1, k + 1))


def medir(caso, agente, tope=None):
    bit = Bitacora("medir", grabar=False)
    bit.tope = tope
    try:
        s = agente.resolver(mundo, caso, bit)
    except StopIteration:
        return None, bit.cuenta
    return s, bit.cuenta


def fabricar(nivel):
    n, m, cuantos_muros, (kmin, kmax), tope_g1, semillas = PLANES[nivel]
    mejor = None
    for semilla in semillas:
        rnd = random.Random(1000 * nivel + semilla)
        todas = [(f, c) for f in range(n) for c in range(m)]
        muros = set(rnd.sample(todas, cuantos_muros))
        piso = [x for x in todas if x not in muros]
        vacio = caso_de(mapa_de(n, m, muros, {}), 0)
        # la solucion escondida
        orden = piso[:]
        rnd.shuffle(orden)
        sol = []
        luz = set()
        for x in orden:
            if x not in luz:
                sol.append(x)
                luz.update([x] + vacio["vista"][x])
        if not (kmin <= len(sol) <= kmax):
            continue
        puestos = set(sol)
        numeros = {w: sum(1 for v in vacio["junto"][w] if v in puestos) for w in muros}
        if contar(mapa_de(n, m, muros, numeros))[0] != 1:
            continue
        # borrar numeros mientras siga habiendo una sola solucion
        lista = sorted(numeros)
        rnd.shuffle(lista)
        for w in lista:
            prueba = dict(numeros)
            del prueba[w]
            if contar(mapa_de(n, m, muros, prueba))[0] == 1:
                numeros = prueba
        mapa = mapa_de(n, m, muros, numeros)
        caso = caso_de(mapa, len(sol))
        p1 = pasos_g1(caso)
        if p1 > tope_g1:
            continue
        s2, c2 = medir(caso, g2_con_hilo)
        if s2 != 1:
            continue
        razon = p1 / max(1, c2["avanzar"])
        if razon < 8:
            continue
        puntaje = (c2["avanzar"] - len(sol), c2["rechazar"])     # que la generacion 2 tenga que devolverse
        if mejor is None or puntaje > mejor[0]:
            mejor = (puntaje, mapa, len(sol), semilla, p1, c2["avanzar"], c2["rechazar"])
    if mejor is None:
        raise RuntimeError("Ninguna semilla sirvio para el nivel %d" % nivel)
    (_, mapa, k, semilla, p1, p2, t2) = mejor
    s1, c1 = medir(caso_de(mapa, k), g1_a_ciegas)              # la generacion 1 de verdad, una vez
    if s1 != 1 or c1["avanzar"] != p1:
        raise RuntimeError("La generacion 1 no dio lo esperado en el nivel %d: %r %r" % (nivel, s1, c1))
    print("nivel %d: semilla %d, %d faroles, G1 %d pasos, G2 %d pasos y %d tropiezos"
          % (nivel, semilla, k, p1, p2, t2))
    return {"titulo": "El apagón · nivel %d" % nivel, "mapa": mapa, "faroles": k}


def verificar(casos):
    """Comprueba con contar() que cada nivel tiene exactamente una solucion,
    y que esa solucion tiene el numero de faroles del nivel."""
    bien = True
    for nivel in sorted(casos):
        c = casos[nivel]
        total, sols = contar(c["mapa"], tope=5)
        k = len(sols[0]) if sols else -1
        estado = "bien" if (total == 1 and k == c["faroles"]) else "MAL"
        if estado != "bien":
            bien = False
        print("nivel %d: %d solución(es), %d faroles (el nivel dice %d)  %s" % (nivel, total, k, c["faroles"], estado))
    return bien


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        guardados = {k: v for (k, v) in casos_apagon.CASOS.items() if k != 99}
        sys.exit(0 if verificar(guardados) else 1)
    niveles = [int(a) for a in sys.argv[1:]] or sorted(PLANES)
    nuevos = {k: v for (k, v) in casos_apagon.CASOS.items() if k != 99}     # se copian antes de usar el 99
    for nivel in niveles:
        nuevos[nivel] = fabricar(nivel)
    if not verificar(nuevos):
        sys.exit("Algun nivel no tiene una sola solución: no se escribe nada.")
    with open(ARCHIVO, "w", encoding="utf-8") as fh:
        fh.write("# casos_apagon.py  ---  los niveles del apagón (datos, no programa)\n")
        fh.write("# Cada caso tiene una sola solución. Lo fabricó herramientas/generar_casos_apagon.py.\n")
        fh.write("# En el mapa: '.' es piso, '#' es un muro sin número y un dígito es un muro que dice\n")
        fh.write("# cuántos faroles lo tocan. 'faroles' es cuántos faroles hay que poner.\n")
        fh.write("CASOS = " + pprint.pformat(nuevos, width=100) + "\n")
    print("Escrito", ARCHIVO)
