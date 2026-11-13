# mundo.py  ---  La fiesta (sentar invitados)
#
# LA FICCION. Pixie da una cena y tiene una sola mesa larga. Hay tantas sillas
# como invitados, y algunos invitados se pelean entre si. Dos que se pelean no
# pueden quedar JUNTOS, es decir, en sillas que se tocan (tambien al doblar la
# esquina de la mesa, de un costado a la cabecera). Ademas, algunos invitados
# pidieron un lugar: una cabecera, el lado de la pared o el lado de la puerta.
# Izquierda y derecha se cuentan mirando la mesa desde la puerta.
# La pregunta: ¿como se arma la mesa sin peleas?
#
# EL CONTRATO. Todos los mundos del proyecto tienen estas mismas funciones.
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
#   pistas(caso)               las pistas, en palabras
#   dibujar(caso, estado)      la escena en 3D de ese estado
#
# Consultas propias de este mundo (las usa la generacion 3):
#   vecinas(caso, s)           las sillas que tocan la silla s
#   lado(caso, s)              "pared", "puerta" o "cabecera"
#   sillas_libres(caso, estado)
#   enemigos(caso, persona)    con quienes se pelea
#   cual_cabecera(caso, s)     "izquierda" o "derecha", vistas desde la puerta
#   cumple(caso, pista, silla) True, False o None (todavia no se sabe)
#
# Las sillas se numeran desde 0 en el codigo y van en orden alrededor de la mesa: el
# lado de la pared de izquierda a derecha, la cabecera derecha, el lado de la puerta
# de derecha a izquierda y la cabecera izquierda. En pantalla no se usan numeros: se
# dice "la segunda silla del lado de la puerta", contando desde la izquierda.
#
# Un ESTADO de este mundo es un diccionario:
#   {"silla": {"Amparo": 2, "Benicio": 5}}      quien esta sentado y en que silla
# El agente puede agregarle dos datos opcionales para que se vean en la escena:
#   "foco": "Clemencia"                 a quien esta mirando
#   "tachadas": [3, 4]                  sillas que ya descarto para el foco
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_fiesta import CASOS            # noqa: E402

PARED = "#a23b8c"                          # fucsia de fiesta: el color de este mundo
COLOR_PISO = "#d9cbb8"
COLOR_SILLA = {"pared": "#b07a4f", "puerta": "#b07a4f", "cabecera": "#d9a441"}
COLOR_MESA = "#7a4b2e"
COLOR_PERSONA = ["#e4572e", "#2e86de", "#8e44ad", "#17a589", "#d68910", "#c0392b", "#34495e", "#5d6d7e"]


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["mesa"] = [tuple(x) for x in caso["mesa"]]
    caso["sillas"] = [tuple(x) for x in caso["sillas"]]
    caso["espera"] = [tuple(x) for x in caso["espera"]]
    fila_mesa = caso["mesa"][0][0]
    caso["lados"] = []
    for (f, c) in caso["sillas"]:
        if f < fila_mesa:
            caso["lados"].append("pared")
        elif f > fila_mesa:
            caso["lados"].append("puerta")
        else:
            caso["lados"].append("cabecera")
    # dos sillas estan juntas si sus casillas se tocan, tambien en diagonal (al doblar la esquina)
    caso["junto_a"] = []
    for (f, c) in caso["sillas"]:
        lista = []
        for j, (g, d) in enumerate(caso["sillas"]):
            if (g, d) != (f, c) and abs(g - f) <= 1 and abs(d - c) <= 1:
                lista.append(j)
        caso["junto_a"].append(lista)
    return caso


# ----------------------------------------------------------------- consultas propias
def vecinas(caso, s):
    """Las sillas que tocan la silla s."""
    return list(caso["junto_a"][s])


def lado(caso, s):
    """De que lado de la mesa esta la silla s: "pared", "puerta" o "cabecera"."""
    return caso["lados"][s]


def cual_cabecera(caso, s):
    """Para una silla de cabecera: "izquierda" o "derecha" (vistas desde la puerta)."""
    return "izquierda" if caso["sillas"][s][1] < caso["mesa"][0][1] else "derecha"


def sillas_libres(caso, estado):
    ocupadas = set(estado["silla"].values())
    return [s for s in range(len(caso["sillas"])) if s not in ocupadas]


def enemigos(caso, persona):
    """Con quienes se pelea esta persona."""
    lista = []
    for pista in caso["pistas"]:
        if pista[0] == "pelea" and persona in (pista[1], pista[2]):
            lista.append(pista[2] if pista[1] == persona else pista[1])
    return lista


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"silla": {}}


def pendiente(caso, estado):
    """A quien le toca sentarse (el primero de la lista que falta), o None."""
    for p in caso["invitados"]:
        if p not in estado["silla"]:
            return p
    return None


def completo(caso, estado):
    return pendiente(caso, estado) is None


def opciones(caso, estado):
    """Las decisiones posibles ahora: (persona, silla) para la persona que toca.
    No mira ninguna pista: ofrece TODAS las sillas que siguen vacias."""
    p = pendiente(caso, estado)
    if p is None:
        return []
    return [(p, s) for s in sillas_libres(caso, estado)]


def aplicar(caso, estado, decision):
    persona, s = decision
    silla = dict(estado["silla"])
    silla[persona] = s
    return {"silla": silla}


def cumple(caso, pista, silla):
    """Revisa UNA pista con las sillas dadas. Devuelve True, False o None (None: todavia no se sabe)."""
    tipo, p = pista[0], pista[1]
    if p not in silla:
        return None
    if tipo == "pelea":
        q = pista[2]
        if q not in silla:
            return None
        return silla[q] not in caso["junto_a"][silla[p]]
    if tipo == "cabecera":
        if lado(caso, silla[p]) != "cabecera":
            return False
        return len(pista) < 3 or cual_cabecera(caso, silla[p]) == pista[2]
    if tipo == "lado":
        return lado(caso, silla[p]) == pista[2]
    raise ValueError("Pista desconocida: %r" % (pista,))


def viola(caso, estado):
    """Devuelve "" si el estado no rompe ninguna regla; si no, cual rompio."""
    silla = estado["silla"]
    vistos = {}
    for p in silla:
        if silla[p] in vistos:
            return "%s y %s en la misma silla" % (vistos[silla[p]], p)
        vistos[silla[p]] = p
    for pista in caso["pistas"]:
        if cumple(caso, pista, silla) is False:
            if pista[0] == "pelea":
                return "%s y %s quedaron juntos y se pelean" % (pista[1], pista[2])
            if pista[0] == "cabecera":
                lugar = "la cabecera" + (" " + pista[2] if len(pista) > 2 else "")
            else:
                lugar = "el lado de la " + pista[2]
            return "%s pidió %s y no quedó ahí" % (pista[1], lugar)
    return ""


def respuesta(caso, estado):
    if not completo(caso, estado) or viola(caso, estado):
        return ""
    quien = {s: p for (p, s) in estado["silla"].items()}
    pared = [quien[s] for s in range(len(caso["sillas"])) if lado(caso, s) == "pared"]
    puerta = [quien[s] for s in range(len(caso["sillas"])) if lado(caso, s) == "puerta"]
    cab = [quien[s] for s in range(len(caso["sillas"])) if lado(caso, s) == "cabecera"]
    puerta.reverse()                       # de izquierda a derecha, como se ve desde la puerta
    texto = "Pared: %s · puerta: %s" % (", ".join(pared), ", ".join(puerta))
    if cab:
        texto += " · cabecera: " + " y ".join(cab)
    return texto


# ----------------------------------------------------------------- en palabras
def texto_pista(pista):
    tipo, p = pista[0], pista[1]
    if tipo == "pelea":
        return "%s y %s se pelean" % (p, pista[2])
    if tipo == "cabecera":
        if len(pista) > 2:
            return "%s va en la cabecera %s" % (p, pista[2])
        return "%s va en la cabecera" % p
    if tipo == "lado":
        return "%s va del lado de la %s" % (p, pista[2])
    return str(pista)


ORDINAL = ["primera", "segunda", "tercera", "cuarta", "quinta", "sexta"]


def nombre_silla(caso, s):
    """La silla s en palabras, como la ve quien mira la mesa desde la puerta."""
    ld = lado(caso, s)
    if ld == "cabecera":
        if sum(1 for x in caso["lados"] if x == "cabecera") > 1:
            return "la cabecera " + cual_cabecera(caso, s)
        return "la cabecera"
    mismas = sorted((c, t) for t, (f, c) in enumerate(caso["sillas"]) if caso["lados"][t] == ld)
    puesto = [t for (c, t) in mismas].index(s)
    return "la %s silla del lado de la %s" % (ORDINAL[puesto], ld)


def decir(caso, decision):
    """Una decision, en palabras, para la nota de la bitacora."""
    persona, s = decision
    return "%s en %s" % (persona, nombre_silla(caso, s))


def pistas(caso):
    return [texto_pista(p) for p in caso["pistas"]]


def renglones(caso):
    """Las pistas agrupadas para el panel: una linea con todas las peleas de cada invitado
    (contadas una sola vez) y una linea por cada peticion de lugar. Devuelve (texto, pistas)."""
    lista = []
    for p in caso["invitados"]:
        grupo = [x for x in caso["pistas"] if x[0] == "pelea" and x[1] == p]
        if grupo:
            nombres = [x[2] for x in grupo]
            texto = nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]
            lista.append(("%s se pelea con %s" % (p, texto), grupo))
    for x in caso["pistas"]:
        if x[0] != "pelea":
            lista.append((texto_pista(x), [x]))
    return lista


# ----------------------------------------------------------------- la escena
def dibujar(caso, estado):
    filas, columnas = caso["filas"], caso["columnas"]
    e = Escena(filas, columnas, titulo=caso["titulo"], ambiente="sala", pared=PARED)
    sillas = caso["sillas"]
    for f in range(filas):
        for c in range(columnas):
            if (f, c) in caso["espera"]:
                e.salida(f, c)                       # la entrada: aqui esperan los que no se han sentado
            elif (f, c) in sillas:
                e.piso(f, c, COLOR_SILLA[lado(caso, sillas.index((f, c)))])
            else:
                e.piso(f, c, COLOR_PISO)
    for (f, c) in caso["mesa"]:
        e.mueble(f, c, "mesa", COLOR_MESA)
    silla = estado["silla"]
    foco = estado.get("foco")
    for s in estado.get("tachadas", []):
        f, c = sillas[s]
        e.equis(f, c)
    for i, p in enumerate(caso["invitados"]):
        if p in silla:
            f, c = sillas[silla[p]]
        else:
            f, c = caso["espera"][i]
        e.personaje(p, f, c, COLOR_PERSONA[i % len(COLOR_PERSONA)], p[0])
    lineas = []
    for (texto, grupo) in renglones(caso):
        veredictos = [cumple(caso, pista, silla) for pista in grupo]
        if False in veredictos:
            marca = "mal"
        elif all(v is True for v in veredictos):
            marca = "bien"
        else:
            marca = ""
        lineas.append((texto, marca, foco is not None and any(foco in pista[1:] for pista in grupo)))
    e.panel("Las peticiones", lineas)
    r = respuesta(caso, estado)
    if r:
        e.veredicto(r)
    return e
