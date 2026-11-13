# mundo.py  ---  El vecindario (un acertijo tipo cebra)
#
# LA FICCION. Pixie se escapo y se metio en una de las casas de la cuadra.
# Las casas estan en fila, numeradas de izquierda a derecha. Cada casa tiene un
# color distinto, en cada una vive una persona distinta con una mascota distinta
# (en los niveles altos, ademas, en cada casa se toma una bebida distinta).
# Pixie es la mascota que falta: el conejo. Los vecinos dejaron pistas.
# La pregunta: ¿quien tiene el conejo?
#
# EL CONTRATO. Todos los mundos del proyecto tienen estas mismas funciones
# (ver CONTRATO.md). Un agente que solo use estas funciones sirve en cualquier mundo.
#
#   casos()                    lista de niveles disponibles, del mas facil al mas dificil
#   cargar(nivel)              devuelve el caso (un diccionario con todo lo del nivel)
#   inicio(caso)               el estado antes de decidir nada
#   completo(caso, estado)     ¿ya no queda nada por decidir?
#   opciones(caso, estado)     las decisiones posibles ahora, SIN mirar las pistas
#   aplicar(caso, estado, d)   un estado NUEVO con la decision d tomada
#   viola(caso, estado)        "" si todo va bien; si no, la pista que se rompio
#   decir(caso, d)             la decision d, en palabras
#   respuesta(caso, estado)    la respuesta a la pregunta de la ficcion
#   pistas(caso)               las pistas, en palabras
#   dibujar(caso, estado)      la escena en 3D de ese estado
#
# Un ESTADO de este mundo es un diccionario:
#   {"casa": {"conejo": 2, "perro": 0, "roja": 1}}     cada cosa ya ubicada y el numero de su casa (desde 0)
# Las cosas se ubican en un orden fijo: primero las mascotas, luego los colores,
# luego las personas (y al final las bebidas). Cada decision es (cosa, casa).
# El agente puede agregarle dos datos opcionales para que se vean en la escena:
#   "foco": "Benicio"              la cosa que esta mirando
#   "tachadas": [0, 3]             las casas que ya descarto para el foco
#
# Las consultas propias de este mundo (para la generacion 3) son:
#   cosas(caso), categoria_de(caso, cosa), cumple(caso, pista, casa), choca(caso, casa),
#   cosas_de_pista(pista)
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_vecindario import CASOS        # noqa: E402

PARED = "#b8662f"                          # terracota: el color de las fachadas del vecindario
CONEJO = "conejo"

COLOR_CASA = {"roja": "#d64541", "azul": "#3a6fd8", "amarilla": "#f2c230", "verde": "#3fa34d",
              "blanca": "#f4f1ea", "morada": "#8e5bb5"}
COLOR_PERSONA = ["#e4572e", "#2e86de", "#8e44ad", "#17a589", "#d68910", "#34495e"]
PISO_FILA = ["#d9cbb8", "#cfd6c4", "#c8d0dc", "#dccfd8"]                  # un tono por fila de atributo
PISO_ANDEN = "#9a9488"


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["n"] = caso["casas"]
    caso["categorias"] = [(nombre, list(lista)) for (nombre, lista) in caso["categorias"]]
    caso["orden"] = []                                          # en este orden se ubican las cosas
    caso["de"] = {}                                             # cosa -> categoria
    for (nombre, lista) in caso["categorias"]:
        for cosa in lista:
            caso["orden"].append(cosa)
            caso["de"][cosa] = nombre
    return caso


# ----------------------------------------------------------------- consultas propias
def cosas(caso):
    """Todas las cosas por ubicar, en el orden en que se ubican."""
    return list(caso["orden"])


def categoria_de(caso, cosa):
    """'mascota', 'color', 'persona' o 'bebida'."""
    return caso["de"][cosa]


def de_la_misma_categoria(caso, cosa):
    """Las cosas de la misma categoria que esta (sin incluirla)."""
    return [x for x in caso["orden"] if caso["de"][x] == caso["de"][cosa] and x != cosa]


def cosas_de_pista(pista):
    """Las cosas que nombra una pista: una o dos."""
    if pista[0] == "en":
        return [pista[1]]
    return [pista[1], pista[2]]


def cumple(caso, pista, casa):
    """Revisa UNA pista contra un reparto (completo o a medias).
    Devuelve True, False o None (None: todavia no se puede saber)."""
    tipo = pista[0]
    if tipo == "en":
        if pista[1] not in casa:
            return None
        return casa[pista[1]] == pista[2]
    x, y = pista[1], pista[2]
    if x not in casa or y not in casa:
        return None
    a, b = casa[x], casa[y]
    if tipo == "mismo":
        return a == b
    if tipo == "distinto":
        return a != b
    if tipo == "junto":
        return abs(a - b) == 1
    if tipo == "izquierda":                       # x queda JUSTO a la izquierda de y
        return a == b - 1
    if tipo == "antes":                           # x queda en algun lugar a la izquierda de y
        return a < b
    raise ValueError("Pista desconocida: %r" % (pista,))


def choca(caso, casa):
    """Revisa un reparto (completo o a medias): una cosa de cada categoria por casa, y las pistas.
    Devuelve "" si nada choca; si no, que choco."""
    vistas = {}
    for cosa in casa:
        clave = (caso["de"][cosa], casa[cosa])
        if clave in vistas:
            return "%s y %s en la misma casa" % (nombre(caso, vistas[clave]), nombre(caso, cosa))
        vistas[clave] = cosa
    for pista in caso["pistas"]:
        if cumple(caso, pista, casa) is False:
            return "falla la pista: " + texto_pista(caso, pista)
    return ""


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"casa": {}}


def pendiente(caso, estado):
    """La cosa que toca ubicar (la primera del orden que falta), o None."""
    for cosa in caso["orden"]:
        if cosa not in estado["casa"]:
            return cosa
    return None


def completo(caso, estado):
    return pendiente(caso, estado) is None


def opciones(caso, estado):
    """Las decisiones posibles ahora: (cosa, casa) para la cosa que toca.
    No mira ninguna pista. Solo ofrece las casas que nadie de su categoria ocupa
    (como en la cueva, donde Pixie no vuelve a una casilla que ya piso)."""
    cosa = pendiente(caso, estado)
    if cosa is None:
        return []
    ocupadas = set()
    for otra in de_la_misma_categoria(caso, cosa):
        if otra in estado["casa"]:
            ocupadas.add(estado["casa"][otra])
    return [(cosa, k) for k in range(caso["n"]) if k not in ocupadas]


def aplicar(caso, estado, decision):
    cosa, k = decision
    casa = dict(estado["casa"])
    casa[cosa] = k
    return {"casa": casa}


def viola(caso, estado):
    """Devuelve "" si el estado no rompe ninguna pista; si no, cual rompio."""
    return choca(caso, estado["casa"])


def dueno_del_conejo(caso, casa):
    """La persona que vive en la casa del conejo, o None si todavia no se sabe."""
    if CONEJO not in casa:
        return None
    for cosa in casa:
        if caso["de"][cosa] == "persona" and casa[cosa] == casa[CONEJO]:
            return cosa
    return None


def respuesta(caso, estado):
    casa = estado["casa"]
    quien = dueno_del_conejo(caso, casa)
    if not completo(caso, estado) or quien is None:
        return ""
    k = casa[CONEJO]
    color = [c for c in casa if caso["de"][c] == "color" and casa[c] == k]
    if color:
        return "El conejo es de %s: vive en la casa %d, la %s" % (quien, k + 1, color[0])
    return "El conejo es de %s: vive en la casa %d" % (quien, k + 1)


# ----------------------------------------------------------------- en palabras
def nombre(caso, cosa):
    """La cosa como objeto de una frase: 'Amparo', 'la casa roja', 'el perro', 'quien toma tinto'."""
    cat = caso["de"][cosa]
    if cat == "persona":
        return cosa
    if cat == "color":
        return "la casa " + cosa
    if cat == "mascota":
        return "el " + cosa
    return "quien toma " + cosa


def _sujeto(caso, cosa):
    t = nombre(caso, cosa)
    return t[0].upper() + t[1:]


def _verbo(caso, cosa):
    return "queda" if caso["de"][cosa] == "color" else "vive"


def _mismo(caso, x, y, si):
    """Frase de 'x y y estan en la misma casa' (o en distinta, si si=False)."""
    rango = {"persona": 0, "color": 1, "mascota": 2, "bebida": 3}
    if rango[caso["de"][x]] > rango[caso["de"][y]]:
        x, y = y, x
    cx, cy = caso["de"][x], caso["de"][y]
    no = "" if si else "no "
    if cx == "persona" and cy == "color":
        return "%s %svive en la casa %s" % (x, no, y)
    if cx == "persona" and cy == "mascota":
        return "%s %stiene el %s" % (x, no, y)
    if cx == "persona" and cy == "bebida":
        return "%s %stoma %s" % (x, no, y)
    if cx == "color" and cy == "mascota":
        return "El %s %svive en la casa %s" % (y, no, x)
    if cx == "color" and cy == "bebida":
        return "En la casa %s %sse toma %s" % (x, no, y)
    if cx == "mascota" and cy == "bebida":
        return "Quien tiene el %s %stoma %s" % (x, no, y)
    return "%s y %s %sviven juntos" % (_sujeto(caso, x), nombre(caso, y), no)


def texto_pista(caso, pista):
    tipo = pista[0]
    x = pista[1]
    if tipo == "en":
        cat = caso["de"][x]
        k = pista[2] + 1
        if cat == "color":
            return "La casa %s es la número %d" % (x, k)
        if cat == "bebida":
            return "En la casa %d se toma %s" % (k, x)
        return "%s vive en la casa %d" % (_sujeto(caso, x), k)
    y = pista[2]
    if tipo == "mismo":
        frase = _mismo(caso, x, y, True)
    elif tipo == "distinto":
        frase = _mismo(caso, x, y, False)
    elif tipo == "junto":
        frase = "%s %s al lado de %s" % (_sujeto(caso, x), _verbo(caso, x), nombre(caso, y))
    elif tipo == "izquierda":
        frase = "%s %s justo a la izquierda de %s" % (_sujeto(caso, x), _verbo(caso, x), nombre(caso, y))
    elif tipo == "antes":
        frase = "%s %s más a la izquierda que %s" % (_sujeto(caso, x), _verbo(caso, x), nombre(caso, y))
    else:
        frase = str(pista)
    return frase.replace(" de el ", " del ")


def decir(caso, decision):
    """Una decision, en palabras, para la nota de la bitacora."""
    cosa, k = decision
    cat = caso["de"][cosa]
    if cat == "color":
        return "la casa %d es la %s" % (k + 1, cosa)
    if cat == "bebida":
        return "en la casa %d se toma %s" % (k + 1, cosa)
    return "%s en la casa %d" % (nombre(caso, cosa), k + 1)


def pistas(caso):
    return [texto_pista(caso, p) for p in caso["pistas"]]


# ----------------------------------------------------------------- la escena
# Cada columna es una casa (la casa 1 a la izquierda). Cada fila es una categoria:
# al fondo el color de la fachada, luego la persona, luego la mascota y la bebida.
# La ultima fila es el anden, con el numero de cada casa escrito en el piso.
def _vista(caso):
    """Las categorias en el orden en que se dibujan, del fondo hacia el frente."""
    presentes = [nom for (nom, _) in caso["categorias"]]
    return [c for c in ("color", "persona", "mascota", "bebida") if c in presentes]


def dibujar(caso, estado):
    n = caso["n"]
    vista = _vista(caso)
    filas = len(vista) + 1
    e = Escena(filas, n, titulo=caso["titulo"], ambiente="sala", pared=PARED)
    for f in range(filas):
        for c in range(n):
            e.piso(f, c, PISO_ANDEN if f == len(vista) else PISO_FILA[f % len(PISO_FILA)])
            if c < n - 1 and f < len(vista):
                e.muro(f, c, "E", bajo=True)                   # la cerca baja entre dos casas
    for c in range(n):
        e.rotulo(len(vista), c, "casa %d" % (c + 1))
    casa = estado["casa"]
    foco = estado.get("foco")
    if foco is not None and foco in caso["de"]:
        f = vista.index(caso["de"][foco])
        for k in estado.get("tachadas", []):
            e.equis(f, k)
    personas = [x for x in caso["orden"] if caso["de"][x] == "persona"]
    for cosa in caso["orden"]:
        if cosa not in casa:
            continue
        cat = caso["de"][cosa]
        f, k = vista.index(cat), casa[cosa]
        if cat == "color":
            e.caja("casa " + cosa, f, k, COLOR_CASA.get(cosa, "#888888"))
        elif cat == "persona":
            e.personaje(cosa, f, k, COLOR_PERSONA[personas.index(cosa) % len(COLOR_PERSONA)], cosa[0])
        elif cosa == CONEJO:
            e.conejo(f, k)
        else:
            e.ficha(f, k, cosa)
    if foco is not None and foco in casa and foco != CONEJO:
        e.luz(vista.index(caso["de"][foco]), casa[foco])
    if foco is not None and foco in caso["de"] and foco not in casa:
        # si de las casas del foco solo queda una, se marca: ahi tiene que ir
        quedan = [k for k in range(n) if k not in estado.get("tachadas", [])]
        if len(quedan) == 1:
            f = vista.index(caso["de"][foco])
            e.luz(f, quedan[0])
            e.ficha(f, quedan[0], foco + "?", "#1f2430")
    # el panel de pistas: se resaltan las que nombran a la cosa que se esta mirando
    lineas = []
    for pista in caso["pistas"]:
        veredicto = cumple(caso, pista, casa)
        marca = "bien" if veredicto is True else ("mal" if veredicto is False else "")
        lineas.append((texto_pista(caso, pista), marca, foco in cosas_de_pista(pista)))
    e.panel("Las pistas", lineas)
    quien = respuesta(caso, estado)
    if quien:
        e.veredicto(quien)
    return e
