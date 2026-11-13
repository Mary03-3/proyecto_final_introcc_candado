# mundo.py  ---  La cueva
#
# LA FICCION. Pixie entra a una cueva a buscar el cofre, que brilla a lo lejos:
# sabe DONDE esta, pero no por donde se llega. En la cueva hay pozos que no se
# ven hasta que ya es tarde. Lo unico que avisa es la BRISA: en toda casilla
# vecina a un pozo se siente aire. Y el farol tiene aceite para un numero
# contado de pasos. La pregunta: ¿por donde llega Pixie al cofre sin caer y
# antes de que se apague el farol?
#
# Cumple el mismo contrato que los demas mundos (ver CONTRATO.md).
# Un ESTADO es un diccionario:
#   {"camino": [(5, 1), (4, 1), (3, 1)]}       las casillas pisadas, en orden; la ultima es donde esta Pixie
# El agente puede agregar, para que se vea en la escena:
#   "peligro": [(1, 3)]                         casillas donde sabe o dedujo que hay un pozo
#   "seguras": [(2, 2)]                         casillas que dedujo que son seguras
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_cueva import CASOS             # noqa: E402


def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["n"] = len(caso["mapa"])
    caso["pozos"] = set()
    for f in range(caso["n"]):
        for c in range(caso["n"]):
            letra = caso["mapa"][f][c]
            if letra == "E":
                caso["entrada"] = (f, c)
            if letra == "C":
                caso["cofre"] = (f, c)
            if letra == "O":
                caso["pozos"].add((f, c))
    return caso


# ----------------------------------------------------------------- lo que se puede preguntar de la cueva
def abierta(caso, casilla):
    """¿Se puede pisar la casilla? (Un pozo tambien se puede pisar: ese es el problema.)"""
    f, c = casilla
    return 0 <= f < caso["n"] and 0 <= c < caso["n"] and caso["mapa"][f][c] != "#"


def vecinas(caso, casilla):
    """Las casillas abiertas que tocan a esta: norte, este, sur, oeste."""
    f, c = casilla
    return [v for v in ((f - 1, c), (f, c + 1), (f + 1, c), (f, c - 1)) if abierta(caso, v)]


def brisa(caso, casilla):
    """Lo que Pixie percibe parado en la casilla: ¿hay brisa? (Hay brisa si alguna vecina es un pozo.)"""
    for v in vecinas(caso, casilla):
        if v in caso["pozos"]:
            return True
    return False


def distancia(a, b):
    """Cuantos pasos hay, como minimo, entre dos casillas (sin contar rocas)."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def aceite(caso, estado):
    """Cuantos pasos le quedan al farol."""
    return caso["aceite"] - (len(estado["camino"]) - 1)


# ----------------------------------------------------------------- el contrato
def inicio(caso):
    return {"camino": [caso["entrada"]]}


def opciones(caso, estado):
    """Los pasos posibles: a una vecina abierta que no este ya en el camino. No mira nada mas."""
    aqui = estado["camino"][-1]
    if aqui == caso["cofre"] or aceite(caso, estado) <= 0:
        return []
    return [v for v in vecinas(caso, aqui) if v not in estado["camino"]]


def completo(caso, estado):
    return len(opciones(caso, estado)) == 0


def aplicar(caso, estado, decision):
    return {"camino": estado["camino"] + [decision]}


def viola(caso, estado):
    for casilla in estado["camino"]:
        if casilla in caso["pozos"]:
            return "cayó en un pozo"
    if estado["camino"][-1] != caso["cofre"]:
        if aceite(caso, estado) <= 0:
            return "se apagó el farol"
        if completo(caso, estado):
            return "callejón sin salida"
    return ""


def decir(caso, decision):
    return "paso a la fila %d, columna %d" % (decision[0] + 1, decision[1] + 1)


def respuesta(caso, estado):
    if estado["camino"][-1] == caso["cofre"] and viola(caso, estado) == "":
        return "Pixie llegó al cofre en %d pasos" % (len(estado["camino"]) - 1)
    return ""


def pistas(caso):
    return ["El farol alcanza para %d pasos." % caso["aceite"],
            "En toda casilla vecina a un pozo se siente brisa.",
            "Donde no hay brisa, las casillas vecinas son seguras."]


def dibujar(caso, estado):
    n = caso["n"]
    e = Escena(n, n, titulo=caso["titulo"], ambiente=caso.get("ambiente", "sala"))
    e.salida(caso["entrada"][0], caso["entrada"][1])
    e.meta(caso["cofre"][0], caso["cofre"][1])
    for f in range(n):
        for c in range(n):
            if caso["mapa"][f][c] == "#":
                e.roca(f, c)
            elif (f, c) in caso["pozos"]:
                e.hueco(f, c)
            else:
                e.piso(f, c, "#7a6a58" if caso.get("ambiente") == "cueva" else "#5a5b5f")
    camino = estado["camino"]
    e.cofre(caso["cofre"][0], caso["cofre"][1])
    e.hilo(camino)
    for casilla in camino:
        if casilla not in caso["pozos"] and brisa(caso, casilla):
            e.brisa(casilla[0], casilla[1])
    for casilla in estado.get("seguras", []):
        if casilla not in camino:
            e.luz(casilla[0], casilla[1], "#4fd08a")
    for casilla in estado.get("peligro", []):
        e.runa(casilla[0], casilla[1])
    e.conejo(camino[-1][0], camino[-1][1])
    e.medidor("aceite", aceite(caso, estado), caso["aceite"])
    quien = respuesta(caso, estado)
    if quien:
        e.veredicto(quien)
    return e
