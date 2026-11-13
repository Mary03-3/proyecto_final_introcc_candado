# mundo.py  ---  El archipielago (puentes entre islas, un hashiwokakero)
#
# LA FICCION. En el mar hay islas, y cada isla tiene escrito un numero: cuantos
# puentes salen de ella. Hay que tender los puentes de modo que
#   - cada isla tenga exactamente los puentes que dice su numero;
#   - los puentes vayan en linea recta (horizontal o vertical) entre dos islas
#     que se ven, sin pasar por encima de otra isla;
#   - entre dos islas haya a lo sumo dos puentes;
#   - ningun puente cruce a otro;
#   - todas las islas queden conectadas: se pueda ir de cualquiera a cualquiera.
# La pregunta: ¿como se conectan todas las islas?
#
# EL CONTRATO. Todos los mundos del proyecto tienen estas mismas funciones.
# Por eso un agente que solo use estas funciones sirve en cualquier mundo.
#
#   casos()                    lista de niveles disponibles, del mas facil al mas dificil
#   cargar(nivel)              devuelve el caso (un diccionario con todo lo del nivel)
#   inicio(caso)               el estado antes de decidir nada
#   completo(caso, estado)     ¿ya no queda nada por decidir?
#   opciones(caso, estado)     las decisiones posibles ahora, SIN mirar las reglas
#   aplicar(caso, estado, d)   un estado NUEVO con la decision d tomada
#   viola(caso, estado)        "" si todo va bien; si no, la regla que se rompio
#   decir(caso, d)             la decision d, en palabras
#   respuesta(caso, estado)    la respuesta a la pregunta de la ficcion
#   pistas(caso)               las reglas, en palabras
#   dibujar(caso, estado)      la escena en 3D de ese estado
#
# Las islas se numeran 0, 1, 2, ... leyendo el mapa como un libro. Un PAR es una
# pareja de islas que se ven (en la misma fila o columna, con solo agua en medio).
# Los pares tambien se numeran: caso["pares"][p] = (i, j).
#
# Una DECISION es (p, k): tender k puentes (0, 1 o 2) en el par p. Los pares se
# deciden en orden, uno por uno.
#
# Un ESTADO de este mundo es un diccionario:
#   {"puentes": {0: 2, 1: 0, 2: 1}}       cuantos puentes lleva cada par ya decidido
# El agente puede agregarle datos opcionales para que se vean en la escena:
#   "foco": 3                             la isla que esta mirando (se resalta)
#   "tachados": [4, 7]                    pares donde ya sabe que NO va puente
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_archipielago import CASOS      # noqa: E402

PARED = "#1f7f6e"            # verde mar: el color de las paredes de este mundo
AGUA = "#3a78a8"
ARENA = "#e6cf8b"
TINTA = "#14213d"            # numero de una isla a la que aun le faltan puentes
LISTA = "#178a3e"            # numero de una isla que ya tiene justo los suyos
MAL = "#d64545"              # numero de una isla que rompe su regla; equis de un cruce
TACHA = "#e8edf3"            # equis de un par donde se sabe que no va puente


# ----------------------------------------------------------------- niveles
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
    islas = []
    for f in range(len(mapa)):
        for c in range(len(mapa[0])):
            if mapa[f][c].isdigit():
                islas.append((f, c, int(mapa[f][c])))
    caso["islas"] = islas
    donde = {}
    for i in range(len(islas)):
        donde[(islas[i][0], islas[i][1])] = i
    # los pares: desde cada isla se mira a la derecha y hacia abajo hasta la primera isla
    pares = []
    celdas = []
    for i in range(len(islas)):
        f, c, _ = islas[i]
        for (df, dc) in ((0, 1), (1, 0)):
            g, d = f + df, c + dc
            agua = []
            while g < caso["filas"] and d < caso["columnas"] and (g, d) not in donde:
                agua.append((g, d))
                g, d = g + df, d + dc
            if (g, d) in donde and len(agua) > 0:
                pares.append((i, donde[(g, d)]))
                celdas.append(agua)
    caso["pares"] = pares
    caso["celdas"] = celdas                    # el agua que cruza cada par
    caso["cruces"] = []                        # los pares que se cruzan con cada par
    for p in range(len(pares)):
        lista = []
        for q in range(len(pares)):
            if q != p and set(celdas[p]) & set(celdas[q]):
                lista.append(q)
        caso["cruces"].append(lista)
    caso["pares_de"] = []                      # los pares que tocan cada isla
    for i in range(len(islas)):
        caso["pares_de"].append([p for p in range(len(pares)) if i in pares[p]])
    return caso


# ----------------------------------------------------------------- consultas propias
def islas_de(caso, p):
    """Las dos islas (i, j) que une el par p."""
    return caso["pares"][p]


def pares_de(caso, i):
    """Los pares que tocan la isla i."""
    return caso["pares_de"][i]


def pide(caso, i):
    """Cuantos puentes pide la isla i (su numero)."""
    return caso["islas"][i][2]


def cruces(caso, p):
    """Los pares que se cruzan con el par p: si p lleva puente, esos no pueden llevarlo."""
    return caso["cruces"][p]


def puentes_de(caso, estado, i):
    """Cuantos puentes tiene ya la isla i en este estado."""
    total = 0
    for p in pares_de(caso, i):
        total = total + estado["puentes"].get(p, 0)
    return total


def grupos(caso, estado):
    """Las islas agrupadas por lo que ya une a cada una: una lista de conjuntos."""
    vistos = set()
    resultado = []
    for inicio_ in range(len(caso["islas"])):
        if inicio_ in vistos:
            continue
        grupo = set([inicio_])
        pila = [inicio_]
        while pila:
            i = pila.pop()
            for p in pares_de(caso, i):
                if estado["puentes"].get(p, 0) > 0:
                    a, b = islas_de(caso, p)
                    otra = b if a == i else a
                    if otra not in grupo:
                        grupo.add(otra)
                        pila.append(otra)
        vistos |= grupo
        resultado.append(grupo)
    return resultado


def nombre_isla(caso, i):
    f, c, _ = caso["islas"][i]
    return "(%d, %d)" % (f + 1, c + 1)


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"puentes": {}}


def pendiente(caso, estado):
    """El primer par que falta por decidir, o None."""
    for p in range(len(caso["pares"])):
        if p not in estado["puentes"]:
            return p
    return None


def completo(caso, estado):
    return pendiente(caso, estado) is None


def opciones(caso, estado):
    """Las decisiones posibles ahora: 0, 1 o 2 puentes en el par que toca.
    No mira ninguna regla."""
    p = pendiente(caso, estado)
    if p is None:
        return []
    return [(p, 0), (p, 1), (p, 2)]


def aplicar(caso, estado, decision):
    p, k = decision
    puentes = dict(estado["puentes"])
    puentes[p] = k
    return {"puentes": puentes}


def choques(caso, estado):
    """Lo que esta mal en el estado, para dibujarlo: (islas que rompen su numero, casillas de cruce)."""
    puentes = estado["puentes"]
    malas = []
    for i in range(len(caso["islas"])):
        tiene = puentes_de(caso, estado, i)
        cerrada = all(p in puentes for p in pares_de(caso, i))
        if tiene > pide(caso, i) or (cerrada and tiene < pide(caso, i)):
            malas.append(i)
    cruzadas = []
    for p in puentes:
        if puentes[p] > 0:
            for q in cruces(caso, p):
                if q > p and puentes.get(q, 0) > 0:
                    cruzadas.append(sorted(set(caso["celdas"][p]) & set(caso["celdas"][q]))[0])
    return malas, cruzadas


def viola(caso, estado):
    """Devuelve "" si el estado no rompe ninguna regla; si no, cual rompio."""
    puentes = estado["puentes"]
    for p in sorted(puentes):
        if puentes[p] > 0:
            for q in cruces(caso, p):
                if puentes.get(q, 0) > 0:
                    (f, c) = sorted(set(caso["celdas"][p]) & set(caso["celdas"][q]))[0]
                    return "dos puentes se cruzan en (%d, %d)" % (f + 1, c + 1)
    for i in range(len(caso["islas"])):
        tiene = puentes_de(caso, estado, i)
        if tiene > pide(caso, i):
            return "la isla %s pide %d y ya tiene %d" % (nombre_isla(caso, i), pide(caso, i), tiene)
        if tiene < pide(caso, i) and all(p in puentes for p in pares_de(caso, i)):
            return "a la isla %s le faltan puentes y ya no le quedan vecinas" % nombre_isla(caso, i)
    if completo(caso, estado) and len(grupos(caso, estado)) > 1:
        return "las islas quedan en %d grupos sueltos" % len(grupos(caso, estado))
    return ""


def total_puentes(caso, estado):
    total = 0
    for k in estado["puentes"].values():
        total = total + k
    return total


def respuesta(caso, estado):
    if completo(caso, estado) and viola(caso, estado) == "":
        dobles = len([p for p in estado["puentes"] if estado["puentes"][p] == 2])
        return "%d puentes unen las %d islas (%d tramos dobles)" % (total_puentes(caso, estado), len(caso["islas"]), dobles)
    return ""


# ----------------------------------------------------------------- en palabras
CUANTOS = {0: "Ningún puente", 1: "Un puente", 2: "Dos puentes"}


def decir(caso, decision):
    """Una decision, en palabras, para la nota de la bitacora."""
    p, k = decision
    i, j = islas_de(caso, p)
    return "%s entre %s y %s" % (CUANTOS[k], nombre_isla(caso, i), nombre_isla(caso, j))


def pistas(caso):
    return ["Cada isla lleva tantos puentes como dice su número.",
            "Los puentes van en línea recta, entre dos islas que se ven.",
            "Entre dos islas hay a lo sumo dos puentes.",
            "Ningún puente cruza a otro.",
            "Todas las islas quedan conectadas."]


# ----------------------------------------------------------------- la escena
def dibujar(caso, estado):
    filas, columnas = caso["filas"], caso["columnas"]
    e = Escena(filas, columnas, titulo=caso["titulo"], ambiente="sala", pared=PARED)
    islas = caso["islas"]
    en_isla = set((f, c) for (f, c, _) in islas)
    for f in range(filas):
        for c in range(columnas):
            e.piso(f, c, ARENA if (f, c) in en_isla else AGUA)
    puentes = estado["puentes"]
    # los puentes: uno sencillo es una tabla; uno doble, dos tablas paralelas.
    # (Provisional: se dibujan con hilo, corrido un poco a lado y lado. Ver NOTAS.md.)
    for p in sorted(puentes):
        k = puentes[p]
        if k == 0:
            continue
        i, j = islas_de(caso, p)
        (f1, c1, _), (f2, c2, _) = islas[i], islas[j]
        if k == 1:
            e.hilo([(f1, c1), (f2, c2)])
        else:
            for corre in (-0.14, 0.14):
                if f1 == f2:
                    g = max(f1, 0.14) + corre          # en la fila 0 no se puede correr hacia afuera
                    e.hilo([(g, c1), (g, c2)])
                else:
                    d = max(c1, 0.14) + corre
                    e.hilo([(f1, d), (f2, d)])
    for p in estado.get("tachados", []):
        if p not in puentes:
            agua = caso["celdas"][p]
            f, c = agua[len(agua) // 2]
            e.equis(f, c, TACHA)
    malas, cruzadas = choques(caso, estado)
    for (f, c) in cruzadas:
        e.equis(f, c, MAL)
    foco = estado.get("foco")
    if foco is not None:
        e.luz(islas[foco][0], islas[foco][1])
    for i in range(len(islas)):
        f, c, n = islas[i]
        if i in malas:
            color = MAL
        elif puentes_de(caso, estado, i) == n:
            color = LISTA
        else:
            color = TINTA
        e.ficha(f, c, str(n), color)
    necesarios = sum(n for (_, _, n) in islas) // 2
    e.medidor("puentes", total_puentes(caso, estado), necesarios)
    r = respuesta(caso, estado)
    if r:
        e.veredicto(r)
    return e
