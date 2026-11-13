# mundo.py  ---  La bodega
#
# LA FICCION. Pixie trabaja en una bodega y tiene que despachar la carga: llevar
# cada caja a un muelle de carga (los parches verdes). Las cajas no se cargan: se
# EMPUJAN, y solo hacia adelante. Pixie no puede halarlas ni pasar por encima, y
# una caja no empuja a otra. El turno alcanza para un numero contado de empujes.
# Una caja que queda arrinconada contra dos paredes ya no se mueve nunca mas.
# La pregunta: ¿como despacha Pixie la carga?
#
# Cumple el mismo contrato que los demas mundos (ver CONTRATO.md).
# Una DECISION es un empuje: (casilla de la caja, lado hacia donde se empuja), por
# ejemplo ((3, 2), "N"). Pixie camina sola hasta detras de la caja y empuja una casilla.
# Un ESTADO es un diccionario:
#   {"cajas": [(3, 2), (4, 4)],      donde esta cada caja (siempre en el mismo orden: caja 1, caja 2, ...)
#    "pixie": (4, 2),                donde esta parado Pixie
#    "camino": [(5, 1), (4, 1), ...] todo lo que Pixie ha caminado, en orden (el hilo)
#    "empujes": [((4, 2), "N")],     los empujes hechos, en orden
#    "acomodos": [...]}              cada acomodo por el que paso la bodega (para no repetir)
# El agente puede agregar, para que se vea en la escena:
#   "muertas": [(1, 1), (1, 2)]      casillas de donde una caja ya no sale (las que dedujo)
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_bodega import CASOS            # noqa: E402

PARED = "#7a5c3a"                          # pardo de carton: el color de la bodega
PISO = "#55585e"
COLOR_CAJA = "#c58b4e"
LADOS = {"N": (-1, 0), "E": (0, 1), "S": (1, 0), "O": (0, -1)}
NOMBRE_LADO = {"N": "el norte", "E": "el este", "S": "el sur", "O": "el oeste"}


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def preparar(datos):
    """Convierte los datos de un nivel (el mapa) en un caso. Lo usa tambien el generador."""
    caso = dict(datos)
    mapa = caso["mapa"]
    caso["filas"] = len(mapa)
    caso["columnas"] = len(mapa[0])
    caso["paredes"] = set()
    caso["metas"] = []
    caso["cajas"] = []
    for f in range(caso["filas"]):
        for c in range(caso["columnas"]):
            letra = mapa[f][c]
            if letra == "#":
                caso["paredes"].add((f, c))
            if letra == "P":
                caso["entrada"] = (f, c)
            if letra == "C":
                caso["cajas"].append((f, c))
            if letra == "M":
                caso["metas"].append((f, c))
    return caso


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = preparar(CASOS[nivel])
    caso["nivel"] = nivel
    return caso


# ----------------------------------------------------------------- lo que se puede preguntar de la bodega
def pared(caso, casilla):
    """¿Hay pared en la casilla? (Fuera del mapa cuenta como pared.)"""
    f, c = casilla
    if not (0 <= f < caso["filas"] and 0 <= c < caso["columnas"]):
        return True
    return casilla in caso["paredes"]


def es_meta(caso, casilla):
    """¿La casilla es un muelle de carga?"""
    return casilla in caso["metas"]


def mover(casilla, lado):
    """La casilla vecina hacia ese lado."""
    df, dc = LADOS[lado]
    return (casilla[0] + df, casilla[1] + dc)


def libre(caso, estado, casilla):
    """¿Se puede pisar la casilla ahora? (No hay pared ni caja.)"""
    return not pared(caso, casilla) and casilla not in estado["cajas"]


def esquina(caso, casilla):
    """¿La casilla tiene pared en dos lados que se tocan (norte y este, este y sur...)?"""
    n = pared(caso, mover(casilla, "N"))
    s = pared(caso, mover(casilla, "S"))
    e = pared(caso, mover(casilla, "E"))
    o = pared(caso, mover(casilla, "O"))
    return (n or s) and (e or o)


def arrinconada(caso, casilla):
    """¿Una caja en esta casilla queda atascada para siempre? (Esquina que no es muelle.)"""
    return esquina(caso, casilla) and not es_meta(caso, casilla)


def ruta(caso, estado, destino):
    """El camino mas corto de Pixie hasta el destino sin atravesar cajas ni paredes, o None."""
    inicio_ = estado["pixie"]
    previo = {inicio_: None}
    cola = deque([inicio_])
    while cola:
        x = cola.popleft()
        if x == destino:
            camino = []
            while x is not None:
                camino.append(x)
                x = previo[x]
            return camino[::-1]
        for lado in ("N", "E", "S", "O"):
            v = mover(x, lado)
            if v not in previo and libre(caso, estado, v):
                previo[v] = x
                cola.append(v)
    return None


def alcanza(caso, cajas, desde):
    """Todas las casillas a las que Pixie puede llegar caminando desde 'desde'."""
    vistas = {desde}
    cola = deque([desde])
    while cola:
        x = cola.popleft()
        for lado in ("N", "E", "S", "O"):
            v = mover(x, lado)
            if v not in vistas and not pared(caso, v) and v not in cajas:
                vistas.add(v)
                cola.append(v)
    return vistas


def acomodo(caso, cajas, pixie):
    """Una foto del acomodo: donde estan las cajas y en que zona esta Pixie.
    Dos acomodos son el mismo si las cajas estan igual y Pixie puede caminar de uno al otro."""
    zona = min(alcanza(caso, set(cajas), pixie))
    return (tuple(sorted(cajas)), zona)


def despachada(caso, estado):
    """¿Todas las cajas estan sobre un muelle?"""
    return all(es_meta(caso, x) for x in estado["cajas"])


def quedan(caso, estado):
    """Cuantos empujes le quedan al turno."""
    return caso["turno"] - len(estado["empujes"])


def distancia(a, b):
    """Cuantos empujes hacen falta, como minimo, para llevar una caja de a hasta b."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


# ----------------------------------------------------------------- el contrato
def inicio(caso):
    cajas = list(caso["cajas"])
    return {"cajas": cajas, "pixie": caso["entrada"], "camino": [caso["entrada"]], "empujes": [],
            "acomodos": [acomodo(caso, cajas, caso["entrada"])]}


def opciones(caso, estado):
    """Los empujes posibles: una caja con espacio libre adelante y Pixie capaz de llegar detras.
    No mira nada mas: ni esquinas, ni si el acomodo se repite, ni si alcanza el turno."""
    if despachada(caso, estado) or quedan(caso, estado) <= 0:
        return []
    zona = alcanza(caso, set(estado["cajas"]), estado["pixie"])
    posibles = []
    for caja in estado["cajas"]:
        for lado in ("N", "E", "S", "O"):
            adelante = mover(caja, lado)
            df, dc = LADOS[lado]
            detras = (caja[0] - df, caja[1] - dc)
            if detras in zona and libre(caso, estado, adelante):
                posibles.append((caja, lado))
    return posibles


def completo(caso, estado):
    return len(opciones(caso, estado)) == 0


def aplicar(caso, estado, decision):
    caja, lado = decision
    df, dc = LADOS[lado]
    detras = (caja[0] - df, caja[1] - dc)
    andar = ruta(caso, estado, detras)
    cajas = [mover(x, lado) if x == caja else x for x in estado["cajas"]]
    camino = estado["camino"] + andar[1:] + [caja]
    return {"cajas": cajas, "pixie": caja, "camino": camino, "empujes": estado["empujes"] + [decision],
            "acomodos": estado["acomodos"] + [acomodo(caso, cajas, caja)]}


def viola(caso, estado):
    for caja in estado["cajas"]:
        if arrinconada(caso, caja):
            return "una caja quedó arrinconada fuera del muelle"
    if len(set(estado["acomodos"])) < len(estado["acomodos"]):
        return "volvió a un acomodo que ya tuvo"
    if not despachada(caso, estado):
        if quedan(caso, estado) <= 0:
            return "se acabó el turno sin despachar"
        if completo(caso, estado):
            return "la carga quedó trabada"
    return ""


def decir(caso, decision):
    caja, lado = decision
    return "empuja la caja de la fila %d, columna %d hacia %s" % (caja[0] + 1, caja[1] + 1, NOMBRE_LADO[lado])


def respuesta(caso, estado):
    if despachada(caso, estado) and viola(caso, estado) == "":
        tramos = []                                   # empujes seguidos hacia el mismo lado: [lado, cuantos]
        for (_, lado) in estado["empujes"]:
            if tramos and tramos[-1][0] == lado:
                tramos[-1][1] = tramos[-1][1] + 1
            else:
                tramos.append([lado, 1])
        partes = ["%d al %s" % (n, NOMBRE_LADO[lado][3:]) for (lado, n) in tramos]
        if len(partes) > 1:
            partes = [", ".join(partes[:-1]) + " y " + partes[-1]]
        return "Pixie despacha la carga en %d empujes: %s" % (len(estado["empujes"]), partes[0])
    return ""


def pistas(caso):
    return ["Cada caja va a un muelle verde. Hay %d cajas y %d muelles." % (len(caso["cajas"]), len(caso["metas"])),
            "Las cajas solo se empujan: no se halan y una no empuja a otra.",
            "El turno alcanza para %d empujes." % caso["turno"],
            "Una caja arrinconada contra dos paredes ya no se mueve."]


def dibujar(caso, estado):
    e = Escena(caso["filas"], caso["columnas"], titulo=caso["titulo"], ambiente=caso.get("ambiente", "sala"), pared=PARED)
    e.salida(caso["entrada"][0], caso["entrada"][1])
    for f in range(caso["filas"]):
        for c in range(caso["columnas"]):
            if (f, c) in caso["paredes"]:
                e.roca(f, c)
            else:
                e.piso(f, c, PISO)
    for m in caso["metas"]:
        e.meta(m[0], m[1])
    e.hilo(estado["camino"])
    for casilla in estado.get("muertas", []):
        if casilla not in estado["cajas"]:
            e.runa(casilla[0], casilla[1], "#ff9f1c")
    for k, caja in enumerate(estado["cajas"]):
        e.caja("caja%d" % (k + 1), caja[0], caja[1], COLOR_CAJA)
        if es_meta(caso, caja):
            e.ficha(caja[0], caja[1], "✓", "#1f7a3a")
        elif arrinconada(caso, caja):
            e.runa(caja[0], caja[1])
    e.conejo(estado["pixie"][0], estado["pixie"][1])
    e.medidor("turno", quedan(caso, estado), caso["turno"])
    frase = respuesta(caso, estado)
    if frase:
        e.veredicto(frase)
    return e
