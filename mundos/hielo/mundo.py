# mundo.py  ---  La pista de hielo
#
# LA FICCION. Pixie quedo encerrado en una pista de hielo y quiere llegar a la
# salida. El problema es que en el hielo no se camina: se toma impulso hacia
# un lado y se DESLIZA en linea recta hasta chocar con una roca o con la baranda.
# Pasar por encima de la salida no sirve; hay que frenar justo ahi. En la pista
# hay huecos de agua: si Pixie pasa por uno, se hunde. Y las fuerzas le alcanzan
# para un numero contado de impulsos. La pregunta: ¿como llega Pixie a la salida
# si solo frena al chocar?
#
# Cumple el mismo contrato que los demas mundos (ver CONTRATO.md).
# Una DECISION es un deslizamiento: (direccion, casilla donde frena), por ejemplo ("norte", (1, 4)).
# Un ESTADO es un diccionario:
#   {"camino": [(7, 1), (1, 1), (1, 4)]}       las casillas donde Pixie freno, en orden; la ultima es donde esta
# El agente puede agregar, para que se vea en la escena:
#   "muertas": [(3, 5)]                        casillas desde las que dedujo que no se llega a la salida
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_hielo import CASOS             # noqa: E402

DIRECCIONES = (("norte", -1, 0), ("este", 0, 1), ("sur", 1, 0), ("oeste", 0, -1))
PARED = "#2b9aa8"            # el color de las paredes de la pista (cian de hielo)
HIELO = "#a9d6e8"            # el color del piso


def casos():
    return sorted(CASOS)


def preparar(datos):
    """Convierte los datos de un nivel (mapa e impulsos) en un caso listo para buscar."""
    caso = dict(datos)
    caso["n"] = len(caso["mapa"])
    caso["agua"] = set()
    for f in range(caso["n"]):
        for c in range(caso["n"]):
            letra = caso["mapa"][f][c]
            if letra == "E":
                caso["entrada"] = (f, c)
            if letra == "S":
                caso["salida"] = (f, c)
            if letra == "O":
                caso["agua"].add((f, c))
    return caso


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = preparar(CASOS[nivel])
    caso["nivel"] = nivel
    return caso


# ----------------------------------------------------------------- lo que se puede preguntar de la pista
def libre(caso, casilla):
    """¿Se puede pasar por la casilla? (El agua tambien se puede pisar: ese es el problema.)"""
    f, c = casilla
    return 0 <= f < caso["n"] and 0 <= c < caso["n"] and caso["mapa"][f][c] != "#"


def deslizar(caso, casilla, direccion):
    """Donde frena Pixie si toma impulso desde la casilla hacia esa direccion.
    Frena en la ultima casilla antes de una roca. Si pasa por agua, se hunde ahi.
    Si la casilla vecina ya es roca, no se mueve y devuelve la misma casilla."""
    df, dc = [(a, b) for (nombre, a, b) in DIRECCIONES if nombre == direccion][0]
    f, c = casilla
    while libre(caso, (f + df, c + dc)):
        f, c = f + df, c + dc
        if (f, c) in caso["agua"]:
            break
    return (f, c)


def recorrido(caso, desde, hasta):
    """Las casillas por las que pasa un deslizamiento en linea recta, sin contar la de partida."""
    df = (hasta[0] > desde[0]) - (hasta[0] < desde[0])
    dc = (hasta[1] > desde[1]) - (hasta[1] < desde[1])
    casillas = []
    f, c = desde
    while (f, c) != hasta:
        f, c = f + df, c + dc
        casillas.append((f, c))
    return casillas


def destinos(caso, casilla):
    """Los deslizamientos que mueven a Pixie desde la casilla: lista de (direccion, donde frena)."""
    lista = []
    for (nombre, _, _) in DIRECCIONES:
        fin = deslizar(caso, casilla, nombre)
        if fin != casilla:
            lista.append((nombre, fin))
    return lista


def impulsos(caso, estado):
    """Cuantos impulsos le quedan a Pixie."""
    return caso["impulsos"] - (len(estado["camino"]) - 1)


def en_linea(a, b):
    """¿Las dos casillas estan en la misma fila o en la misma columna?"""
    return a[0] == b[0] or a[1] == b[1]


# ----------------------------------------------------------------- el contrato
def inicio(caso):
    return {"camino": [caso["entrada"]]}


def opciones(caso, estado):
    """Los deslizamientos posibles: los que mueven a Pixie a una casilla donde no haya frenado ya.
    No mira nada mas: ni el agua, ni si por ahi se llega."""
    aqui = estado["camino"][-1]
    if aqui == caso["salida"] or impulsos(caso, estado) <= 0:
        return []
    return [d for d in destinos(caso, aqui) if d[1] not in estado["camino"]]


def completo(caso, estado):
    return len(opciones(caso, estado)) == 0


def aplicar(caso, estado, decision):
    return {"camino": estado["camino"] + [decision[1]]}


def viola(caso, estado):
    for casilla in estado["camino"]:
        if casilla in caso["agua"]:
            return "se hundió en el agua"
    if estado["camino"][-1] != caso["salida"]:
        if impulsos(caso, estado) <= 0:
            return "se le acabaron los impulsos"
        if completo(caso, estado):
            return "no tiene a dónde deslizarse"
    return ""


def decir(caso, decision):
    direccion, (f, c) = decision
    return "se desliza al %s hasta la fila %d, columna %d" % (direccion, f + 1, c + 1)


def direcciones_de(estado):
    """Las direcciones de cada deslizamiento del camino, en orden."""
    camino = estado["camino"]
    lista = []
    for i in range(1, len(camino)):
        (f1, c1), (f2, c2) = camino[i - 1], camino[i]
        if f2 < f1:
            lista.append("norte")
        elif f2 > f1:
            lista.append("sur")
        elif c2 > c1:
            lista.append("este")
        else:
            lista.append("oeste")
    return lista


def respuesta(caso, estado):
    if estado["camino"][-1] == caso["salida"] and viola(caso, estado) == "":
        pasos = direcciones_de(estado)
        return "Pixie sale con %d deslizamientos: %s" % (len(pasos), ", ".join(pasos))
    return ""


def pistas(caso):
    return ["Pixie solo frena al chocar con una roca o con la baranda.",
            "Si pasa por un hueco de agua, se hunde.",
            "Le alcanzan las fuerzas para %d impulsos." % caso["impulsos"]]


def dibujar(caso, estado):
    n = caso["n"]
    e = Escena(n, n, titulo=caso["titulo"], ambiente=caso.get("ambiente", "sala"), pared=PARED)
    e.salida(caso["entrada"][0], caso["entrada"][1])
    e.meta(caso["salida"][0], caso["salida"][1])
    for f in range(n):
        for c in range(n):
            if caso["mapa"][f][c] == "#":
                e.roca(f, c)
            elif (f, c) in caso["agua"]:
                e.hueco(f, c)
            else:
                e.piso(f, c, HIELO)
    camino = estado["camino"]
    e.hilo(camino)
    for casilla in estado.get("muertas", []):
        if casilla != camino[-1]:
            e.equis(casilla[0], casilla[1])
    e.conejo(camino[-1][0], camino[-1][1])
    e.medidor("impulsos", impulsos(caso, estado), caso["impulsos"])
    frase = respuesta(caso, estado)
    if frase:
        e.veredicto(frase)
    return e
