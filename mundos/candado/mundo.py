# mundo.py  ---  El candado (un codigo con pistas)
#
# LA FICCION. En la puerta del cuarto de herramientas hay un candado de ruedas.
# Cada rueda muestra un digito. Es un candado de feria: a cada intento enciende
# una luz verde por cada digito que quedo en su sitio y una amarilla por cada
# digito que esta en la clave pero en otra rueda. Alguien ya hizo varios
# intentos y los dejo anotados en la pared, con sus luces. Se sabe ademas que
# la clave no repite digitos. Pregunta: ¿cual es la clave?
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
# Las consultas propias de este mundo (las usa la generacion 3) son
#   luces(intento, clave)      cuantos digitos de la clave estan en su sitio y cuantos en otra rueda
#   cuentas(caso, pista, clave)  lo mismo, pero con una clave a medias
#
# Un ESTADO de este mundo es un diccionario:
#   {"clave": [7, 2]}          los digitos ya puestos, de la rueda 1 en adelante
# Las ruedas se ponen en orden: primero la 1, luego la 2, y asi.
# El agente puede agregarle datos opcionales para que se vean en la escena:
#   "tachadas": [(3, 0), ...]  (digito, rueda) que ya descarto: salen con una equis
#   "fijas":    [(7, 1), ...]  (digito, rueda) que dedujo seguras: salen iluminadas
#   "foco": 2                  la pista (su posicion en la lista) que esta usando
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_candado import CASOS           # noqa: E402

PARED = "#2e6b5e"                          # verde petroleo: el color de la sala del candado
COLOR_RUEDA = ["#c9a86a", "#b8955a"]       # laton claro, alternado por rueda
COLOR_LECTURA = "#3a3f47"                  # la columna de lectura, donde se para Pixie
COLOR_DIGITO = "#1f2430"                   # el digito puesto en una rueda
COLOR_REGLA = "#5d6470"                    # los numeros de la fila de adelante
COLOR_FIJA = "#7bd88f"
NUMEROS = ["ninguno", "uno", "dos", "tres", "cuatro", "cinco", "seis"]


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["intentos"] = [(tuple(a), b, r) for (a, b, r) in caso["intentos"]]
    return caso


# ----------------------------------------------------------------- las luces
def luces(intento, clave):
    """Para una clave completa: (cuantos digitos del intento estan en su sitio, cuantos en otra rueda)."""
    en_sitio = 0
    for i in range(len(clave)):
        if intento[i] == clave[i]:
            en_sitio = en_sitio + 1
    comunes = len(set(intento) & set(clave))
    return en_sitio, comunes - en_sitio


def cuentas(caso, pista, clave):
    """Para una clave a medias: (en su sitio, en otra rueda) que YA aportan las ruedas puestas.
    Como la clave no repite digitos, un digito puesto que esta en el intento ya no cambia de luz."""
    intento = pista[0]
    en_sitio, en_otra = 0, 0
    for i in range(len(clave)):
        if clave[i] == intento[i]:
            en_sitio = en_sitio + 1
        elif clave[i] in intento:
            en_otra = en_otra + 1
    return en_sitio, en_otra


def cumple(caso, pista, clave):
    """Revisa UNA pista. Devuelve True, False o None (None: todavia no se puede saber)."""
    intento, verdes, amarillas = pista
    s, o = cuentas(caso, pista, clave)
    faltan = caso["ruedas"] - len(clave)
    if s > verdes or o > amarillas:
        return False                                     # ya sobran luces
    if (verdes - s) + (amarillas - o) > faltan:
        return False                                     # no quedan ruedas para las luces que faltan
    if faltan == 0:
        return True
    return None


# ----------------------------------------------------------------- busqueda
def inicio(caso):
    return {"clave": []}


def completo(caso, estado):
    return len(estado["clave"]) == caso["ruedas"]


def opciones(caso, estado):
    """Las decisiones posibles ahora: (rueda, digito) para la siguiente rueda.
    No mira ninguna regla: ofrece TODOS los digitos de la rueda."""
    if completo(caso, estado):
        return []
    rueda = len(estado["clave"])
    return [(rueda, d) for d in range(caso["digitos"])]


def aplicar(caso, estado, decision):
    rueda, digito = decision
    return {"clave": estado["clave"][:rueda] + [digito]}


def repetido(clave):
    """El primer digito que se repite en la clave, o None."""
    vistos = set()
    for d in clave:
        if d in vistos:
            return d
        vistos.add(d)
    return None


def viola(caso, estado):
    """Devuelve "" si el estado no rompe ninguna regla; si no, cual rompio."""
    clave = estado["clave"]
    d = repetido(clave)
    if d is not None:
        return "la clave repite el %d" % d
    for pista in caso["intentos"]:
        if cumple(caso, pista, clave) is False:
            return "falla la pista " + escribir(pista[0])
    return ""


def respuesta(caso, estado):
    if completo(caso, estado) and viola(caso, estado) == "":
        return "La clave es " + escribir(estado["clave"])
    return ""


# ----------------------------------------------------------------- en palabras
def escribir(codigo):
    return " ".join(str(d) for d in codigo)


def texto_pista(pista):
    intento, verdes, amarillas = pista
    if verdes == 0 and amarillas == 0:
        return "%s: ninguno está en la clave" % escribir(intento)
    partes = []
    if verdes:
        partes.append("%s en su sitio" % NUMEROS[verdes])
    if amarillas:
        partes.append("%s en otra rueda" % NUMEROS[amarillas])
    return "%s: %s" % (escribir(intento), " y ".join(partes))


def decir(caso, decision):
    rueda, digito = decision
    return "rueda %d en el %d" % (rueda + 1, digito)


def pistas(caso):
    return ["La clave no repite dígitos"] + [texto_pista(p) for p in caso["intentos"]]


# ----------------------------------------------------------------- la escena
# El tablero: una fila por rueda (la rueda 1 al fondo) y una columna por digito.
# La columna 0 es la de lectura: ahi se para Pixie, frente a la rueda que gira.
# La fila de adelante es una regla con los digitos parados, para leer las columnas.
def dibujar(caso, estado):
    n, k = caso["ruedas"], caso["digitos"]
    e = Escena(n + 1, k + 1, titulo=caso["titulo"], ambiente="sala", pared=PARED)
    e.piso(n, 0, COLOR_LECTURA)
    for d in range(k):
        e.piso(n, d + 1, COLOR_LECTURA)
        e.ficha(n, d + 1, str(d), COLOR_REGLA)
    for f in range(n):
        e.piso(f, 0, COLOR_LECTURA)
        e.rotulo(f, 0, "rueda %d" % (f + 1))
        e.muro(f, 0, "E", bajo=True)
        for d in range(k):
            e.piso(f, d + 1, COLOR_RUEDA[f % 2])
            e.rotulo(f, d + 1, str(d))
    for c in range(k + 1):
        e.muro(0, c, "N")
    clave = estado["clave"]
    for (d, rueda) in estado.get("tachadas", []):
        e.equis(rueda, d + 1)
    for (d, rueda) in estado.get("fijas", []):
        e.luz(rueda, d + 1, COLOR_FIJA)
    for rueda in range(len(clave)):
        e.luz(rueda, clave[rueda] + 1)
        e.ficha(rueda, clave[rueda] + 1, str(clave[rueda]), COLOR_DIGITO)
    # Pixie, frente a la ultima rueda que giro (o a la primera, si no ha girado ninguna)
    e.conejo(max(len(clave) - 1, 0), 0)
    # el panel de pistas: se resalta la que el agente esta usando
    foco = estado.get("foco")
    lineas = []
    rep = repetido(clave)
    lineas.append(("La clave no repite dígitos", "mal" if rep is not None else "", foco == -1))
    for i, pista in enumerate(caso["intentos"]):
        veredicto = cumple(caso, pista, clave)
        marca = "bien" if veredicto is True else ("mal" if veredicto is False else "")
        lineas.append((texto_pista(pista), marca, foco == i))
    e.panel("Los intentos", lineas)
    quien = respuesta(caso, estado)
    if quien:
        e.veredicto(quien)
    return e
