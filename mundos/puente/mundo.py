# mundo.py  ---  El puente de noche
#
# LA FICCION. Pixie y sus amigos vuelven de noche a casa. Para llegar tienen que
# pasar del monte a la otra orilla por un puente colgante sobre la quebrada. El
# puente aguanta a dos a la vez. Tienen UNA linterna y nadie pisa el puente sin
# ella: dos que cruzan juntos van al paso del mas lento, y alguien tiene que
# devolver la linterna para los que esperan. A la bateria le quedan pocos minutos.
# En el monte, cuando se queda sin linterna, hay dos peligros: un miedoso no se
# queda sin compania, y dos que estan peleados no pueden quedar juntos. (En la
# otra orilla esta la casa con la luz prendida: alla no pasa nada.)
# La pregunta: ¿cruzan todos antes de que se apague la linterna?
#
# Es un mundo de OPTIMIZACION: la bateria alcanza justo para el mejor plan, asi
# que la unica forma de que crucen todos es el plan optimo, y la respuesta da el
# tiempo de ese plan.
#
# Cumple el mismo contrato que los demas mundos (ver CONTRATO.md).
# Un ESTADO es un diccionario:
#   {"viajes": [("Pixie", "Rosa"), ("Pixie",), ...]}    los grupos que han pisado el puente, en orden.
#   El primer viaje va del monte a la otra orilla, el segundo vuelve, y asi alternan
#   (la linterna siempre va con el que cruza).
# El agente puede agregar, para que se vea en la escena:
#   "cota": 9          lo minimo que falta, en el mejor caso (sale en el panel)
#   "foco": ("Pixie",) un grupo que esta mirando sin haberlo mandado (se marca en naranja)
import os
import sys
from itertools import combinations

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_puente import CASOS            # noqa: E402

PARED = "#2f5d50"        # verde de monte de noche: el color de este mundo
CUPO = 2                 # el puente aguanta a dos


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["nombres"] = [g[0] for g in caso["gente"]]
    caso["minutos"] = {g[0]: g[1] for g in caso["gente"]}
    caso["miedosos"] = list(caso.get("miedosos", []))
    caso["peleados"] = [tuple(par) for par in caso.get("peleados", [])]
    return caso


# ----------------------------------------------------------------- lo que se puede preguntar del puente
def reparto(caso, viajes):
    """Despues de esos viajes: (quienes estan ALLA, en la otra orilla, como frozenset; ¿la linterna esta alla?)."""
    alla = set()
    for k, grupo in enumerate(viajes):
        if k % 2 == 0:
            alla.update(grupo)
        else:
            alla.difference_update(grupo)
    return frozenset(alla), len(viajes) % 2 == 1


def aca(caso, alla):
    """Los que siguen en la orilla de salida, en el orden del caso."""
    return [p for p in caso["nombres"] if p not in alla]


def duracion(caso, grupo):
    """Lo que tarda un grupo en cruzar: el paso del mas lento."""
    return max(caso["minutos"][p] for p in grupo)


def tiempo(caso, estado):
    """Minutos gastados hasta ahora."""
    return sum(duracion(caso, g) for g in estado["viajes"])


def bateria(caso, estado):
    """Minutos que le quedan a la linterna (negativo si ya se apago)."""
    return caso["linterna"] - tiempo(caso, estado)


def a_oscuras(caso, alla, linterna_alla):
    """Lo que sale mal en el monte (la orilla de salida) cuando queda sin linterna: "" si nada.
    En la otra orilla esta la casa con la luz prendida: alla no pasa nada."""
    if not linterna_alla:
        return ""
    monte = aca(caso, alla)
    if len(monte) == 1 and monte[0] in caso["miedosos"]:
        return "%s quedó sin compañía en el monte, a oscuras" % monte[0]
    for (a, b) in caso["peleados"]:
        if a in monte and b in monte:
            return "%s y %s compartieron el monte a oscuras y pelearon" % (a, b)
    return ""


def mejor_caso(caso, alla, linterna_alla):
    """Lo MINIMO que falta para que crucen todos desde este reparto, aun en el mejor caso.
    Nunca se pasa: cuenta los viajes de ida que hacen falta como si cada uno costara lo menos
    posible (los dos mas lentos juntos, luego los dos siguientes...) y cada vuelta como el mas
    rapido de todos."""
    quedan = aca(caso, alla)
    if not quedan:
        return 0
    rapido = min(caso["minutos"].values())
    if linterna_alla:
        # alguien tiene que volver primero con la linterna, y despues ese alguien cruza otra vez
        mejor = None
        for r in alla:
            c = caso["minutos"][r] + _ida(caso, quedan + [r], rapido)
            if mejor is None or c < mejor:
                mejor = c
        return mejor
    return _ida(caso, quedan, rapido)


def _ida(caso, quedan, rapido):
    """Cota con la linterna en la orilla de salida y esos que quedan."""
    k = len(quedan)
    if k <= 2:
        return duracion(caso, quedan)
    lentos = sorted((caso["minutos"][p] for p in quedan), reverse=True)
    idas = sum(lentos[0::2])                  # el 1o, el 3o, el 5o mas lento: cada uno va en un viaje distinto
    viajes_ida = k - 1                        # cada ida lleva a lo mas dos y cada vuelta trae a uno
    extra = viajes_ida - len(lentos[0::2])    # idas que sobran, al menos de un minuto rapido
    vueltas = k - 2
    return idas + max(0, extra) * rapido + vueltas * rapido


# ----------------------------------------------------------------- el contrato
def inicio(caso):
    return {"viajes": []}


def opciones(caso, estado):
    """Los grupos que pueden pisar el puente ahora: de uno o de dos, de la orilla donde esta la
    linterna. No mira el miedo, ni las peleas, ni la bateria. Solo deja por fuera un viaje que
    repita un reparto por el que ya se paso (eso seria dar vueltas)."""
    alla, linterna_alla = reparto(caso, estado["viajes"])
    if len(alla) == len(caso["nombres"]) or bateria(caso, estado) <= 0:
        return []
    orilla = sorted(alla, key=caso["nombres"].index) if linterna_alla else aca(caso, alla)
    vistos = set()
    for k in range(len(estado["viajes"]) + 1):
        vistos.add(reparto(caso, estado["viajes"][:k]))
    grupos = []
    for t in range(1, CUPO + 1):
        for grupo in combinations(orilla, t):
            if reparto(caso, estado["viajes"] + [grupo]) not in vistos:
                grupos.append(grupo)
    return grupos


def completo(caso, estado):
    return len(opciones(caso, estado)) == 0


def aplicar(caso, estado, decision):
    return {"viajes": estado["viajes"] + [tuple(decision)]}


def viola(caso, estado):
    viajes = estado["viajes"]
    for k, grupo in enumerate(viajes):
        falla = a_oscuras(caso, *reparto(caso, viajes[:k + 1]))
        if falla:
            return falla
    if bateria(caso, estado) < 0:
        return "se apagó la linterna en el puente"
    alla, _ = reparto(caso, viajes)
    if len(alla) < len(caso["nombres"]) and completo(caso, estado):
        if bateria(caso, estado) <= 0:
            return "se apagó la linterna con gente en la orilla"
        return "no queda un viaje nuevo"
    return ""


def decir(caso, decision):
    grupo = list(decision)
    if len(grupo) == 1:
        nombres = grupo[0]
    else:
        nombres = ", ".join(grupo[:-1]) + " y " + grupo[-1]
    return "%s al puente (%d min)" % (nombres, duracion(caso, grupo))


def respuesta(caso, estado):
    alla, _ = reparto(caso, estado["viajes"])
    if len(alla) == len(caso["nombres"]) and viola(caso, estado) == "":
        return "Sí: cruzan todos en %d minutos, %d viajes" % (tiempo(caso, estado), len(estado["viajes"]))
    return ""


def texto_regla(caso, regla):
    tipo = regla[0]
    if tipo == "miedo":
        return "%s no se queda sin compañía a oscuras" % regla[1]
    return "%s y %s pelean si comparten la oscuridad" % (regla[1], regla[2])


def reglas(caso):
    """Las reglas del monte, como tuplas: ("miedo", p) o ("pelea", a, b)."""
    return [("miedo", p) for p in caso["miedosos"]] + [("pelea", a, b) for (a, b) in caso["peleados"]]


def rompe(caso, regla, alla, linterna_alla):
    """¿Este reparto rompe esa regla del monte?"""
    if not linterna_alla:
        return False
    monte = aca(caso, alla)
    if regla[0] == "miedo":
        return monte == [regla[1]]
    return regla[1] in monte and regla[2] in monte


def pistas(caso):
    lineas = ["La linterna dura %d minutos." % caso["linterna"],
              "El puente aguanta a dos y nadie lo pisa sin la linterna.",
              "Dos juntos van al paso del más lento."]
    for regla in reglas(caso):
        lineas.append(texto_regla(caso, regla) + ".")
    return lineas


# ----------------------------------------------------------------- la escena
#  columnas: 0 nombres · 1 el monte (orilla de salida) · 2..4 el puente · 5 la otra orilla · 6 la casa
#  filas:    0 quebrada · 1..n una por persona · n+1 y n+2 quebrada (la ultima queda bajo los subtitulos)
COLOR = ["#e4572e", "#2e86de", "#8e44ad", "#17a589", "#d68910", "#c0392b", "#34495e", "#7f8c8d"]
MONTE, CASA, TABLA, AMARILLO = "#2f4a2c", "#5b6b4a", "#8a6a45", "#ffb000"


def dibujar(caso, estado):
    gente = caso["nombres"]
    n = len(gente)
    filas, cols = n + 3, 7
    e = Escena(filas, cols, titulo=caso["titulo"], ambiente="sala", pared=PARED)
    for f in range(filas):
        for c in range(cols):
            if c in (2, 3, 4):
                if f == 0 or f > n:
                    e.hueco(f, c)                         # la quebrada
                else:
                    e.piso(f, c, TABLA)                   # las tablas del puente
                    if f == 1:
                        e.muro(f, c, "N", bajo=True)      # las barandas
                    if f == n:
                        e.muro(f, c, "S", bajo=True)
            else:
                e.piso(f, c, MONTE if c < 2 else CASA)
    for i, p in enumerate(gente):
        e.rotulo(i + 1, 0, "%s %d" % (p, caso["minutos"][p]))
        e.meta(i + 1, 5)
    e.mueble((n + 1) // 2, 6, "casa", "#c9a46a")          # provisional: la casa con la luz prendida
    viajes = estado["viajes"]
    alla, linterna_alla = reparto(caso, viajes)
    col = {p: (5 if p in alla else 1) for p in gente}
    # la linterna: alumbra la cabecera del puente al lado de los que la tienen
    lado = 5 if linterna_alla else 1
    for i, p in enumerate(gente):
        if col[p] == lado:
            e.luz(i + 1, 4 if linterna_alla else 2, AMARILLO)
    # lo que esta mirando la generacion 3 sin mandarlo
    for p in estado.get("foco", ()):
        e.runa(gente.index(p) + 1, col[p], "#ff9f1c")
    # lo que salio mal en el monte, en cualquier momento de estos viajes
    repartos = [reparto(caso, viajes[:k + 1]) for k in range(len(viajes))]
    malos = set()
    lineas = []
    for regla in reglas(caso):
        mal = any(rompe(caso, regla, a, l) for (a, l) in repartos)
        if mal:
            malos.update(regla[1:])
        lineas.append((texto_regla(caso, regla), "mal" if mal else "", False))
    for i, p in enumerate(gente):
        if p == "Pixie":
            e.conejo(i + 1, col[p])
        else:
            e.personaje(p, i + 1, col[p], COLOR[i % len(COLOR)], p[0])
        if p in malos:
            e.equis(i + 1, col[p])
    queda = bateria(caso, estado)
    e.medidor("linterna", max(0, queda), caso["linterna"])
    if "cota" in estado:
        lineas.append(("Falta, en el mejor caso: %d min" % estado["cota"], "mal" if estado["cota"] > queda else "bien", True))
    e.panel("A oscuras, en el monte", lineas)
    frase = respuesta(caso, estado)
    if frase:
        e.veredicto(frase)
    return e
