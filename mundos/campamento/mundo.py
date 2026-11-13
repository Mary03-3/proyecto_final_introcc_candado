# mundo.py  ---  El campamento (carpas y arboles)
#
# LA FICCION. Anoche llegaron unos excursionistas al campamento. Cada uno amarro
# su carpa a SU arbol, en una casilla pegada a el (arriba, abajo, a la izquierda
# o a la derecha). Ninguna carpa toca a otra, ni siquiera en diagonal. Por la
# manana el guardabosques solo anoto cuantas carpas habia en cada fila y en cada
# columna: el CUPO. Con eso hay que reconstruir donde armo su carpa cada uno.
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
#   pistas(caso)               las reglas del nivel, en palabras
#   dibujar(caso, estado)      la escena en 3D de ese estado
#
# Consultas propias de este mundo (solo las usa la generacion 3):
#   arbol_de(caso, persona)          la casilla del arbol de esa persona
#   junto_al_arbol(caso, persona)    las casillas donde podria amarrar su carpa
#   alrededor(caso, casilla)         las casillas que la tocan, diagonales incluidas, y ella misma
#   carpas_en_fila(caso, carpas, f)  cuantas carpas hay ya en la fila f (igual con columna)
#
# Un ESTADO de este mundo es un diccionario:
#   {"carpas": {"Ana": (1, 2), "Bruno": (3, 0)}}     quien ya armo su carpa y donde
# El agente puede agregarle dos datos opcionales para que se vean en la escena:
#   "pasto": [(0, 0), (0, 1)]        casillas donde ya sabe que no va ninguna carpa
#   "foco": "Bruno"                  a quien esta mirando (se resalta su arbol)
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_campamento import CASOS        # noqa: E402

PARED = "#2f5d3a"                         # verde pino: el color de este mundo
PASTO = "#7fa95b"
TIERRA = "#4a3c30"                        # las casillas del borde donde va el cupo
COLOR_ARBOL = "#2e7d3c"
COLOR_PERSONA = ["#e4572e", "#2e86de", "#8e44ad", "#d68910", "#c0392b", "#17a589",
                 "#34495e", "#d35400", "#7d3c98", "#1f618d", "#b03a2e"]
LADOS = ((-1, 0, "al norte"), (1, 0, "al sur"), (0, -1, "al oeste"), (0, 1, "al este"))


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["arboles"] = [tuple(a) for a in caso["arboles"]]
    caso["orden"] = list(caso["personas"])                     # en este orden arman la carpa
    return caso


# ----------------------------------------------------------------- geometria
def dentro(caso, casilla):
    f, c = casilla
    return 0 <= f < caso["n"] and 0 <= c < caso["n"]


def arbol_de(caso, persona):
    """La casilla del arbol de esa persona."""
    return caso["arboles"][caso["personas"].index(persona)]


def junto_al_arbol(caso, persona):
    """Las casillas pegadas al arbol de la persona (norte, sur, oeste, este) donde cabe una carpa:
    dentro del campamento y sin otro arbol encima."""
    f, c = arbol_de(caso, persona)
    lista = []
    for (df, dc, _) in LADOS:
        x = (f + df, c + dc)
        if dentro(caso, x) and x not in caso["arboles"]:
            lista.append(x)
    return lista


def alrededor(caso, casilla):
    """La casilla y las ocho que la tocan (con diagonales), sin salirse del campamento."""
    f, c = casilla
    lista = []
    for df in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dentro(caso, (f + df, c + dc)):
                lista.append((f + df, c + dc))
    return lista


def carpas_en_fila(caso, carpas, f):
    return sum(1 for x in carpas.values() if x[0] == f)


def carpas_en_columna(caso, carpas, c):
    return sum(1 for x in carpas.values() if x[1] == c)


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"carpas": {}}


def pendiente(caso, estado):
    """A quien le toca armar su carpa (el primero del orden que falta), o None."""
    for p in caso["orden"]:
        if p not in estado["carpas"]:
            return p
    return None


def completo(caso, estado):
    return pendiente(caso, estado) is None


def opciones(caso, estado):
    """Las decisiones posibles ahora: (persona, casilla) para la persona que toca.
    No mira ninguna regla: ofrece TODAS las casillas pegadas a su arbol."""
    p = pendiente(caso, estado)
    if p is None:
        return []
    return [(p, x) for x in junto_al_arbol(caso, p)]


def aplicar(caso, estado, decision):
    persona, casilla = decision
    carpas = dict(estado["carpas"])
    carpas[persona] = tuple(casilla)
    return {"carpas": carpas}


def choque(caso, carpas):
    """"" si ninguna carpa toca a otra; si no, cuales se tocan."""
    nombres = list(carpas)
    for i in range(len(nombres)):
        for j in range(i):
            a, b = carpas[nombres[j]], carpas[nombres[i]]
            if a == b:
                return "%s y %s en la misma casilla" % (nombres[j], nombres[i])
            if abs(a[0] - b[0]) <= 1 and abs(a[1] - b[1]) <= 1:
                return "las carpas de %s y %s se tocan" % (nombres[j], nombres[i])
    return ""


def exceso(caso, carpas):
    """"" si ninguna fila ni columna pasa su cupo; si no, cual lo pasa."""
    for f in range(caso["n"]):
        if carpas_en_fila(caso, carpas, f) > caso["cupo_filas"][f]:
            return "la fila %d pasa su cupo de %d" % (f + 1, caso["cupo_filas"][f])
    for c in range(caso["n"]):
        if carpas_en_columna(caso, carpas, c) > caso["cupo_columnas"][c]:
            return "la columna %d pasa su cupo de %d" % (c + 1, caso["cupo_columnas"][c])
    return ""


def viola(caso, estado):
    """Devuelve "" si el estado no rompe ninguna regla; si no, cual rompio.
    Basta con revisar que ninguna fila ni columna PASE su cupo: hay tantas carpas como
    excursionistas y los cupos suman eso mismo, asi que al final cada cupo queda justo."""
    carpas = estado["carpas"]
    return choque(caso, carpas) or exceso(caso, carpas)


def respuesta(caso, estado):
    if not completo(caso, estado) or viola(caso, estado):
        return ""
    partes = []
    for p in caso["orden"]:
        f, c = estado["carpas"][p]
        partes.append("%s en la fila %d, columna %d" % (p, f + 1, c + 1))
    return "; ".join(partes)


# ----------------------------------------------------------------- en palabras
def lado(caso, persona, casilla):
    f, c = arbol_de(caso, persona)
    for (df, dc, nombre) in LADOS:
        if (f + df, c + dc) == tuple(casilla):
            return nombre
    return "lejos"


def decir(caso, decision):
    """Una decision, en palabras, para la nota de la bitacora."""
    persona, (f, c) = decision
    return "%s arma su carpa en la fila %d, columna %d, %s de su árbol" % (
        persona, f + 1, c + 1, lado(caso, persona, (f, c)))


def pistas(caso):
    lineas = ["Cada carpa está pegada a su árbol, arriba, abajo o a un lado",
              "Ninguna carpa toca a otra, ni siquiera en diagonal"]
    lineas.append("Cupo por fila: " + ", ".join(str(x) for x in caso["cupo_filas"]))
    lineas.append("Cupo por columna: " + ", ".join(str(x) for x in caso["cupo_columnas"]))
    return lineas


# ----------------------------------------------------------------- la escena
def dibujar(caso, estado):
    n = caso["n"]
    # una fila arriba y una columna a la izquierda de mas: alli, sobre tierra, se escribe el cupo.
    # Por eso la casilla (f, c) del campamento se dibuja en (f + 1, c + 1).
    e = Escena(n + 1, n + 1, titulo=caso["titulo"], ambiente="sala", pared=PARED)
    for f in range(n + 1):
        for c in range(n + 1):
            e.piso(f, c, PASTO if (f > 0 and c > 0) else TIERRA)
    for (f, c) in caso["arboles"]:
        e.mueble(f + 1, c + 1, "planta", COLOR_ARBOL)    # provisional: falta una pieza "arbol"
    carpas = estado["carpas"]
    foco = estado.get("foco")
    # el cupo de cada fila y columna: blanco si falta, verde si se lleno, rojo si se paso
    for f in range(n):
        e.ficha(f + 1, 0, str(caso["cupo_filas"][f]), _tono(carpas_en_fila(caso, carpas, f), caso["cupo_filas"][f]))
    for c in range(n):
        e.ficha(0, c + 1, str(caso["cupo_columnas"][c]), _tono(carpas_en_columna(caso, carpas, c), caso["cupo_columnas"][c]))
    # de quien es cada arbol: la inicial del dueno, de su color
    for i, p in enumerate(caso["personas"]):
        f, c = caso["arboles"][i]
        e.ficha(f + 1, c + 1, p[0], COLOR_PERSONA[i % len(COLOR_PERSONA)])
        if p == foco:
            e.runa(f + 1, c + 1, "#ffd23f")
    for casilla in estado.get("pasto", []):
        if tuple(casilla) not in carpas.values():
            e.equis(casilla[0] + 1, casilla[1] + 1)
    for i, p in enumerate(caso["personas"]):
        if p in carpas:
            f, c = carpas[p]
            e.personaje(p, f + 1, c + 1, COLOR_PERSONA[i % len(COLOR_PERSONA)], p[0])   # provisional: falta una "carpa"
    # el panel: tres reglas cortas, marcadas segun como va el estado
    toca = choque(caso, carpas)
    pasa = exceso(caso, carpas)
    lleno = completo(caso, estado)
    e.panel("Las reglas", [
        ("Cada carpa, pegada a su árbol", "bien" if lleno and not (toca or pasa) else "", False),
        ("Ninguna carpa toca a otra", "mal" if toca else ("bien" if lleno else ""), bool(toca)),
        ("Cada fila y columna, su cupo", "mal" if pasa else ("bien" if lleno and not toca else ""), bool(pasa)),
    ])
    if respuesta(caso, estado):
        e.veredicto("Las %d carpas quedaron en su sitio" % len(carpas))
    return e


def _tono(hay, cupo):
    if hay > cupo:
        return "#ff5a5a"
    if hay == cupo:
        return "#8dff6b"
    return "#ffffff"
