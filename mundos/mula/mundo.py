# mundo.py  ---  La mula cafetera
#
# LA FICCION. Una mula sale de la Tierra cargada de cafe colombiano para venderlo
# en las colonias de otros planetas. Pixie la arrea. Cada colonia pide cierto
# numero de cargas y paga cierto multiplo del precio de referencia por carga.
# La mula lleva un numero limitado de cargas y de combustible, y el cafe pierde
# valor con cada dia de viaje: lo que llega el dia t paga 1 - t/6000 de su precio.
# La pregunta: ¿que ruta entrega mas cafe? (la que mas vale al final)
#
# La fisica viene de la receta de la guia L2 (transferencias de Hohmann entre
# orbitas circulares); los dias y el combustible de cada viaje ya estan en el caso.
#
# Cumple el mismo contrato que los demas mundos (ver CONTRATO.md).
# Un ESTADO es un diccionario:
#   {"ruta": ["Venus", "Marte"], "fin": False}   las colonias visitadas, en orden (sale de la Tierra);
#                                                "fin" es True cuando la mula decidio no seguir
# Una DECISION es el nombre de la proxima colonia, o "fin" (detenerse y cerrar la ruta).
# El agente puede agregar, para que se vea en la escena:
#   "tachadas": ["Marte"]         colonias que dedujo que ya no caben en esta ruta
#   "mejor": 38.87                el valor de la mejor ruta que lleva hallada
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "Recursos"))
from escena import Escena                 # noqa: E402

from casos_mula import CASOS              # noqa: E402

FIN = "fin"
TIERRA = "Tierra"
ORDEN_SOLAR = ["Mercurio", "Venus", "Tierra", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"]
COLOR_PLANETA = {"Mercurio": "#9a8f86", "Venus": "#d9b26f", "Tierra": "#3d7cc9", "Marte": "#c1502e",
                 "Júpiter": "#c99a6b", "Saturno": "#e0c67a", "Urano": "#7fd1d8", "Neptuno": "#4a6fe3"}
PARED = "#2a2a30"           # grafito: la noche del espacio
PISO = "#2a2f45"


# ----------------------------------------------------------------- niveles
def casos():
    return sorted(CASOS)


def cargar(nivel):
    if nivel not in CASOS:
        raise ValueError("No existe el nivel %r. Niveles: %s" % (nivel, casos()))
    caso = dict(CASOS[nivel])
    caso["nivel"] = nivel
    caso["orden"] = [c for (c, _, _) in caso["colonias"]]
    caso["pedido"] = {c: (n, p) for (c, n, p) in caso["colonias"]}
    caso["costo"] = {(a, b): (d, k) for (a, b, d, k) in caso["costos"]}
    return caso


# ----------------------------------------------------------------- lo que se puede preguntar del viaje
def dias(caso, a, b):
    """Dias de viaje de la orbita de a a la de b."""
    return caso["costo"][(a, b)][0]


def empuje(caso, a, b):
    """Combustible del viaje de a a b, en km/s."""
    return caso["costo"][(a, b)][1]


def cargas(caso, colonia):
    """Cuantas cargas pide la colonia."""
    return caso["pedido"][colonia][0]


def paga(caso, colonia):
    """Cuanto paga la colonia por carga, en precios de referencia, si el cafe llega el dia 0."""
    return caso["pedido"][colonia][1]


def donde(caso, estado):
    """El planeta donde esta la mula."""
    return estado["ruta"][-1] if estado["ruta"] else TIERRA


def recorrido(caso, estado):
    """Lo que lleva la ruta: (dia de la ultima llegada, km/s gastados, cargas entregadas, valor entregado)."""
    aqui, dia, gastado, entregadas, valor = TIERRA, 0.0, 0.0, 0, 0.0
    for c in estado["ruta"]:
        dia = dia + dias(caso, aqui, c)
        gastado = gastado + empuje(caso, aqui, c)
        entregadas = entregadas + cargas(caso, c)
        valor = valor + cargas(caso, c) * paga(caso, c) * max(0.0, 1 - dia / caso["vida"])
        aqui = c
    return dia, gastado, entregadas, valor


def dia(caso, estado):
    return recorrido(caso, estado)[0]


def combustible(caso, estado):
    """Cuantos km/s le quedan a la mula."""
    return caso["combustible"] - recorrido(caso, estado)[1]


def carga_libre(caso, estado):
    """Cuantas cargas le quedan a la mula por entregar."""
    return caso["carga"] - recorrido(caso, estado)[2]


def valor(caso, estado):
    """El valor entregado hasta ahora, en precios de referencia de una carga."""
    return recorrido(caso, estado)[3]


def pago_al_llegar(caso, estado, colonia):
    """Lo que pagaria la colonia si la mula fuera alla directo desde donde esta."""
    llega = dia(caso, estado) + dias(caso, donde(caso, estado), colonia)
    return cargas(caso, colonia) * paga(caso, colonia) * max(0.0, 1 - llega / caso["vida"])


# ----------------------------------------------------------------- el contrato
def inicio(caso):
    return {"ruta": [], "fin": False}


def opciones(caso, estado):
    """Las decisiones posibles: ir a una colonia que no se ha visitado, o detenerse. No mira nada mas."""
    if estado["fin"]:
        return []
    faltan = [c for c in caso["orden"] if c not in estado["ruta"]]
    if not faltan:
        return []
    return faltan + [FIN]


def completo(caso, estado):
    return len(opciones(caso, estado)) == 0


def aplicar(caso, estado, decision):
    if decision == FIN:
        return {"ruta": list(estado["ruta"]), "fin": True}
    return {"ruta": estado["ruta"] + [decision], "fin": False}


def viola(caso, estado):
    aqui, dia_, gastado, entregadas = TIERRA, 0.0, 0.0, 0
    for c in estado["ruta"]:
        dia_ = dia_ + dias(caso, aqui, c)
        gastado = gastado + empuje(caso, aqui, c)
        entregadas = entregadas + cargas(caso, c)
        if gastado > caso["combustible"] + 1e-9:
            return "se acabó el combustible antes de llegar a %s" % c
        if entregadas > caso["carga"]:
            return "la mula no carga tanto: no alcanza para %s" % c
        if dia_ >= caso["vida"]:
            return "el café llegó a %s sin valor" % c
        aqui = c
    return ""


def decir(caso, decision):
    if decision == FIN:
        return "se detiene y cierra la ruta"
    return "viaja a %s" % decision


def texto_ruta(caso, estado):
    return " → ".join([TIERRA] + estado["ruta"])


def respuesta(caso, estado):
    if completo(caso, estado) and viola(caso, estado) == "":
        return "La ruta %s vale %s precios de carga" % (texto_ruta(caso, estado), numero(valor(caso, estado)))
    return ""


def numero(x, decimales=2):
    return ("%.*f" % (decimales, x)).replace(".", ",")


def pistas(caso):
    lineas = ["La mula lleva %d cargas y %s km/s de combustible." % (caso["carga"], numero(caso["combustible"], 0)),
              "El café que llega el día t paga 1 − t/%d de su precio." % caso["vida"]]
    for (c, n, p) in caso["colonias"]:
        lineas.append("%s pide %d cargas y paga %s por carga." % (c, n, numero(p, 1)))
    return lineas


# ----------------------------------------------------------------- la escena
def lugares(caso):
    """Los planetas del nivel, en el orden del sistema solar, con su columna y su fila en la escena."""
    presentes = [p for p in ORDEN_SOLAR if p == TIERRA or p in caso["pedido"]]
    return {p: (1 if i % 2 == 0 else 3, i + 1) for (i, p) in enumerate(presentes)}


def trazo(paradas):
    """El hilo entre planetas: de cada uno baja (o sube) al carril del medio, corre por el carril
    y sube (o baja) al siguiente. Asi cada tramo es recto, como lo dibuja el visor."""
    puntos = [paradas[0]]
    for (f2, c2) in paradas[1:]:
        f1, c1 = puntos[-1]
        for punto in ((2, c1), (2, c2), (f2, c2)):
            if punto != puntos[-1]:
                puntos.append(punto)
    return puntos


def dibujar(caso, estado):
    sitio = lugares(caso)
    columnas = len(sitio) + 1
    e = Escena(5, columnas, titulo=caso["titulo"], ambiente="sala", pared=PARED)
    for f in range(5):
        for c in range(columnas):
            e.piso(f, c, PISO)
    e.mueble(2, 0, "sol", "#ffcc33")                    # pieza provisional: el Sol (ver NOTAS.md)
    tachadas = estado.get("tachadas", [])
    for p, (f, c) in sitio.items():
        e.piso(f, c, COLOR_PLANETA[p])
        e.rotulo(2, c, p)
        if p == TIERRA:
            e.salida(f, c)
            continue
        afuera = 0 if f == 1 else 4                      # la casilla del pedido, del lado de afuera
        if p in estado["ruta"]:
            e.caja("Café " + p, afuera, c, "#7b4a2a")    # el bulto entregado
        else:
            e.ficha(afuera, c, str(cargas(caso, p)))
        if p in tachadas:
            e.equis(f, c)
    e.hilo(trazo([sitio[TIERRA]] + [sitio[p] for p in estado["ruta"]]))
    aqui = sitio[donde(caso, estado)]
    if completo(caso, estado) and viola(caso, estado) == "":
        e.meta(aqui[0], aqui[1])
    e.conejo(aqui[0], aqui[1])
    e.medidor("combustible", round(max(0.0, combustible(caso, estado)), 1), caso["combustible"])
    lineas = []
    for (p, n, pago) in caso["colonias"]:
        marca = "bien" if p in estado["ruta"] else ("mal" if p in tachadas else "")
        lineas.append(("%s · %d cargas · paga %s" % (p, n, numero(pago, 1)), marca, p == donde(caso, estado)))
    d, _, entregadas, v = recorrido(caso, estado)
    lineas.append(("Día %d · carga %d de %d" % (round(d), entregadas, caso["carga"]), "", False))
    lineas.append(("Valor entregado: %s" % numero(v), "", False))
    if "mejor" in estado:
        lineas.append(("Mejor ruta hallada: %s" % numero(estado["mejor"]), "", False))
    e.panel("La mula", lineas)
    quien = respuesta(caso, estado)
    if quien:
        e.veredicto(quien)
    return e
