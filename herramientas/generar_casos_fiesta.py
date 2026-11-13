# generar_casos_fiesta.py  ---  fabrica los niveles de la fiesta (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_fiesta.py            fabrica y escribe mundos/fiesta/casos_fiesta.py
#       python3 herramientas/generar_casos_fiesta.py revisar    solo comprueba los niveles ya escritos
#
# Como se fabrica un nivel:
#   1. La mesa: una fila de k mesas, con sillas a lo largo (lado de la pared y lado de
#      la puerta) y una o dos cabeceras. Debajo, la fila de la puerta, donde esperan
#      los invitados que no se han sentado.
#   2. Una mesa solucion al azar: cada invitado en una silla.
#   3. Las pistas verdaderas: cada pareja que NO quedo junta puede pelearse, y cada
#      invitado puede pedir su lado (o la cabecera).
#   4. Se agregan pistas al azar hasta que la mesa sea la unica posible, y luego se
#      quitan las que sobran (primero las peticiones de lugar, despues las peleas).
#   5. Entre varias semillas se escoge la que cuenta mejor la historia: la generacion 1
#      visita al menos 5 veces mas estados que la 2 y, entre esas, la que mas separa a la 2
#      de la 3 (pasos de la 2 sobre pasos de la 3, por tropiezos de la 2 sobre podas de la 3).
# Cada nivel tiene una sola solucion: se comprueba probando TODAS las permutaciones.
import itertools
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, os.path.join(RAIZ, "mundos", "fiesta"))
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))
sys.path.insert(0, os.path.join(RAIZ, "referencia", "fiesta"))

INVITADOS = ["Amparo", "Benicio", "Clemencia", "Dámaso", "Eulalia", "Fermín", "Gertrudis", "Horacio"]

# nivel: (mesas en fila, cabecera izquierda, cabecera derecha) -> sillas = 2k + cabeceras
FORMAS = {1: (2, False, True), 2: (2, True, True), 3: (3, False, True), 4: (3, True, True)}
MAX_LINEAS = 9          # el panel de la pelicula agrupa las peleas por invitado y no da para mas lineas


def geometria(nivel):
    k, izq, der = FORMAS[nivel]
    columnas = k + 2
    sillas = [(0, c) for c in range(1, k + 1)]                 # lado de la pared, de izquierda a derecha
    if der:
        sillas.append((1, k + 1))                              # cabecera derecha
    sillas += [(2, c) for c in range(k, 0, -1)]                # lado de la puerta, de derecha a izquierda
    if izq:
        sillas.append((1, 0))                                  # cabecera izquierda
    mesa = [(1, c) for c in range(1, k + 1)]
    espera = [(3, c) for c in range(columnas)] + [(4, c) for c in range(columnas)]
    n = len(sillas)
    return dict(titulo="La fiesta · nivel %d" % nivel, filas=5, columnas=columnas,
                mesa=[list(x) for x in mesa], sillas=[list(x) for x in sillas],
                espera=[list(x) for x in espera[:n]], invitados=INVITADOS[:n])


import casos_fiesta          # noqa: E402
import mundo                 # noqa: E402


def caso_de(base, pistas):
    casos_fiesta.CASOS[99] = dict(base, pistas=pistas)
    return mundo.cargar(99)


def todas_las_mesas(caso, tope=None):
    """Todas las soluciones, probando cada permutacion (fuerza bruta: no hay atajos que puedan fallar)."""
    gente = caso["invitados"]
    halladas = []
    for perm in itertools.permutations(range(len(caso["sillas"]))):
        estado = {"silla": dict(zip(gente, perm))}
        if mundo.viola(caso, estado) == "":
            halladas.append(perm)
            if tope and len(halladas) >= tope:
                break
    return halladas


def contar(caso, tope=None):
    """Cuenta soluciones con retroceso (rapido); se usa mientras se fabrica."""
    gente = caso["invitados"]
    n = len(caso["sillas"])
    cuenta = [0]

    def bus(i, silla):
        if tope and cuenta[0] >= tope:
            return
        if i == len(gente):
            cuenta[0] += 1
            return
        usadas = set(silla.values())
        for s in range(n):
            if s in usadas:
                continue
            silla[gente[i]] = s
            if mundo.viola(caso, {"silla": silla}) == "":
                bus(i + 1, silla)
            del silla[gente[i]]
    bus(0, {})
    return cuenta[0]


def fabricar(nivel, semilla):
    base = geometria(nivel)
    rnd = random.Random(semilla)
    vacio = caso_de(base, [])
    gente = vacio["invitados"]
    n = len(gente)
    perm = list(range(n))
    rnd.shuffle(perm)
    silla = dict(zip(gente, perm))
    peleas, lugares = [], []
    for i in range(n):
        for j in range(i + 1, n):
            a, b = gente[i], gente[j]
            if silla[b] not in vacio["junto_a"][silla[a]]:
                peleas.append(["pelea", a, b])
    for p in gente:
        ld = mundo.lado(vacio, silla[p])
        if ld != "cabecera":
            lugares.append(["lado", p, ld])
        elif FORMAS[nivel][1] and FORMAS[nivel][2]:
            lugares.append(["cabecera", p, mundo.cual_cabecera(vacio, silla[p])])
        else:
            lugares.append(["cabecera", p])
    rnd.shuffle(peleas)
    rnd.shuffle(lugares)
    pozo = peleas + lugares[:3]                       # pocas peticiones de lugar: casi todo son peleas
    rnd.shuffle(pozo)
    elegidas = []
    for pista in pozo:
        elegidas.append(pista)
        if contar(caso_de(base, elegidas), tope=2) == 1:
            break
    else:
        return None
    # quitar lo que sobra: primero las peticiones de lugar, despues las peleas
    for pista in [x for x in elegidas if x[0] != "pelea"] + [x for x in elegidas if x[0] == "pelea"]:
        prueba = [x for x in elegidas if x is not pista]
        if contar(caso_de(base, prueba), tope=2) == 1:
            elegidas = prueba
    orden = {p: i for i, p in enumerate(gente)}
    elegidas.sort(key=lambda x: (x[0] != "pelea", orden[x[1]], orden.get(x[2], 0) if len(x) > 2 else 0))
    return dict(base, pistas=elegidas, solucion={p: silla[p] for p in gente})


def medir(caso):
    """Pasos y tropiezos de las tres generaciones (sin grabar)."""
    from bitacora import Bitacora
    import g1_a_ciegas
    import g2_con_hilo
    import g3_fiesta
    fila = []
    for g in (g1_a_ciegas, g2_con_hilo, g3_fiesta):
        bit = Bitacora("medir", grabar=False)
        s = g.resolver(mundo, caso, bit)
        fila.append((s, bit.cuenta["avanzar"], bit.cuenta["rechazar"], bit.cuenta["deducir"], bit.cuenta["podar"]))
    return fila


def puntaje(m):
    (s1, a1, r1, _, _), (s2, a2, r2, _, _), (s3, a3, r3, d3, p3) = m
    if not (s1 == s2 == s3 == 1) or a1 < 5 * a2:
        return None
    return (a2 / max(a3, 1)) * (r2 / max(r3 + p3, 1))


def revisar():
    print("%-6s %-8s %-7s %s" % ("nivel", "sillas", "pistas", "soluciones (todas las permutaciones)"))
    bien = True
    for nivel in mundo.casos():
        caso = mundo.cargar(nivel)
        mesas = todas_las_mesas(caso)
        esperada = tuple(caso["solucion"][p] for p in caso["invitados"])
        ok = len(mesas) == 1 and mesas[0] == esperada
        bien = bien and ok
        print("%-6s %-8d %-7d %d %s" % (nivel, len(caso["sillas"]), len(caso["pistas"]), len(mesas),
                                       "bien" if ok else "MAL"))
    print("Todos los niveles tienen exactamente una solución." if bien else "HAY NIVELES CON PROBLEMAS.")
    return bien


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "revisar":
        sys.exit(0 if revisar() else 1)
    intentos = {1: 60, 2: 60, 3: 80, 4: 25}
    casos = {}
    for nivel in sorted(FORMAS):
        mejor, mejor_p, mejor_s = None, -1, None
        for semilla in range(intentos[nivel]):
            caso = fabricar(nivel, 1000 * nivel + semilla)
            if caso is None or len(mundo.renglones(caso_de(caso, caso["pistas"]))) > MAX_LINEAS:
                continue
            if sum(1 for x in caso["pistas"] if x[0] == "pelea") < len(caso["pistas"]) - 3:
                continue
            m = medir(caso_de(caso, caso["pistas"]))
            p = puntaje(m)
            if p is not None and p > mejor_p:
                mejor, mejor_p, mejor_s, mejor_m = caso, p, semilla, m
        if mejor is None:
            raise SystemExit("No salió ningún caso para el nivel %d" % nivel)
        print("nivel %d: semilla %d, %d pistas, medida %s" % (nivel, mejor_s, len(mejor["pistas"]), mejor_m))
        casos[nivel] = mejor
    destino = os.path.join(RAIZ, "mundos", "fiesta", "casos_fiesta.py")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("# casos_fiesta.py  ---  los niveles de la fiesta (datos, no programa)\n")
        f.write("# Cada caso tiene una sola mesa posible. Lo fabrico herramientas/generar_casos_fiesta.py.\n")
        f.write("# Casillas: (fila, columna) desde 0. Las sillas van en orden alrededor de la mesa;\n")
        f.write("# 'espera' es donde aguarda cada invitado antes de sentarse; 'solucion' da la silla de cada uno.\n")
        f.write("CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")
    print("Escrito", os.path.relpath(destino))
    import importlib
    importlib.reload(casos_fiesta)
    mundo.CASOS = casos_fiesta.CASOS
    revisar()


if __name__ == "__main__":
    main()
