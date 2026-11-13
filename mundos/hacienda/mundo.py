# mundo.py  ---  El robo en la hacienda (un murdoku)
#
# LA FICCION. Anoche desaparecio lo que guardaba el cofre de la hacienda.
# A esa hora cada persona estaba quieta en una casilla, y el cofre tambien
# ocupa la suya. Se sabe que nunca hubo dos en la misma fila ni en la misma
# columna (contando el cofre). Cada persona dejo una pista sobre donde estaba.
# El ladron es quien quedo A SOLAS con el cofre en su habitacion.
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
#   pistas(caso)               las pistas, en palabras
#   dibujar(caso, estado)      la escena en 3D de ese estado
#
# Un ESTADO de este mundo es un diccionario:
#   {"lugar": {"Amparo": (0, 2), "Cofre": (3, 1)}}     quien esta ya ubicado y donde
# El agente puede agregarle dos datos opcionales para que se vean en la escena:
#   "foco": "Benicio"                    a quien esta mirando
#   "tachadas": [(0, 0), (0, 1)]         casillas que ya descarto para el foco
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_hacienda import CASOS          # noqa: E402

COFRE = "Cofre"
COLOR_HABITACION = ["#6b5a4e", "#4f6152", "#4c5a6e", "#6e6648", "#5e5068", "#6e4f4f", "#4e6664"]   # tonos oscuros, uno por habitacion
COLOR_PERSONA = ["#e4572e", "#2e86de", "#8e44ad", "#17a589", "#d68910", "#c0392b", "#34495e"]
COLOR_MUEBLE = {"cama": "#7d5a44", "mesa": "#a9744f", "planta": "#3f9b57", "estufa": "#6b7480",
                "piano": "#2b2f3a", "fuente": "#5aa7d6", "barril": "#8c5a2b", "telar": "#b0855b"}


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["n"] = len(caso["plano"])
    caso["muebles"] = {tuple(k): v for (k, v) in caso["muebles"]}
    caso["orden"] = list(caso["personas"]) + [COFRE]          # en este orden se ubican
    return caso


# ----------------------------------------------------------------- geometria
def habitacion_de(caso, casilla):
    """El nombre de la habitacion donde esta la casilla (f, c)."""
    f, c = casilla
    return caso["habitaciones"][caso["plano"][f][c]]


def casillas_libres(caso):
    """Todas las casillas donde puede pararse alguien (las que no tienen mueble)."""
    libres = []
    for f in range(caso["n"]):
        for c in range(caso["n"]):
            if (f, c) not in caso["muebles"]:
                libres.append((f, c))
    return libres


def junto_a_mueble(caso, casilla, mueble):
    """¿La casilla toca (arriba, abajo, izquierda o derecha) un mueble de ese tipo, en su misma habitacion?"""
    f, c = casilla
    for (g, d) in ((f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)):
        if caso["muebles"].get((g, d)) == mueble and habitacion_de(caso, (g, d)) == habitacion_de(caso, casilla):
            return True
    return False


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"lugar": {}}


def pendiente(caso, estado):
    """A quien le toca ubicarse (el primero del orden que falta), o None."""
    for p in caso["orden"]:
        if p not in estado["lugar"]:
            return p
    return None


def completo(caso, estado):
    return pendiente(caso, estado) is None


def opciones(caso, estado):
    """Las decisiones posibles ahora: (persona, casilla) para la persona que toca.
    No mira ninguna regla: ofrece TODAS las casillas sin mueble."""
    p = pendiente(caso, estado)
    if p is None:
        return []
    return [(p, casilla) for casilla in casillas_libres(caso)]


def aplicar(caso, estado, decision):
    persona, casilla = decision
    lugar = dict(estado["lugar"])
    lugar[persona] = casilla
    return {"lugar": lugar}


def cumple(caso, pista, lugar):
    """Revisa UNA pista. Devuelve True, False o None (None: todavia no se puede saber)."""
    tipo, p = pista[0], pista[1]
    if p not in lugar:
        return None
    donde = lugar[p]
    if tipo == "en":
        return habitacion_de(caso, donde) == pista[2]
    if tipo == "no_en":
        return habitacion_de(caso, donde) != pista[2]
    if tipo == "fila":
        return donde[0] == pista[2]
    if tipo == "columna":
        return donde[1] == pista[2]
    if tipo == "junto":
        return junto_a_mueble(caso, donde, pista[2])
    if tipo in ("con", "sin", "norte", "oeste"):
        q = pista[2]
        if q not in lugar:
            return None
        if tipo == "con":
            return habitacion_de(caso, donde) == habitacion_de(caso, lugar[q])
        if tipo == "sin":
            return habitacion_de(caso, donde) != habitacion_de(caso, lugar[q])
        if tipo == "norte":
            return donde[0] < lugar[q][0]
        return donde[1] < lugar[q][1]
    if tipo == "solo":
        mia = habitacion_de(caso, donde)
        for q in lugar:
            if q != p and habitacion_de(caso, lugar[q]) == mia:
                return False
        return True if len(lugar) == len(caso["orden"]) else None
    raise ValueError("Pista desconocida: %r" % (pista,))


def choca(caso, lugar):
    """Revisa un reparto (completo o a medias): fila, columna y pistas.
    Devuelve "" si nada choca; si no, que choco."""
    nombres = list(lugar)
    for i in range(len(nombres)):
        for j in range(i):
            a, b = lugar[nombres[i]], lugar[nombres[j]]
            if a == b:
                return "%s y %s en la misma casilla" % (nombres[j], nombres[i])
            if a[0] == b[0]:
                return "%s y %s en la misma fila" % (nombres[j], nombres[i])
            if a[1] == b[1]:
                return "%s y %s en la misma columna" % (nombres[j], nombres[i])
    for pista in caso["pistas"]:
        if cumple(caso, pista, lugar) is False:
            return "falla la pista: " + texto_pista(pista)
    return ""


def viola(caso, estado):
    """Devuelve "" si el estado no rompe ninguna regla; si no, cual rompio."""
    lugar = estado["lugar"]
    falla = choca(caso, lugar)
    if falla:
        return falla
    if len(lugar) == len(caso["orden"]) and len(acompanantes(caso, lugar)) != 1:
        return "nadie quedó a solas con el cofre"
    return ""


def acompanantes(caso, lugar):
    """Las personas que estan en la habitacion del cofre."""
    if COFRE not in lugar:
        return []
    sala = habitacion_de(caso, lugar[COFRE])
    return [p for p in lugar if p != COFRE and habitacion_de(caso, lugar[p]) == sala]


def respuesta(caso, estado):
    quien = acompanantes(caso, estado["lugar"])
    if completo(caso, estado) and len(quien) == 1:
        return "Fue %s, en %s" % (quien[0], habitacion_de(caso, estado["lugar"][COFRE]))
    return ""


# ----------------------------------------------------------------- pistas en palabras
def texto_pista(pista):
    tipo, p = pista[0], pista[1]
    sujeto = "El cofre" if p == COFRE else p
    if tipo == "en":
        return "%s estaba en %s" % (sujeto, pista[2])
    if tipo == "no_en":
        return "%s no estaba en %s" % (sujeto, pista[2])
    if tipo == "fila":
        return "%s estaba en la fila %d" % (sujeto, pista[2] + 1)
    if tipo == "columna":
        return "%s estaba en la columna %d" % (sujeto, pista[2] + 1)
    if tipo == "junto":
        return ("%s estaba junto a %s" % (sujeto, ARTICULO[pista[2]])).replace(" a el ", " al ")
    if tipo == "con":
        return "%s compartía habitación con %s" % (sujeto, _obj(pista[2]))
    if tipo == "sin":
        return "%s no compartía habitación con %s" % (sujeto, _obj(pista[2]))
    if tipo == "norte":
        return "%s estaba más al norte que %s" % (sujeto, _obj(pista[2]))
    if tipo == "oeste":
        return "%s estaba más al oeste que %s" % (sujeto, _obj(pista[2]))
    if tipo == "solo":
        return "%s estaba a solas en su habitación" % sujeto
    return str(pista)


ARTICULO = {"cama": "la cama", "mesa": "la mesa", "planta": "la planta", "estufa": "la estufa",
            "piano": "el piano", "fuente": "la fuente", "barril": "el barril", "telar": "el telar"}


def _obj(q):
    return "el cofre" if q == COFRE else q


def decir(caso, decision):
    """Una decision, en palabras, para la nota de la bitacora."""
    persona, (f, c) = decision
    return "%s en %s, fila %d, columna %d" % (_obj(persona), habitacion_de(caso, (f, c)), f + 1, c + 1)


def pistas(caso):
    return [texto_pista(p) for p in caso["pistas"]]


# ----------------------------------------------------------------- la escena
def dibujar(caso, estado):
    n = caso["n"]
    e = Escena(n, n, titulo=caso["titulo"], ambiente="sala", pared="#8f1d30")
    plano = caso["plano"]
    for f in range(n):
        for c in range(n):
            e.piso(f, c, COLOR_HABITACION[plano[f][c] % len(COLOR_HABITACION)])
            # muros: en el borde de la casa y entre habitaciones distintas
            if f == 0:
                e.muro(f, c, "N")
            if c == 0:
                e.muro(f, c, "O")
            if f == n - 1 or plano[f + 1][c] != plano[f][c]:
                e.muro(f, c, "S", bajo=(f != n - 1))
            if c == n - 1 or plano[f][c + 1] != plano[f][c]:
                e.muro(f, c, "E", bajo=(c != n - 1))
    for (f, c) in sorted(caso["muebles"]):
        tipo = caso["muebles"][(f, c)]
        e.mueble(f, c, tipo, COLOR_MUEBLE.get(tipo, "#888888"))
    # el nombre de cada habitacion, escrito en el piso de su primera casilla
    vistas = set()
    for f in range(n):
        for c in range(n):
            h = plano[f][c]
            if h not in vistas and (f, c) not in caso["muebles"]:
                vistas.add(h)
                e.rotulo(f, c, caso["habitaciones"][h])
    foco = estado.get("foco")
    for casilla in estado.get("tachadas", []):
        e.equis(casilla[0], casilla[1])
    lugar = estado["lugar"]
    for p in caso["orden"]:
        if p in lugar:
            f, c = lugar[p]
            if p == COFRE:
                e.cofre(f, c)
            else:
                e.personaje(p, f, c, COLOR_PERSONA[caso["personas"].index(p) % len(COLOR_PERSONA)], p[0])
    # el panel de pistas: se resalta la de la persona que se esta mirando
    lineas = []
    for pista in caso["pistas"]:
        veredicto = cumple(caso, pista, lugar)
        marca = "bien" if veredicto is True else ("mal" if veredicto is False else "")
        lineas.append((texto_pista(pista), marca, pista[1] == foco))
    e.panel("Las pistas", lineas)
    quien = respuesta(caso, estado)
    if quien:
        e.veredicto(quien)
    return e
