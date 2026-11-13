# mundo.py  ---  El cofre
#
# LA FICCION. El cofre esta al fondo de una casa llena de puertas cerradas. Por
# el piso hay llaves tiradas. Cualquier llave abre cualquier puerta, pero se
# queda pegada en la cerradura: cada llave sirve UNA sola vez. Pixie recoge
# todas las llaves que alcanza a pie. La pregunta: ¿en que orden abre Pixie las
# puertas para llegar al cofre? Una llave gastada en la puerta equivocada puede
# dejarlo encerrado lejos del cofre.
#
# Cumple el mismo contrato que los demas mundos (ver CONTRATO.md).
# Una DECISION es una casilla: la de la puerta que Pixie abre, o la del cofre
# cuando ya lo alcanza a pie y decide ir por el.
# Un ESTADO es un diccionario:
#   {"abiertas": [(3, 4), (1, 6)], "cofre": False}
#       las puertas abiertas, en el orden en que las abrio, y si ya llego al cofre.
# Todo lo demas (cuantas llaves tiene, hasta donde alcanza a caminar, donde esta
# parado) se deduce de ahi. Para eso estan las consultas propias de este mundo:
#   llaves, alcanzables, cerradas_a_mano, en_el_piso, faltan, recoge, trampa, letra.
# El agente puede agregar, para que se vea en la escena:
#   "trampas": [(5, 2)]      puertas que dedujo que no llevan a nada (runa roja)
#   "tachadas": [(1, 4)]     puertas que decidio no abrir en este momento (equis)
import os
import sys
from collections import deque

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_cofre import CASOS             # noqa: E402

PARED = "#1d6a68"          # petroleo: el color de las paredes de esta sala
PISO = "#5a5b5f"
MADERA = "#8a552a"         # las puertas cerradas
ORO = "#f2c230"            # las llaves


def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    mapa = caso["mapa"]
    caso["filas"] = len(mapa)
    caso["columnas"] = len(mapa[0])
    caso["puertas"] = []
    caso["llaves"] = []
    for f in range(caso["filas"]):
        for c in range(caso["columnas"]):
            letra_ = mapa[f][c]
            if letra_ == "E":
                caso["entrada"] = (f, c)
            elif letra_ == "C":
                caso["cofre"] = (f, c)
            elif letra_ == "P":
                caso["puertas"].append((f, c))
            elif letra_ == "L":
                caso["llaves"].append((f, c))
    if len(caso["puertas"]) > 26:
        raise ValueError("El nivel tiene %d puertas; con letras solo se nombran 26." % len(caso["puertas"]))
    caso["letras"] = {}
    for i, p in enumerate(caso["puertas"]):          # las puertas se nombran A, B, C... en orden de lectura
        caso["letras"][p] = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[i]
    _cuartos(caso)
    return caso


# ----------------------------------------------------------------- los cuartos (calculo interno)
def _pisable(caso, casilla):
    f, c = casilla
    return 0 <= f < caso["filas"] and 0 <= c < caso["columnas"] and caso["mapa"][f][c] != "#"


def _vecinas(caso, casilla):
    f, c = casilla
    return [v for v in ((f - 1, c), (f, c + 1), (f + 1, c), (f, c - 1)) if _pisable(caso, v)]


def _cuartos(caso):
    """Parte la casa en cuartos: pedazos de piso que se tocan sin pasar por una puerta."""
    puertas = set(caso["puertas"])
    cuarto = {}
    n = 0
    for f in range(caso["filas"]):
        for c in range(caso["columnas"]):
            x = (f, c)
            if not _pisable(caso, x) or x in puertas or x in cuarto:
                continue
            cuarto[x] = n
            cola = deque([x])
            while cola:
                y = cola.popleft()
                for v in _vecinas(caso, y):
                    if v not in puertas and v not in cuarto:
                        cuarto[v] = n
                        cola.append(v)
            n = n + 1
    caso["cuarto"] = cuarto
    caso["n_cuartos"] = n
    caso["llaves_de"] = [0] * n                       # cuantas llaves hay en cada cuarto
    for x in caso["llaves"]:
        caso["llaves_de"][cuarto[x]] += 1
    caso["puertas_de"] = [[] for _ in range(n)]        # las puertas de cada cuarto
    caso["lados"] = {}                                 # los cuartos que une cada puerta
    for p in caso["puertas"]:
        lados = []
        for v in _vecinas(caso, p):
            if v in puertas:
                raise ValueError("Dos puertas pegadas en %s y %s: el mapa no es valido." % (p, v))
            if cuarto[v] not in lados:
                lados.append(cuarto[v])
        caso["lados"][p] = lados
        for z in lados:
            caso["puertas_de"][z].append(p)


def _repaso(caso, abiertas):
    """Repite las aperturas en orden. Devuelve (cuartos alcanzados, llaves en mano, si alguna se forzo)."""
    region = set([caso["cuarto"][caso["entrada"]]])
    juntadas = caso["llaves_de"][caso["cuarto"][caso["entrada"]]]
    abiertas_ya = set()
    forzo = False
    for i, p in enumerate(abiertas):
        if juntadas - i <= 0:
            forzo = True
        abiertas_ya.add(p)
        if any(z in region for z in caso["lados"][p]):
            cola = deque(z for z in caso["lados"][p] if z not in region)
            for z in cola:
                region.add(z)
            while cola:
                z = cola.popleft()
                juntadas += caso["llaves_de"][z]
                for q in caso["puertas_de"][z]:
                    if q in abiertas_ya:
                        for z2 in caso["lados"][q]:
                            if z2 not in region:
                                region.add(z2)
                                cola.append(z2)
    return region, juntadas - len(abiertas), forzo


# ----------------------------------------------------------------- lo que se puede preguntar de la casa
def letra(caso, puerta):
    """El nombre de la puerta en pantalla: A, B, C..."""
    return caso["letras"][puerta]


def llaves(caso, estado):
    """Cuantas llaves tiene Pixie en la mano. (Si abrio puertas sin llave, puede dar negativo.)"""
    return _repaso(caso, estado["abiertas"])[1]


def alcanzables(caso, estado):
    """Los cuartos (numeros) a los que Pixie llega a pie con las puertas que ya abrio."""
    return _repaso(caso, estado["abiertas"])[0]


def cerradas_a_mano(caso, estado):
    """Las puertas cerradas que Pixie tiene al alcance, en orden alfabetico."""
    region = alcanzables(caso, estado)
    abiertas = set(estado["abiertas"])
    lista = []
    for p in caso["puertas"]:
        if p not in abiertas and any(z in region for z in caso["lados"][p]):
            lista.append(p)
    return lista


def en_el_piso(caso, estado):
    """Cuantas llaves siguen tiradas en cuartos a los que Pixie todavia no llega."""
    region = alcanzables(caso, estado)
    return sum(caso["llaves_de"][z] for z in range(caso["n_cuartos"]) if z not in region)


def faltan(caso, estado):
    """Cuantas puertas cerradas hay, como minimo, entre Pixie y el cofre."""
    region = alcanzables(caso, estado)
    abiertas = set(estado["abiertas"])
    meta = caso["cuarto"][caso["cofre"]]
    costo = {}
    cola = deque()
    for z in region:
        costo[z] = 0
        cola.append(z)
    while cola:                                     # 0-1 BFS: cruzar una puerta abierta no cuesta, una cerrada cuesta 1
        z = cola.popleft()
        for p in caso["puertas_de"][z]:
            paso = 0 if p in abiertas else 1
            for z2 in caso["lados"][p]:
                if z2 not in costo or costo[z] + paso < costo[z2]:
                    costo[z2] = costo[z] + paso
                    if paso == 0:
                        cola.appendleft(z2)
                    else:
                        cola.append(z2)
    return costo.get(meta, 10 ** 6)


def recoge(caso, estado, puerta):
    """Cuantas llaves nuevas alcanza Pixie si abre esa puerta (sin contar la que gasta)."""
    antes = alcanzables(caso, estado)
    despues = _repaso(caso, estado["abiertas"] + [puerta])[0]
    return sum(caso["llaves_de"][z] for z in despues if z not in antes)


def trampa(caso, puerta):
    """True si la puerta da a un cuarto sin llaves, sin el cofre y sin ninguna otra puerta."""
    for z in caso["lados"][puerta]:
        if (caso["llaves_de"][z] == 0 and z != caso["cuarto"][caso["cofre"]] and z != caso["cuarto"][caso["entrada"]]
                and caso["puertas_de"][z] == [puerta]):
            return True
    return False


# ----------------------------------------------------------------- el contrato
def inicio(caso):
    return {"abiertas": [], "cofre": False}


def opciones(caso, estado):
    """Las puertas cerradas al alcance y, si ya se llega a pie, el cofre. No mira si quedan llaves."""
    if estado["cofre"]:
        return []
    lista = cerradas_a_mano(caso, estado)
    if caso["cuarto"][caso["cofre"]] in alcanzables(caso, estado):
        lista = [caso["cofre"]] + lista
    return lista


def completo(caso, estado):
    return len(opciones(caso, estado)) == 0


def aplicar(caso, estado, decision):
    if decision == caso["cofre"]:
        return {"abiertas": list(estado["abiertas"]), "cofre": True}
    return {"abiertas": estado["abiertas"] + [decision], "cofre": False}


def viola(caso, estado):
    if _repaso(caso, estado["abiertas"])[2]:
        return "no le quedaba llave para esa puerta"
    if not estado["cofre"] and completo(caso, estado):
        return "quedó encerrado"
    return ""


def decir(caso, decision):
    if decision == caso["cofre"]:
        return "va por el cofre"
    return "abre la puerta %s" % letra(caso, decision)


def _lista(nombres):
    if len(nombres) == 1:
        return nombres[0]
    return ", ".join(nombres[:-1]) + " y " + nombres[-1]


def respuesta(caso, estado):
    if not estado["cofre"] or viola(caso, estado) != "":
        return ""
    if not estado["abiertas"]:
        return "Pixie llega al cofre sin abrir ninguna puerta"
    return "Pixie abre %s, y llega al cofre" % _lista([letra(caso, p) for p in estado["abiertas"]])


def pistas(caso):
    return ["Hay %d llaves y %d puertas." % (len(caso["llaves"]), len(caso["puertas"])),
            "Cualquier llave abre cualquier puerta, pero se gasta.",
            "Pixie recoge las llaves que alcanza a pie."]


# ----------------------------------------------------------------- la escena
def _ruta(caso, desde, hasta, pasables):
    """El camino mas corto, casilla por casilla, pisando solo casillas pasables (y la de llegada)."""
    previo = {desde: None}
    cola = deque([desde])
    while cola:
        x = cola.popleft()
        if x == hasta:
            break
        for v in _vecinas(caso, x):
            if v not in previo and (v in pasables or v == hasta):
                previo[v] = x
                cola.append(v)
    if hasta not in previo:
        return [desde]
    ruta = []
    x = hasta
    while x is not None:
        ruta.append(x)
        x = previo[x]
    ruta.reverse()
    return ruta


def _juntar(caso, camino, pasables, llaves_nuevas):
    """Pixie camina a recoger las llaves, siempre a la mas cercana primero."""
    pendientes = list(llaves_nuevas)
    while pendientes:
        mejor = None
        for k in pendientes:
            r = _ruta(caso, camino[-1], k, pasables)
            if r[-1] == k and (mejor is None or len(r) < len(mejor)):
                mejor = r
        if mejor is None:
            break
        camino.extend(mejor[1:])
        pendientes.remove(mejor[-1])


def recorrido(caso, estado):
    """Lo que camino Pixie, casilla por casilla: a cada puerta y a cada llave que recogio."""
    cuarto = caso["cuarto"]
    region = set([cuarto[caso["entrada"]]])
    abiertas = []
    pasables = set(x for x in cuarto if cuarto[x] in region)
    camino = [caso["entrada"]]
    _juntar(caso, camino, pasables, [k for k in caso["llaves"] if cuarto[k] in region])
    for p in estado["abiertas"]:
        camino.extend(_ruta(caso, camino[-1], p, pasables)[1:])
        abiertas.append(p)
        nueva = _repaso(caso, abiertas)[0]
        ganadas = [k for k in caso["llaves"] if cuarto[k] in nueva and cuarto[k] not in region]
        region = nueva
        pasables = set(x for x in cuarto if cuarto[x] in region) | set(abiertas)
        _juntar(caso, camino, pasables, ganadas)
    if estado["cofre"]:
        camino.extend(_ruta(caso, camino[-1], caso["cofre"], pasables)[1:])
    return camino


def dibujar(caso, estado):
    e = Escena(caso["filas"], caso["columnas"], titulo=caso["titulo"], ambiente="sala", pared=PARED)
    e.salida(caso["entrada"][0], caso["entrada"][1])
    e.meta(caso["cofre"][0], caso["cofre"][1])
    for f in range(caso["filas"]):
        for c in range(caso["columnas"]):
            if caso["mapa"][f][c] == "#":
                e.roca(f, c)
            else:
                e.piso(f, c, PISO)
    abiertas = estado["abiertas"]
    region, _, _ = _repaso(caso, abiertas)
    forzadas = set()
    juntadas = caso["llaves_de"][caso["cuarto"][caso["entrada"]]]
    hechas = []
    for i, p in enumerate(abiertas):                 # que puertas se abrieron sin llave
        if juntadas - i <= 0:
            forzadas.add(p)
        hechas.append(p)
        r = _repaso(caso, hechas)[0]
        juntadas = sum(caso["llaves_de"][z] for z in r)
    e.cofre(caso["cofre"][0], caso["cofre"][1])
    camino = recorrido(caso, estado)
    e.hilo(camino)
    for k in caso["llaves"]:                          # las llaves que siguen en el piso
        if caso["cuarto"][k] not in region:
            e.caja("llave %d,%d" % k, k[0], k[1], ORO)
    for p in caso["puertas"]:
        nombre = letra(caso, p)
        if p in forzadas:
            e.equis(p[0], p[1])
            e.ficha(p[0], p[1], nombre, "#ff6b6b")
        elif p in abiertas:
            e.ficha(p[0], p[1], nombre, "#8dff6b")
        else:
            e.caja("puerta " + nombre, p[0], p[1], MADERA)
            e.ficha(p[0], p[1], nombre, "#ffffff")
    for p in estado.get("trampas", []):
        if p not in abiertas:
            e.runa(p[0], p[1])
    for p in estado.get("tachadas", []):
        if p not in abiertas:
            e.equis(p[0], p[1])
    e.conejo(camino[-1][0], camino[-1][1])
    e.medidor("llaves", max(0, llaves(caso, estado)), max(1, len(caso["llaves"])))
    frase = respuesta(caso, estado)
    if frase:
        e.veredicto(frase)
    return e
