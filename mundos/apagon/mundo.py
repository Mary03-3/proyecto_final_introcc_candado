# mundo.py  ---  El apagon (faroles)
#
# LA FICCION. Se fue la luz en el salon del pueblo y esta noche hay baile. Pixie
# tiene un numero contado de faroles. Un farol alumbra su casilla y toda su fila
# y su columna, hasta que topa con un muro. Hay tres reglas:
#   1. Todo el piso tiene que quedar alumbrado.
#   2. Ningun farol puede alumbrar a otro (se encandilan).
#   3. Un muro con numero dice cuantos faroles lo tocan (arriba, abajo, izquierda
#      o derecha). Un muro sin numero no dice nada.
# La pregunta: ¿donde van las lamparas?
#
# Cumple el mismo contrato que los demas mundos (ver CONTRATO.md).
#
# Un ESTADO es un diccionario:
#   {"faroles": [(0, 2), (1, 4)]}     los faroles puestos, en el orden de lectura del salon
# Las casillas del piso se recorren como se lee: de izquierda a derecha y de arriba
# abajo. Cada decision es "el siguiente farol va en tal casilla", siempre mas adelante
# que el anterior. Las casillas que quedaron atras sin farol ya no lo tendran.
# El agente puede agregar, para que se vea en la escena:
#   "tachadas": [(0, 3)]       casillas donde ya sabe que no puede ir un farol
#   "foco": (2, 1)             la casilla que esta mirando
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_apagon import CASOS            # noqa: E402

PARED = "#5b3a8c"          # morado de noche: el color propio del apagon
PISO = "#33363f"           # el piso a oscuras
COLOR_FAROL = "#ffd23f"
COLOR_NUMERO = "#1f2430"


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    mapa = caso["mapa"]
    caso["n"] = len(mapa)
    caso["m"] = len(mapa[0])
    caso["piso"] = []                     # las casillas del piso, en orden de lectura
    caso["muros"] = {}                    # muro -> numero (None si no tiene)
    for f in range(caso["n"]):
        for c in range(caso["m"]):
            letra = mapa[f][c]
            if letra == ".":
                caso["piso"].append((f, c))
            elif letra == "#":
                caso["muros"][(f, c)] = None
            else:
                caso["muros"][(f, c)] = int(letra)
    caso["turno"] = {x: i for (i, x) in enumerate(caso["piso"])}
    caso["vista"] = {x: _vista(caso, x) for x in caso["piso"]}
    caso["junto"] = {w: vecinas_de_piso(caso, w) for w in caso["muros"]}
    return caso


# ----------------------------------------------------------------- lo que se puede preguntar del salon
def es_piso(caso, casilla):
    f, c = casilla
    return 0 <= f < caso["n"] and 0 <= c < caso["m"] and caso["mapa"][f][c] == "."


def _vista(caso, casilla):
    vistas = []
    for (df, dc) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        f, c = casilla[0] + df, casilla[1] + dc
        while es_piso(caso, (f, c)):
            vistas.append((f, c))
            f, c = f + df, c + dc
    return vistas


def alumbra(caso, farol):
    """Las casillas que alumbra un farol puesto en esa casilla, sin contarla a ella."""
    return caso["vista"][farol]


def vecinas_de_piso(caso, casilla):
    """Las casillas de piso que tocan a esta: norte, sur, oeste, este."""
    f, c = casilla
    return [v for v in ((f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)) if es_piso(caso, v)]


def numerados(caso):
    """Los muros con numero: {(f, c): numero}."""
    return {w: k for (w, k) in caso["muros"].items() if k is not None}


def alumbradas(caso, faroles):
    """Todas las casillas con luz, contando las de los faroles."""
    luz = set(faroles)
    for x in faroles:
        luz.update(caso["vista"][x])
    return luz


def decidida(caso, estado, casilla):
    """¿Ya quedo atras esa casilla? (Las casillas se deciden en orden de lectura.)"""
    if not estado["faroles"]:
        return False
    if completo(caso, estado):
        return True
    return caso["turno"][casilla] <= caso["turno"][estado["faroles"][-1]]


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"faroles": []}


def completo(caso, estado):
    return len(estado["faroles"]) == caso["faroles"]


def opciones(caso, estado):
    """Donde puede ir el siguiente farol: cualquier casilla de piso mas adelante que el
    ultimo, dejando sitio para los que faltan. No mira ninguna regla."""
    faltan = caso["faroles"] - len(estado["faroles"])
    if faltan == 0:
        return []
    desde = caso["turno"][estado["faroles"][-1]] + 1 if estado["faroles"] else 0
    hasta = len(caso["piso"]) - faltan
    return caso["piso"][desde:hasta + 1]


def aplicar(caso, estado, casilla):
    return {"faroles": estado["faroles"] + [casilla]}


def problema(caso, estado):
    """La regla rota y las casillas donde se ve. ("", []) si nada se rompio."""
    faroles = estado["faroles"]
    puestos = set(faroles)
    for x in faroles:                                                   # regla 2
        for v in caso["vista"][x]:
            if v in puestos:
                return ("los faroles de %s y %s se encandilan" % (_casilla(x), _casilla(v)), [x, v])
    for (w, k) in numerados(caso).items():                              # regla 3
        tiene = sum(1 for v in caso["junto"][w] if v in puestos)
        if tiene > k:
            return ("el muro de %s pide %d y ya toca %d" % (_casilla(w), k, tiene), [w])
        if tiene < k and all(decidida(caso, estado, v) for v in caso["junto"][w]):
            return ("el muro de %s pide %d y se quedó con %d" % (_casilla(w), k, tiene), [w])
    luz = alumbradas(caso, faroles)
    for x in caso["piso"]:                                              # regla 1
        if x in luz or not decidida(caso, estado, x):
            continue
        if all(decidida(caso, estado, v) for v in caso["vista"][x]):
            return ("%s quedó a oscuras" % _casilla(x).capitalize(), [x])
    return ("", [])


def viola(caso, estado):
    """Devuelve "" si el estado no rompe ninguna regla; si no, cual rompio."""
    return problema(caso, estado)[0]


def _casilla(x):
    return "la fila %d, columna %d" % (x[0] + 1, x[1] + 1)


def decir(caso, casilla):
    return "farol en %s" % _casilla(casilla)


def respuesta(caso, estado):
    if not completo(caso, estado) or viola(caso, estado):
        return ""
    lista = ", ".join("%d·%d" % (f + 1, c + 1) for (f, c) in estado["faroles"])
    return "Faroles en %s (fila·columna)" % lista


def pistas(caso):
    lineas = ["Hay %d faroles" % caso["faroles"],
              "Todo el piso queda alumbrado",
              "Ningún farol alumbra a otro"]
    for (w, k) in sorted(numerados(caso).items()):
        lineas.append("El muro de %s toca %d farol%s" % (_casilla(w), k, "" if k == 1 else "es"))
    return lineas


# ----------------------------------------------------------------- la escena
def dibujar(caso, estado):
    e = Escena(caso["n"], caso["m"], titulo=caso["titulo"], ambiente="sala", pared=PARED)
    for (f, c) in caso["piso"]:
        e.piso(f, c, PISO)
    for (w, k) in sorted(caso["muros"].items()):
        e.roca(w[0], w[1])
    faroles = estado["faroles"]
    for x in sorted(alumbradas(caso, faroles)):
        e.luz(x[0], x[1], COLOR_FAROL)
    for x in estado.get("tachadas", []):
        if x not in faroles:
            e.equis(x[0], x[1])
    foco = estado.get("foco")
    if foco is not None and tuple(foco) not in faroles and tuple(foco) not in caso["muros"]:
        e.runa(foco[0], foco[1], "#ffb02e")             # la casilla que se esta mirando
    for (f, c) in faroles:
        e.caja("farol %d,%d" % (f, c), f, c, COLOR_FAROL)
    _, malas = problema(caso, estado)
    for x in malas:
        e.runa(x[0], x[1])
    for (w, k) in sorted(numerados(caso).items()):
        e.ficha(w[0], w[1], str(k), COLOR_NUMERO)
    e.medidor("faroles", caso["faroles"] - len(faroles), caso["faroles"])
    quien = respuesta(caso, estado)
    if quien:
        e.veredicto(quien)
    return e
