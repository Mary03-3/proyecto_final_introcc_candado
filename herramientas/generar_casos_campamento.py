# generar_casos_campamento.py  ---  fabrica los niveles del campamento (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_campamento.py            fabrica, verifica y escribe casos_campamento.py
#       python3 herramientas/generar_casos_campamento.py verificar  solo verifica los niveles ya escritos
#
# Como se fabrica un nivel:
#   1. Se riegan al azar tantas carpas como excursionistas, sin que dos se toquen (ni en diagonal).
#   2. A cada carpa se le pone su arbol en una casilla pegada (norte, sur, oeste o este).
#   3. Los cupos de filas y columnas se cuentan de esas carpas.
#   4. Se cuentan TODAS las soluciones con un buscador exhaustivo. Si no es exactamente una, se descarta.
#   5. Entre los que tienen una sola solucion se escoge el que mejor separa las generaciones:
#      la generacion 1 mucho mas larga que la 2, y la 2 tropezando mucho mas que la 3.
# El archivo que escribe queda congelado en el repositorio.
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, os.path.join(RAIZ, "mundos", "campamento"))
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))
sys.path.insert(0, os.path.join(RAIZ, "referencia", "campamento"))

import casos_campamento          # noqa: E402
import mundo                     # noqa: E402
from bitacora import Bitacora    # noqa: E402
import g2_con_hilo               # noqa: E402
import g3_campamento             # noqa: E402

NOMBRES = ["Ana", "Bruno", "Carmen", "Darío", "Elisa", "Fidel", "Gloria", "Hernán", "Irene", "Jairo", "Lucía"]
TAMANOS = {1: (5, 4), 2: (6, 6), 3: (7, 8), 4: (8, 10)}        # nivel: (lado, excursionistas)
INTENTOS = {1: 400, 2: 400, 3: 600, 4: 400}
PASOS_G2 = {1: (5, 12), 2: (12, 30), 3: (30, 90), 4: (60, 400)}     # pasos de la generacion 2 que se buscan


def caso_de(datos):
    casos_campamento.CASOS[99] = datos
    return mundo.cargar(99)


def contar(caso, tope):
    """Cuenta las soluciones (hasta tope) probando TODAS las combinaciones, con retroceso.
    No usa ninguna regla del agente de la generacion 3: solo opciones y viola del mundo."""
    cuenta = [0]

    def bus(estado):
        if cuenta[0] >= tope:
            return
        if mundo.completo(caso, estado):
            cuenta[0] += 1
            return
        for d in mundo.opciones(caso, estado):
            nuevo = mundo.aplicar(caso, estado, d)
            if mundo.viola(caso, nuevo) == "":
                bus(nuevo)
    bus(mundo.inicio(caso))
    return cuenta[0]


def pasos_g1(caso):
    """Pasos y tropiezos de la generacion 1 sin correrla: recorre el arbol completo,
    asi que sus pasos son la suma de los productos de las ramas en cada nivel."""
    total, prod = 0, 1
    for p in caso["orden"]:
        prod *= len(mundo.junto_al_arbol(caso, p))
        total += prod
    return total, prod


def medir(caso, g):
    bit = Bitacora("medir", grabar=False)
    s = g.resolver(mundo, caso, bit)
    return s, bit.cuenta


def fabricar(nivel, rnd):
    n, k = TAMANOS[nivel]
    while True:
        carpas = []
        celdas = [(f, c) for f in range(n) for c in range(n)]
        rnd.shuffle(celdas)
        for x in celdas:
            if len(carpas) == k:
                break
            if all(abs(x[0] - y[0]) > 1 or abs(x[1] - y[1]) > 1 for y in carpas):
                carpas.append(x)
        if len(carpas) < k:
            continue
        arboles = []
        ok = True
        for (f, c) in carpas:
            lados = [(f + df, c + dc) for (df, dc) in ((-1, 0), (1, 0), (0, -1), (0, 1))]
            lados = [y for y in lados if 0 <= y[0] < n and 0 <= y[1] < n and y not in carpas and y not in arboles]
            if not lados:
                ok = False
                break
            arboles.append(rnd.choice(lados))
        if not ok:
            continue
        pares = sorted(zip(arboles, carpas))                  # los excursionistas, en orden de lectura de su arbol
        personas = NOMBRES[:k]
        datos = {"titulo": "El campamento · nivel %d" % nivel, "n": n,
                 "personas": personas,
                 "arboles": [list(a) for (a, _) in pares],
                 "cupo_filas": [sum(1 for x in carpas if x[0] == f) for f in range(n)],
                 "cupo_columnas": [sum(1 for x in carpas if x[1] == c) for c in range(n)],
                 "solucion": {personas[i]: list(pares[i][1]) for i in range(k)}}
        return datos


def puntaje(nivel, datos):
    """None si el nivel no sirve; si sirve, un numero: mas alto, mas trabajo le da a la generacion 2
    y mas reglas usa la 3 (siempre que la 1 quede muy por encima de la 2)."""
    caso = caso_de(datos)
    if contar(caso, 2) != 1:
        return None
    g1, _ = pasos_g1(caso)
    s2, c2 = medir(caso, g2_con_hilo)
    s3, c3 = medir(caso, g3_campamento)
    if s2 != 1 or s3 != 1:
        return None
    if c3["deducir"] == 0 or c2["rechazar"] < 2 * (c3["rechazar"] + 1):
        return None
    if nivel == 4 and g1 > 400000:                         # la generacion 1 debe terminar tambien aqui
        return None
    if nivel >= 2 and g1 < 8 * c2["avanzar"]:
        return None
    lo, hi = PASOS_G2[nivel]
    if not (lo <= c2["avanzar"] <= hi):                    # que la generacion 2 crezca de nivel en nivel
        return None
    return c2["rechazar"] + c3["deducir"] + c3["podar"]   # mas tropiezos de la 2 y mas reglas de la 3, mejor


def verificar(casos):
    print("%-6s %-5s %-5s %12s %9s %8s %9s %9s %8s %6s" % ("nivel", "lado", "gente", "soluciones", "g1 pasos",
                                                         "g2 pasos", "g2 tropi", "g3 pasos", "g3 ded", "g3 poda"))
    for nivel in sorted(casos):
        caso = caso_de(casos[nivel])
        s = contar(caso, 10)
        assert s == 1, "el nivel %d tiene %d soluciones" % (nivel, s)
        sol = {"carpas": {p: tuple(x) for (p, x) in casos[nivel]["solucion"].items()}}
        assert mundo.completo(caso, sol) and mundo.viola(caso, sol) == "", "la solucion guardada del nivel %d no sirve" % nivel
        g1, _ = pasos_g1(caso)
        _, c2 = medir(caso, g2_con_hilo)
        _, c3 = medir(caso, g3_campamento)
        print("%-6s %-5d %-5d %12d %9d %8d %9d %9d %8d %6d" % (nivel, caso["n"], len(caso["personas"]), s, g1,
                                                             c2["avanzar"], c2["rechazar"], c3["avanzar"], c3["deducir"], c3["podar"]))
    print("Todos los niveles tienen exactamente una solución.")


def escribir(casos):
    ruta = os.path.join(RAIZ, "mundos", "campamento", "casos_campamento.py")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("# casos_campamento.py  ---  los niveles del campamento (datos, no programa)\n")
        f.write("# Cada caso tiene una sola solucion. Lo fabrico herramientas/generar_casos_campamento.py.\n")
        f.write("# El arbol i es de la persona i. Los cupos dicen cuantas carpas hay en cada fila y columna.\n")
        f.write("# Para inventar un caso propio: copien uno, muevan los arboles, recalculen los cupos\n")
        f.write("# y comprueben con su agente que tiene exactamente una solucion.\n")
        f.write("CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")
    print("Escrito", os.path.relpath(ruta))


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        verificar({k: v for (k, v) in casos_campamento.CASOS.items() if k != 99})
        sys.exit(0)
    SEMILLAS = {1: 11, 2: 23, 3: 37, 4: 41}
    casos = {}
    for nivel in sorted(TAMANOS):
        rnd = random.Random(SEMILLAS[nivel])
        mejor, nota = None, None
        for _ in range(INTENTOS[nivel]):
            datos = fabricar(nivel, rnd)
            p = puntaje(nivel, datos)
            if p is not None and (nota is None or p > nota):
                mejor, nota = datos, p
        assert mejor is not None, "no salió ningún nivel %d que sirva" % nivel
        casos[nivel] = mejor
        print("nivel %d listo (puntaje %.1f)" % (nivel, nota))
    casos_campamento.CASOS.clear()
    casos_campamento.CASOS.update(casos)
    escribir(casos)
    verificar(casos)
