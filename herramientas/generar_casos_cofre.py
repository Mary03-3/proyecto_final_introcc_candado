# generar_casos_cofre.py  ---  fabrica y verifica los niveles del cofre (lo corre el profesor)
#
# Como se fabrica un nivel:
#   1. La casa se parte por division recursiva: un muro corta un cuarto en dos y deja un paso.
#      El paso es una PUERTA o un hueco abierto; a veces un muro deja dos pasos (eso crea vueltas).
#   2. Pixie entra por una esquina, el cofre va en un cuarto lejano y se riegan llaves al azar.
#   3. Se cuenta con el mismo mundo y con los agentes de verdad (G1, G2 de ejemplo_hacienda y la G3
#      de referencia) y se acepta el nivel solo si:
#        - hay EXACTAMENTE una solucion (un solo orden de puertas que llega al cofre), y las tres
#          generaciones hallan esa misma;
#        - la solucion abre varias puertas y la G1 trabaja claramente mas que la G2 (la G2, mas que la G3).
#   Uso:  python3 generar_casos_cofre.py            fabrica los cuatro niveles y escribe casos_cofre.py
#         python3 generar_casos_cofre.py verificar  solo vuelve a contar los niveles ya escritos
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, os.path.join(RAIZ, "mundos", "cofre"))
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))
sys.path.insert(0, os.path.join(RAIZ, "referencia", "cofre"))

import mundo                      # noqa: E402
from bitacora import Bitacora     # noqa: E402
import g1_a_ciegas                # noqa: E402
import g2_con_hilo                # noqa: E402
import g3_cerrajero               # noqa: E402


def dividir(g, r0, r1, c0, c1, rnd, plan):
    """Division recursiva. Los cuartos ocupan filas y columnas impares; los muros, las pares."""
    alto = (r1 - r0) // 2 + 1
    ancho = (c1 - c0) // 2 + 1
    if alto == 1 and ancho == 1:
        return
    if alto * ancho <= plan["cuarto"] and rnd.random() < plan["parar"]:
        return
    horizontal = alto > ancho or (alto == ancho and rnd.random() < 0.5)
    if alto == 1:
        horizontal = False
    if ancho == 1:
        horizontal = True
    if horizontal:
        w = rnd.randrange(r0 + 1, r1, 2)
        for c in range(c0, c1 + 1):
            g[w][c] = "#"
        pasos = rnd.sample(range(c0, c1 + 1, 2), min(ancho, 2 if rnd.random() < plan["doble"] else 1))
        for c in pasos:
            g[w][c] = "o"
        dividir(g, r0, w - 1, c0, c1, rnd, plan)
        dividir(g, w + 1, r1, c0, c1, rnd, plan)
    else:
        w = rnd.randrange(c0 + 1, c1, 2)
        for f in range(r0, r1 + 1):
            g[f][w] = "#"
        pasos = rnd.sample(range(r0, r1 + 1, 2), min(alto, 2 if rnd.random() < plan["doble"] else 1))
        for f in pasos:
            g[f][w] = "o"
        dividir(g, r0, r1, c0, w - 1, rnd, plan)
        dividir(g, r0, r1, w + 1, c1, rnd, plan)


def contar(caso, tope_g1):
    """Corre las tres generaciones (la G1 al final, porque es la mas cara). Devuelve un diccionario
    nombre -> (soluciones, pasos, tropiezos, deducciones, podas); si alguna no tiene una sola
    solucion, o la G1 pasa del tope, se detiene antes y devuelve None."""
    r = {}
    for (nombre, agente, tope) in (("g2", g2_con_hilo, None), ("g3", g3_cerrajero, None), ("g1", g1_a_ciegas, tope_g1)):
        bit = Bitacora(nombre, grabar=False)
        bit.tope = tope
        try:
            s = agente.resolver(mundo, caso, bit)
        except StopIteration:
            return None
        r[nombre] = (s, bit.cuenta["avanzar"], bit.cuenta["rechazar"], bit.cuenta["deducir"], bit.cuenta["podar"])
        if s != 1:
            return None
    return r


def intento(n, plan, rnd):
    g = [["#"] * n for _ in range(n)]
    for f in range(1, n - 1):
        for c in range(1, n - 1):
            g[f][c] = "."
    dividir(g, 1, n - 2, 1, n - 2, rnd, plan)
    pasos = [(f, c) for f in range(n) for c in range(n) if g[f][c] == "o"]
    if len(pasos) < plan["puertas"][0] or len(pasos) > 26:
        return None
    for (f, c) in pasos:
        g[f][c] = "."
    for (f, c) in rnd.sample(pasos, min(len(pasos), plan["puertas"][1])):
        g[f][c] = "P"
    entrada = (n - 2, 1)
    cofre = (1, n - 2)
    g[entrada[0]][entrada[1]] = "E"
    g[cofre[0]][cofre[1]] = "C"
    return regar_llaves(g, plan, rnd)


def regar_llaves(g, plan, rnd):
    """Simula un recorrido: elige al azar la puerta buena entre las que estan a mano y pone las
    llaves en los cuartos que esa puerta destapa. Las demas puertas quedan sin llave detras."""
    mundo.CASOS[0] = {"titulo": "prueba", "mapa": ["".join(fila) for fila in g]}
    caso = mundo.cargar(0)
    meta = caso["cuarto"][caso["cofre"]]
    estado = mundo.inicio(caso)
    mano = 0
    nuevos = [caso["cuarto"][caso["entrada"]]]
    usadas = set([caso["entrada"], caso["cofre"]])
    while True:
        alcanza = mundo.alcanzables(caso, estado)
        if meta in alcanza:
            break
        if mano == 0:
            poner = 2 if rnd.random() < plan["dobles"] else 1
        else:
            poner = 0 if rnd.random() < 0.5 else 1
        celdas = [x for x in caso["cuarto"] if caso["cuarto"][x] in nuevos and x not in usadas and g[x[0]][x[1]] == "."]
        if len(celdas) < poner:
            return None
        for x in rnd.sample(celdas, poner):
            g[x[0]][x[1]] = "L"
            usadas.add(x)
        mano = mano + poner - 1
        candidatas = mundo.cerradas_a_mano(caso, estado)
        if mano >= 1:                           # con llave de sobra, la puerta buena es una recien destapada:
            recientes = [p for p in candidatas if any(z in nuevos for z in caso["lados"][p])]
            if not recientes:                   # asi no se pueden abrir en otro orden
                return None
            candidatas = recientes
        lejos = [p for p in candidatas if meta not in mundo.alcanzables(caso, mundo.aplicar(caso, estado, p))]
        if mano >= 1 and not lejos:
            return None                         # sobraria una llave al llegar al cofre
        if lejos and (mano >= 1 or rnd.random() < plan["rodeo"]):
            candidatas = lejos                  # no destapa el cofre todavia: el recorrido se alarga
        buena = rnd.choice(candidatas)
        estado = mundo.aplicar(caso, estado, buena)
        nuevos = [z for z in mundo.alcanzables(caso, estado) if z not in alcanza]
    if mano != 0:
        return None
    return ["".join(fila) for fila in g]


def aceptable(r, plan):
    if r is None:
        return False
    s1, s2, s3 = r["g1"][0], r["g2"][0], r["g3"][0]
    if not (s1 == s2 == s3 == 1):
        return False
    g1, g2, g3 = r["g1"][1], r["g2"][1], r["g3"][1]
    return (g1 >= plan["g1_min"] and g1 >= plan["veces"] * g2 and r["g2"][2] >= 3 * max(1, r["g3"][2])
            and g2 >= plan["g2_min"] and g3 < g2)


def fabricar(nivel, n, plan, semilla):
    rnd = random.Random(semilla)
    for vuelta in range(1, 50001):
        mapa = intento(n, plan, rnd)
        if mapa is None:
            continue
        mundo.CASOS[0] = {"titulo": "prueba", "mapa": mapa}
        caso = mundo.cargar(0)
        r = contar(caso, plan["tope"])
        if not aceptable(r, plan):
            continue
        sol = solucion(caso)
        if len(sol["abiertas"]) < plan["minimo"]:
            continue
        del mundo.CASOS[0]
        print("nivel %d (vuelta %d): %s" % (nivel, vuelta, r))
        return mapa
    raise RuntimeError("No se hallo un nivel %d con ese plan." % nivel)


def solucion(caso):
    """La unica solucion, buscada con la G2 (orden de puertas)."""
    hallada = []

    class Bit:
        tope = None

        def registrar(self, tipo, estado=None, nota=""):
            if tipo == "solucion":
                hallada.append(estado)
    g2_con_hilo.resolver(mundo, caso, Bit())
    return hallada[0]


PLANES = {   # nivel: (lado de la casa, plan, semilla)
    # cuarto/parar: cuando dejar de partir cuartos; doble: probabilidad de que un muro deje dos pasos;
    # dobles: probabilidad de dejar dos llaves juntas; rodeo: preferencia por no destapar el cofre pronto;
    # puertas: minimo de puertas; minimo: puertas que debe abrir la solucion; tope: eventos maximos de la G1;
    # g1_min, g2_min: pasos minimos de G1 y G2; veces: cuantas veces mas pasos da la G1 que la G2.
    1: (9, {"cuarto": 4, "parar": 1.0, "doble": 0.0, "rodeo": 0.5, "dobles": 0.3, "puertas": (5, 26), "minimo": 3,
            "tope": 20000, "g1_min": 40, "g2_min": 6, "veces": 3}, 11),
    2: (11, {"cuarto": 4, "parar": 1.0, "doble": 0.0, "rodeo": 0.5, "dobles": 0.4, "puertas": (6, 26), "minimo": 4,
             "tope": 300000, "g1_min": 400, "g2_min": 15, "veces": 5}, 22),
    3: (13, {"cuarto": 4, "parar": 1.0, "doble": 0.0, "rodeo": 0.5, "dobles": 0.4, "puertas": (8, 26), "minimo": 5,
             "tope": 1500000, "g1_min": 3000, "g2_min": 40, "veces": 8}, 33),
    4: (15, {"cuarto": 6, "parar": 1.0, "doble": 0.0, "rodeo": 0.5, "dobles": 0.4, "puertas": (10, 26), "minimo": 6,
             "tope": 800000, "g1_min": 8000, "g2_min": 20, "veces": 10}, 44),
}


def verificar():
    for nivel in mundo.casos():
        caso = mundo.cargar(nivel)
        r = contar(caso, None)
        sol = solucion(caso)
        print("nivel %d: soluciones G1 %d, G2 %d, G3 %d | pasos %d / %d / %d | %s"
              % (nivel, r["g1"][0], r["g2"][0], r["g3"][0], r["g1"][1], r["g2"][1], r["g3"][1],
                 mundo.respuesta(caso, sol)))
        if not (r["g1"][0] == r["g2"][0] == r["g3"][0] == 1):
            raise SystemExit("El nivel %d no tiene exactamente una solucion." % nivel)
    print("Los cuatro niveles tienen exactamente una solucion, y las tres generaciones la hallan.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        verificar()
        sys.exit(0)
    quiero = [int(x) for x in sys.argv[1:]] or sorted(PLANES)
    casos = dict(mundo.CASOS)
    for nivel in quiero:
        n, plan, semilla = PLANES[nivel]
        mapa = fabricar(nivel, n, plan, semilla)
        casos[nivel] = {"titulo": "El cofre · nivel %d" % nivel, "mapa": mapa}
        print("\n".join("   " + fila for fila in mapa))
    casos.pop(0, None)
    with open(os.path.join(RAIZ, "mundos", "cofre", "casos_cofre.py"), "w", encoding="utf-8") as f:
        f.write("# casos_cofre.py  ---  los niveles del cofre (datos, no programa)\n"
                "# '#' muro, '.' piso, 'E' entrada, 'C' cofre, 'P' puerta cerrada, 'L' llave.\n"
                "# Las puertas se nombran A, B, C... en orden de lectura (de arriba abajo, de izquierda a derecha).\n"
                "# Los fabrico herramientas/generar_casos_cofre.py: cada nivel tiene un solo orden de puertas\n"
                "# que lleva al cofre sin quedarse sin llaves.\n"
                "CASOS = " + pprint.pformat({k: casos[k] for k in sorted(casos)}, width=60, sort_dicts=False) + "\n")
