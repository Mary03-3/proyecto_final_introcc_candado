# generar_casos_mula.py  ---  como se fabricaron y verificaron los niveles de la mula cafetera
#
# Uso (desde la raiz del repositorio):
#     python3 herramientas/generar_casos_mula.py            verifica y escribe mundos/mula/casos_mula.py
#     python3 herramientas/generar_casos_mula.py revisar    solo verifica, no escribe
#
# DE DONDE SALEN LOS NUMEROS
#   * La fisica es la receta de la guia L2 (fisica_mula.py del curso), RECONSTRUIDA aqui porque el
#     archivo original no estaba a mano: orbitas circulares y en el mismo plano, radios de la
#     Planetary Fact Sheet de la NASA, y transferencia de Hohmann entre dos orbitas. Sin ventanas
#     de lanzamiento (los planetas siempre bien alineados) y sin contar despegues ni aterrizajes.
#     La reconstruccion reproduce los controles de la tarea puente de la guia: 56 parejas,
#     Tierra-Marte 258,9 dias, Tierra-Jupiter 997,8 dias, y la busqueda de la sesion 1 con cinco
#     planetas hace 326 llamadas y halla 50,40 km/s. El unico control que no da exacto es el
#     empuje Tierra-Marte: aqui 5,596 km/s, en la guia 5,600. Este programa lo imprime.
#   * Las colonias, sus pedidos y sus pagos son los de la mision de referencia de la guia (sesion 2):
#     la mula carga 45 cargas, tiene 50 km/s y el cafe que llega el dia t paga 1 - t/6000.
#     Esa mision es el nivel 4 tal cual. Los niveles 1 a 3 usan menos colonias y otros topes de
#     carga y combustible, elegidos para que el optimo sea unico y la tabla cuente la historia.
#
# QUE SE VERIFICA
#   Para cada nivel se recorren TODOS los planes posibles (sin podar nada) y se comprueba que el
#   mejor plan es unico: el segundo mejor vale al menos 0,5 menos (y se ve distinto en pantalla).
import math
import os
import pprint
import sys

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# ----------------------------------------------------------------- la receta (fisica_mula.py, reconstruida)
MU_SOL = 1.32712440018e11          # km^3/s^2, parametro gravitacional del Sol
RADIO = {                          # radio medio de la orbita, km (NASA, Planetary Fact Sheet, 10^6 km)
    "Mercurio": 57.9e6, "Venus": 108.2e6, "Tierra": 149.6e6, "Marte": 228.0e6,
    "Júpiter": 778.5e6, "Saturno": 1432.0e6, "Urano": 2867.0e6, "Neptuno": 4515.0e6,
}
PLANETAS = ["Mercurio", "Venus", "Tierra", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"]


def dias_viaje(a, b):
    """Dias que tarda la mula de la orbita de a a la de b: media vuelta de la elipse de Hohmann."""
    semieje = (RADIO[a] + RADIO[b]) / 2
    return math.pi * math.sqrt(semieje ** 3 / MU_SOL) / 86400


def empuje(a, b):
    """Combustible del viaje de a a b, en km/s de cambio de velocidad: el encendido de salida mas el de llegada."""
    r1, r2 = RADIO[a], RADIO[b]
    semieje = (r1 + r2) / 2
    salida = math.sqrt(MU_SOL * (2 / r1 - 1 / semieje)) - math.sqrt(MU_SOL / r1)
    llegada = math.sqrt(MU_SOL / r2) - math.sqrt(MU_SOL * (2 / r2 - 1 / semieje))
    return abs(salida) + abs(llegada)


def tabla_costos():
    """La tabla congelada, como costos_mula.csv: (origen, destino) -> (dias, km/s), redondeada."""
    tabla = {}
    for a in PLANETAS:
        for b in PLANETAS:
            if a != b:
                tabla[(a, b)] = (round(dias_viaje(a, b), 1), round(empuje(a, b), 3))
    return tabla


def controles(tabla):
    """Los controles de la tarea puente de la guia L2."""
    llamadas = [0]

    def mejor_ruta(actual, pendientes):
        llamadas[0] += 1
        if not pendientes:
            return 0, []
        mejor = (float("inf"), [])
        for p in pendientes:
            c, r = mejor_ruta(p, [q for q in pendientes if q != p])
            c = c + empuje(actual, p)
            if c < mejor[0]:
                mejor = (c, [p] + r)
        return mejor

    km, ruta = mejor_ruta("Tierra", ["Mercurio", "Venus", "Marte", "Júpiter", "Saturno"])
    print("Controles de la guía L2 (tarea puente):")
    print("  filas de la tabla:        %d   (guía: 56)" % len(tabla))
    print("  Tierra-Marte:             %.1f días, %.3f km/s   (guía: 258,9 días y 5,600 km/s)" % tabla[("Tierra", "Marte")])
    print("  Tierra-Júpiter:           %.1f días   (guía: 997,8)" % tabla[("Tierra", "Júpiter")][0])
    print("  búsqueda con 5 planetas:  %d llamadas, %.2f km/s %s   (guía: 326 y 50,40)" % (llamadas[0], km, ruta))


# ----------------------------------------------------------------- la mision de referencia (guia L2, sesion 2)
PEDIDO = {   # colonia: (cargas pedidas, paga por carga en multiplos del precio interno de referencia)
    "Mercurio": (6, 3.0), "Venus": (8, 1.5), "Marte": (12, 1.0), "Júpiter": (10, 2.0),
    "Saturno": (8, 2.5), "Urano": (6, 4.0), "Neptuno": (5, 5.0),
}
VIDA = 6000      # a los 6000 dias el cafe ya no vale nada

# los niveles: (colonias, carga maxima, combustible en km/s)
NIVELES = {
    1: (["Mercurio", "Venus", "Marte"], 30, 30),
    2: (["Mercurio", "Venus", "Marte", "Júpiter"], 26, 45),
    3: (["Mercurio", "Venus", "Marte", "Júpiter", "Saturno", "Urano"], 40, 35),
    4: (["Mercurio", "Venus", "Marte", "Júpiter", "Saturno", "Urano", "Neptuno"], 45, 50),
}


def armar(nivel, tabla):
    colonias, carga, combustible = NIVELES[nivel]
    lugares = ["Tierra"] + colonias
    costos = []
    for a in lugares:
        for b in colonias:
            if a != b:
                d, k = tabla[(a, b)]
                costos.append((a, b, d, k))
    return {"titulo": "La mula cafetera · nivel %d" % nivel,
            "colonias": [(c, PEDIDO[c][0], PEDIDO[c][1]) for c in colonias],
            "carga": carga, "combustible": combustible, "vida": VIDA,
            "costos": costos}


# ----------------------------------------------------------------- verificacion por fuerza bruta (independiente del mundo)
def todos_los_planes(caso):
    """Recorre todos los planes (cada orden de cada subconjunto de colonias) y devuelve los que
    cumplen las tres reglas, con su valor: [(valor, ruta)]."""
    pedido = {c: (n, p) for (c, n, p) in caso["colonias"]}
    costo = {(a, b): (d, k) for (a, b, d, k) in caso["costos"]}
    buenos = []

    def recorrer(aqui, ruta, dia, gastado, cargas, valor):
        buenos.append((valor, list(ruta)))
        for c in pedido:
            if c in ruta:
                continue
            d, k = costo[(aqui, c)]
            n, p = pedido[c]
            if gastado + k > caso["combustible"] + 1e-9 or cargas + n > caso["carga"] or dia + d >= caso["vida"]:
                continue      # una regla rota no se arregla siguiendo: el combustible, la carga y el dia solo crecen
            recorrer(c, ruta + [c], dia + d, gastado + k, cargas + n, valor + n * p * (1 - (dia + d) / caso["vida"]))

    recorrer("Tierra", [], 0.0, 0.0, 0, 0.0)
    buenos.sort(key=lambda x: -x[0])
    return buenos


def main():
    tabla = tabla_costos()
    controles(tabla)
    casos = {}
    todo_bien = True
    for nivel in sorted(NIVELES):
        caso = armar(nivel, tabla)
        planes = todos_los_planes(caso)
        mejor, segundo = planes[0], planes[1]
        unico = mejor[0] - segundo[0] >= 0.5
        todo_bien = todo_bien and unico
        print("Nivel %d: %d colonias, carga %d, combustible %d km/s -> %d planes válidos" % (
            nivel, len(caso["colonias"]), caso["carga"], caso["combustible"], len(planes)))
        print("   óptimo  %.2f  Tierra → %s" % (mejor[0], " → ".join(mejor[1])))
        print("   segundo %.2f  Tierra → %s" % (segundo[0], " → ".join(segundo[1])))
        print("   ¿óptimo único? %s" % ("sí" if unico else "NO"))
        casos[nivel] = caso
    if not todo_bien:
        print("Hay un nivel sin óptimo único: no se escribe nada.")
        sys.exit(1)
    if len(sys.argv) > 1 and sys.argv[1] == "revisar":
        return
    destino = os.path.join(RAIZ, "mundos", "mula", "casos_mula.py")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("# casos_mula.py  ---  los niveles de la mula cafetera (datos, no programa)\n")
        f.write("# Escrito por herramientas/generar_casos_mula.py; no se edita a mano.\n")
        f.write("# 'colonias': (nombre, cargas pedidas, paga por carga en precios de referencia).\n")
        f.write("# 'carga': cuantas cargas lleva la mula. 'combustible': km/s de cambio de velocidad.\n")
        f.write("# 'vida': a los tantos dias el cafe ya no vale nada (paga 1 - dia/vida).\n")
        f.write("# 'costos': (origen, destino, dias de viaje, km/s), transferencias de Hohmann.\n")
        f.write("# En cada nivel hay una sola ruta que entrega el mayor valor.\n")
        f.write("CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")
    print("Escrito", os.path.normpath(destino))


if __name__ == "__main__":
    main()
