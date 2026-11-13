# generar_casos_vecindario.py  ---  fabrica y verifica los niveles del vecindario (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_vecindario.py            fabrica los cuatro niveles y los escribe
#       python3 herramientas/generar_casos_vecindario.py verificar  solo cuenta las soluciones de casos_vecindario.py
#
# Como se fabrica un nivel:
#   1. Se elige al azar una solucion: a cada categoria se le baraja el orden de las casas.
#   2. Se escriben TODAS las pistas verdaderas de esa solucion (en, mismo, distinto, junto,
#      izquierda, antes). Se excluyen las que regalan la respuesta: «X tiene el conejo»
#      y «el conejo vive en la casa k».
#   3. Se barajan y se van agregando las que reducen el numero de soluciones, hasta que queda una.
#   4. Se quitan las que sobran: si sin una pista la solucion sigue siendo unica, se quita.
#   5. Se cuentan las soluciones con un programa (no a ojo) y se exige que sea exactamente 1.
# El archivo que escribe queda congelado en el repositorio.
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "Recursos"))
sys.path.insert(0, os.path.join(AQUI, "..", "mundos", "vecindario"))

import mundo                   # noqa: E402
import casos_vecindario        # noqa: E402

PERSONAS = ["Aurelio", "Bárbara", "Celmira", "Domingo", "Etelvina"]
MASCOTAS = ["conejo", "perro", "gato", "loro", "tortuga"]
COLORES = ["roja", "azul", "amarilla", "verde", "blanca"]
BEBIDAS = ["tinto", "aguapanela", "chocolate", "avena", "limonada"]


def base(nivel, casas, con_color, con_bebida):
    cats = [["mascota", MASCOTAS[:casas]]]
    if con_color:
        cats.append(["color", COLORES[:casas]])
    cats.append(["persona", PERSONAS[:casas]])
    if con_bebida:
        cats.append(["bebida", BEBIDAS[:casas]])
    return {"titulo": "El vecindario · nivel %d" % nivel, "casas": casas, "categorias": cats}


PLANOS = {
    1: base(1, 3, False, False),
    2: base(2, 3, True, False),
    3: base(3, 4, True, False),
    4: base(4, 5, True, False),
}
SEMILLAS = {1: 1, 2: 1, 3: 1, 4: 1}


def caso_de(plano, pistas):
    casos_vecindario.CASOS[99] = dict(plano, pistas=[list(p) for p in pistas])
    return mundo.cargar(99)


def contar(caso, tope):
    """Cuenta las soluciones (hasta tope) con retroceso, en el orden del mundo.
    Revisa las pistas apenas se pueden revisar (como la generacion 2, pero sin bitacora)."""
    orden = caso["orden"]
    n = caso["n"]
    cuenta = [0]

    def bus(i, casa, usadas):
        if cuenta[0] >= tope:
            return
        if i == len(orden):
            cuenta[0] += 1
            return
        cosa = orden[i]
        cat = caso["de"][cosa]
        for k in range(n):
            if (cat, k) in usadas:
                continue
            casa[cosa] = k
            usadas.add((cat, k))
            if mundo.choca(caso, casa) == "":
                bus(i + 1, casa, usadas)
            usadas.discard((cat, k))
            del casa[cosa]

    bus(0, {}, set())
    return cuenta[0]


def todas_las_pistas(caso, sol, rnd):
    """Todas las pistas verdaderas de la solucion, sin las que regalan la respuesta."""
    pozo = []
    orden = caso["orden"]
    de = caso["de"]
    for x in orden:
        if x != mundo.CONEJO:
            pozo.append(("en", x, sol[x]))
    for x in orden:
        for y in orden:
            if x == y:
                continue
            regalo = mundo.CONEJO in (x, y) and "persona" in (de[x], de[y])
            if orden.index(x) < orden.index(y) and de[x] != de[y]:
                if sol[x] == sol[y]:
                    if not regalo:
                        pozo += [("mismo", x, y)] * 2
                else:
                    pozo.append(("distinto", x, y))
            if abs(sol[x] - sol[y]) == 1 and orden.index(x) < orden.index(y):
                pozo += [("junto", x, y)] * 2
            if sol[x] == sol[y] - 1:
                pozo += [("izquierda", x, y)] * 2
            if sol[x] < sol[y] - 1:
                pozo += [("antes", x, y)] * 2
    rnd.shuffle(pozo)
    return pozo


def fabricar(nivel, semilla):
    plano = PLANOS[nivel]
    rnd = random.Random(semilla)
    vacio = caso_de(plano, [])
    n = vacio["n"]
    # 1. una solucion al azar
    sol = {}
    for (_, lista) in vacio["categorias"]:
        casas = list(range(n))
        rnd.shuffle(casas)
        for (cosa, k) in zip(lista, casas):
            sol[cosa] = k
    # 2. todas las pistas verdaderas
    pozo = todas_las_pistas(vacio, sol, rnd)
    # 3. agregar las que reducen las soluciones hasta que quede una
    TOPE = 500
    elegidas = []
    actual = contar(caso_de(plano, elegidas), TOPE)
    for pista in pozo:
        if actual == 1:
            break
        if pista in elegidas:
            continue
        nuevo = contar(caso_de(plano, elegidas + [pista]), TOPE)
        if nuevo < actual or actual >= TOPE:
            elegidas.append(pista)
            actual = nuevo
    assert actual == 1, "no se logro solucion unica"
    # 4. quitar las que sobran
    for pista in list(elegidas):
        resto = [x for x in elegidas if x != pista]
        if contar(caso_de(plano, resto), 2) == 1:
            elegidas = resto
    orden = vacio["orden"]
    elegidas.sort(key=lambda p: (["en", "mismo", "distinto", "junto", "izquierda", "antes"].index(p[0]),
                                 orden.index(p[1])))
    caso = caso_de(plano, elegidas)
    dueno = mundo.dueno_del_conejo(caso, sol)
    return dict(plano, pistas=[list(p) for p in elegidas], solucion=dict(sol), dueno=dueno)


def verificar(casos):
    """Cuenta las soluciones de cada nivel y exige que sea exactamente una, y que sea la anotada."""
    bien = True
    for nivel in sorted(casos):
        casos_vecindario.CASOS[nivel] = casos[nivel]
        caso = mundo.cargar(nivel)
        s = contar(caso, 10)
        anotada = casos[nivel]["solucion"]
        valida = mundo.viola(caso, {"casa": dict(anotada)}) == "" and len(anotada) == len(caso["orden"])
        print("nivel %d | casas %d | cosas %d | pistas %2d | soluciones %d | la anotada cumple: %s | el conejo es de %s"
              % (nivel, caso["n"], len(caso["orden"]), len(caso["pistas"]), s, "sí" if valida else "NO",
                 casos[nivel]["dueno"]))
        bien = bien and s == 1 and valida
    print("TODOS LOS NIVELES TIENEN EXACTAMENTE UNA SOLUCION" if bien else "HAY NIVELES CON PROBLEMAS")
    return bien


def escribir(casos):
    with open(os.path.join(AQUI, "..", "mundos", "vecindario", "casos_vecindario.py"), "w", encoding="utf-8") as f:
        f.write("# casos_vecindario.py  ---  los niveles del vecindario (datos, no programa)\n"
                "# Cada caso tiene una sola solucion. Lo fabrico y lo verifico herramientas/generar_casos_vecindario.py.\n"
                "# Las casas se numeran desde 0 en el codigo y desde 1 en pantalla.\n"
                "# Tipos de pista: ['en', x, k]  ['mismo', x, y]  ['distinto', x, y]  ['junto', x, y]\n"
                "#                 ['izquierda', x, y] (x JUSTO a la izquierda de y)  ['antes', x, y] (x en algun lugar a la izquierda de y)\n"
                "CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")
    print("escrito casos_vecindario.py")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        ok = verificar(dict(casos_vecindario.CASOS))
        sys.exit(0 if ok else 1)
    casos = {}
    for nivel in sorted(PLANOS):
        casos[nivel] = fabricar(nivel, SEMILLAS[nivel])
    casos_vecindario.CASOS.pop(99, None)
    if not verificar(casos):
        sys.exit(1)
    casos_vecindario.CASOS.pop(99, None)
    escribir(casos)
