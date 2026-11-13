# mundo.py  ---  El trasteo (encajar muebles en el camion)
#
# LA FICCION. Pixie se muda y el camion ya llego. El piso del camion es una
# cuadricula; algunas casillas ya estan ocupadas por los bultos de otro trasteo
# y por la caja de la llanta. Los muebles se ven desde arriba como piezas de
# varias casillas: la cama ocupa un cuadrado de 2 x 2, el sofa una L, y asi.
# Cada mueble se puede GIRAR, pero no voltear (nadie sube un sofa patas arriba),
# y no se puede montar uno encima de otro. Las casillas libres del camion son
# exactamente las que suman los muebles. La pregunta: ¿cabe todo en el camion?
# Y si cabe, ¿como queda acomodado?
#
# EL CONTRATO. Es el mismo de todos los mundos (ver CONTRATO.md).
#
# Un ESTADO es un diccionario:
#   {"puestos": {"la cama": ((0, 0), (0, 1), (1, 0), (1, 1))}}   cada mueble subido y sus casillas
# El agente puede agregarle datos opcionales para que se vean en la escena:
#   "foco": (2, 3)                     la casilla que esta mirando (se ilumina)
#   "hueco": [(3, 0), (4, 0)]          casillas de un hueco que dedujo perdido (se tachan en rojo)
#   "mueble": "la cama"                el mueble que esta mirando (se resalta en el panel; None: ninguno).
#                                      Sin esta clave se resalta el siguiente que sale de la casa.
#
# UNA DECISION es (mueble, casillas): que mueble se sube y en que casillas queda.
#
# PIEZAS IGUALES. Cada nivel usa muebles de FORMAS DISTINTAS. Si hubiera dos
# baules iguales, cambiar uno por el otro daria una "solucion" nueva que en el
# camion se ve identica, y la cuenta de soluciones se duplicaria. Ademas, un
# mueble simetrico (la cama, el baul) tiene giros que caen en las mismas
# casillas: esos giros se cuentan una sola vez (ver posiciones()).
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_trasteo import CASOS           # noqa: E402

PARED = "#d4a72c"                          # amarillo mostaza de camion de trasteo

# Las formas de los muebles, vistas desde arriba, en su posicion de catalogo.
# Cada forma es una lista de casillas (fila, columna).
FORMAS = {
    "el baúl":        [(0, 0), (0, 1)],
    "la biblioteca":  [(0, 0), (0, 1), (0, 2)],
    "el escritorio":  [(0, 0), (1, 0), (1, 1)],
    "la cama":        [(0, 0), (0, 1), (1, 0), (1, 1)],
    "el armario":     [(0, 0), (0, 1), (0, 2), (0, 3)],
    "el sofá":        [(0, 0), (1, 0), (2, 0), (2, 1)],
    "el comedor":     [(0, 0), (0, 1), (0, 2), (1, 1)],
    "el modular":     [(0, 1), (0, 2), (1, 0), (1, 1)],
    "el piano":       [(0, 0), (0, 1), (1, 0), (1, 1), (2, 0)],
    "el sofá grande": [(0, 0), (1, 0), (2, 0), (3, 0), (3, 1)],
    "la estantería":  [(0, 0), (0, 2), (1, 0), (1, 1), (1, 2)],
}
COLOR = {
    "el baúl": "#8c5a2b", "la biblioteca": "#e4572e", "el escritorio": "#d6a24e",
    "la cama": "#f2a7c3", "el armario": "#3d4452", "el sofá": "#3f9b57",
    "el comedor": "#17a589", "el modular": "#2e86de", "el piano": "#1f2430",
    "el sofá grande": "#8e44ad", "la estantería": "#d64f6e",
}


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["filas"] = len(caso["camion"])
    caso["columnas"] = len(caso["camion"][0])
    caso["orden"] = list(caso["muebles"])                 # en este orden salen de la casa
    caso["libres"] = casillas_libres(caso)
    caso["posiciones"] = {m: posiciones(caso, m) for m in caso["orden"]}
    return caso


# ----------------------------------------------------------------- geometria del camion
def casillas_libres(caso):
    """Las casillas del camion donde se puede poner algo (sin bultos ajenos), leyendo de arriba a abajo."""
    libres = []
    for f in range(caso["filas"]):
        for c in range(caso["columnas"]):
            if caso["camion"][f][c] == ".":
                libres.append((f, c))
    return libres


def giros(forma):
    """Los giros distintos de una forma (sin voltearla). Una forma simetrica tiene menos de cuatro."""
    vistos = []
    actual = list(forma)
    for _ in range(4):
        fmin = min(f for (f, c) in actual)
        cmin = min(c for (f, c) in actual)
        normal = tuple(sorted((f - fmin, c - cmin) for (f, c) in actual))
        if normal not in vistos:
            vistos.append(normal)
        actual = [(c, -f) for (f, c) in actual]           # un cuarto de vuelta
    return vistos


def posiciones(caso, mueble):
    """Todas las maneras de poner el mueble dentro del camion, sobre casillas libres.
    NO mira si choca con otro mueble: eso es una regla, no geometria."""
    libres = set(casillas_libres(caso))
    lista = []
    for forma in giros(FORMAS[mueble]):
        for f in range(caso["filas"]):
            for c in range(caso["columnas"]):
                casillas = tuple(sorted((f + df, c + dc) for (df, dc) in forma))
                if all(x in libres for x in casillas) and casillas not in lista:
                    lista.append(casillas)
    return lista


def ocupadas(caso, estado):
    """Diccionario casilla -> mueble, con lo que ya esta subido."""
    dueno = {}
    for m in estado["puestos"]:
        for x in estado["puestos"][m]:
            dueno[x] = m
    return dueno


def vacias(caso, estado):
    """Las casillas libres del camion que todavia no tienen mueble."""
    dueno = ocupadas(caso, estado)
    return [x for x in caso["libres"] if x not in dueno]


def huecos(caso, estado):
    """Los huecos: grupos de casillas vacias que se tocan por un lado. Cada hueco es una lista."""
    quedan = set(vacias(caso, estado))
    grupos = []
    for x in vacias(caso, estado):
        if x not in quedan:
            continue
        grupo = [x]
        quedan.discard(x)
        i = 0
        while i < len(grupo):
            f, c = grupo[i]
            for v in ((f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)):
                if v in quedan:
                    quedan.discard(v)
                    grupo.append(v)
            i = i + 1
        grupos.append(sorted(grupo))
    return grupos


def faltan(caso, estado):
    """Los muebles que todavia no se han subido, en el orden en que salen de la casa."""
    return [m for m in caso["orden"] if m not in estado["puestos"]]


def tamano(mueble):
    return len(FORMAS[mueble])


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"puestos": {}}


def completo(caso, estado):
    return len(faltan(caso, estado)) == 0


def opciones(caso, estado):
    """Las decisiones posibles ahora: (mueble, casillas) para el siguiente mueble que sale de la casa.
    No mira ninguna regla: ofrece TODAS sus posiciones dentro del camion, aunque pise otro mueble."""
    pendientes = faltan(caso, estado)
    if not pendientes:
        return []
    m = pendientes[0]
    return [(m, casillas) for casillas in caso["posiciones"][m]]


def aplicar(caso, estado, decision):
    mueble, casillas = decision
    puestos = dict(estado["puestos"])
    puestos[mueble] = tuple(casillas)
    return {"puestos": puestos}


def viola(caso, estado):
    """"" si ningun mueble se monta sobre otro; si no, cuales chocan y donde."""
    dueno = {}
    for m in caso["orden"]:
        if m not in estado["puestos"]:
            continue
        for x in estado["puestos"][m]:
            if x in dueno:
                return "%s se monta sobre %s en la fila %d, columna %d" % (mayus(m), dueno[x], x[0] + 1, x[1] + 1)
            dueno[x] = m
    return ""


def respuesta(caso, estado):
    if completo(caso, estado) and viola(caso, estado) == "":
        return "Sí, cabe todo: %d muebles en %d casillas, sin un hueco" % (len(caso["orden"]), len(caso["libres"]))
    return ""


# ----------------------------------------------------------------- en palabras
def mayus(texto):
    return texto[0].upper() + texto[1:]


def rango(numeros):
    a, b = min(numeros) + 1, max(numeros) + 1
    return "%d" % a if a == b else "%d a %d" % (a, b)


def donde(casillas):
    """Las casillas de un mueble en palabras: filas y columnas que abarca."""
    filas = [f for (f, c) in casillas]
    cols = [c for (f, c) in casillas]
    fs, cs = rango(filas), rango(cols)
    return "%s %s, %s %s" % ("fila" if " " not in fs else "filas", fs, "columna" if " " not in cs else "columnas", cs)


def decir(caso, decision):
    mueble, casillas = decision
    return "sube %s: %s" % (mueble, donde(casillas))


def pistas(caso):
    lineas = ["Los muebles se giran, pero no se voltean",
              "Ningún mueble va encima de otro"]
    for m in caso["orden"]:
        lineas.append("%s: %d casillas" % (mayus(m), tamano(m)))
    return lineas


# ----------------------------------------------------------------- la escena
def dibujar(caso, estado):
    e = Escena(caso["filas"], caso["columnas"], titulo=caso["titulo"], ambiente="sala", pared=PARED)
    for f in range(caso["filas"]):
        for c in range(caso["columnas"]):
            if caso["camion"][f][c] == ".":
                e.piso(f, c, "#6f7378")
            else:
                e.roca(f, c)                                # bulto ajeno: ahi no cabe nada
    for c in range(caso["columnas"]):
        e.muro(0, c, "N")                                   # la cabina, al fondo
    puestos = estado["puestos"]
    for m in caso["orden"]:
        if m in puestos:
            casillas = sorted(puestos[m])
            for i, (f, c) in enumerate(casillas):
                e.caja("%s·%d" % (m, i), f, c, COLOR[m])
    foco = estado.get("foco")
    if foco is not None:
        e.luz(foco[0], foco[1])
    for (f, c) in estado.get("hueco", []):
        e.equis(f, c)
    # el panel: lo que ya se subio (bien), lo que falta, y el que va ahora resaltado
    pendientes = faltan(caso, estado)
    choque = viola(caso, estado)
    mirado = estado["mueble"] if "mueble" in estado else (pendientes[0] if pendientes else None)
    lineas = []
    for m in caso["orden"]:
        if m in puestos:
            marca = "mal" if choque.startswith(mayus(m) + " ") else "bien"
        else:
            marca = ""
        lineas.append(("%s (%d)" % (mayus(m), tamano(m)), marca, m == mirado))
    e.panel("La mudanza", lineas)
    llenas = sum(len(puestos[m]) for m in puestos)
    e.medidor("carga", min(llenas, len(caso["libres"])), len(caso["libres"]))
    quien = respuesta(caso, estado)
    if quien:
        e.veredicto(quien)
    return e
