# generar_casos_candado.py  ---  fabrica los niveles del candado (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_candado.py           fabrica, verifica y escribe
#       python3 herramientas/generar_casos_candado.py revisar   solo verifica el archivo que ya existe
#
# Para cada nivel se elige al azar una clave sin digitos repetidos y se van
# agregando intentos (tambien sin repetidos), con sus luces, hasta que una sola
# clave las cumple todas. Se exige que haya un intento apagado (para la regla 1
# de la generacion 3) y uno sin verdes (para la regla 2). De muchos candidatos se
# queda con el que mas distancia pone entre las generaciones 2 y 3, con pocos intentos.
# Al final se recarga el archivo escrito y se cuenta, recorriendo TODAS las claves
# posibles con mundo.viola, que cada nivel tenga exactamente una solucion.
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "..")
sys.path.insert(0, os.path.join(RAIZ, "Recursos"))
sys.path.insert(0, os.path.join(RAIZ, "mundos", "candado"))
sys.path.insert(0, os.path.join(RAIZ, "ejemplo_hacienda"))
sys.path.insert(0, os.path.join(RAIZ, "referencia", "candado"))
ARCHIVO = os.path.join(RAIZ, "mundos", "candado", "casos_candado.py")

NIVELES = {   # nivel: (ruedas, digitos, maximo de intentos, candidatos a probar, semilla)
    1: (3, 6, 4, 300, 11),
    2: (3, 10, 5, 300, 22),
    3: (4, 10, 6, 300, 33),
    4: (5, 10, 7, 150, 44),
}


def luces(intento, clave):
    en_sitio = sum(1 for i in range(len(clave)) if intento[i] == clave[i])
    return en_sitio, len(set(intento) & set(clave)) - en_sitio


def todas(n, k):
    """Todas las claves sin digitos repetidos."""
    salida = [()]
    for _ in range(n):
        salida = [c + (d,) for c in salida for d in range(k) if d not in c]
    return salida


def fabricar(n, k, maximo, azar):
    """Una clave y una lista de intentos con solucion unica, o None si no sale."""
    universo = todas(n, k)
    clave = tuple(azar.sample(range(k), n))
    intentos = []
    # un intento apagado: digitos que no estan en la clave
    fuera = [d for d in range(k) if d not in clave]
    apagado = tuple(azar.sample(fuera, n))
    # uno sin verdes y con alguna amarilla
    while True:
        sin_verdes = tuple(azar.sample(range(k), n))
        v, a = luces(sin_verdes, clave)
        if v == 0 and a >= 1:
            break
    for t in (apagado, sin_verdes):
        intentos.append((t, ) + luces(t, clave))
    quedan = [c for c in universo if all(luces(t, c) == (v, a) for (t, v, a) in intentos)]
    while len(quedan) > 1 and len(intentos) < maximo:
        # se prueban unos cuantos intentos al azar y se queda el que mas descarta
        mejor = None
        for _ in range(40):
            t = tuple(azar.sample(range(k), n))
            if t == clave:
                continue
            v, a = luces(t, clave)
            resto = [c for c in quedan if luces(t, c) == (v, a)]
            if mejor is None or len(resto) < len(mejor[1]):
                mejor = ((t, v, a), resto)
        intentos.append(mejor[0])
        quedan = mejor[1]
    if len(quedan) != 1:
        return None
    azar.shuffle(intentos)
    return clave, intentos


def medir(caso):
    """Pasos y tropiezos de las generaciones 2 y 3 (la 1 se mide en correr.py tabla)."""
    import mundo
    import g2_con_hilo
    import g3_cerrajero
    from bitacora import Bitacora
    salida = []
    for g in (g2_con_hilo, g3_cerrajero):
        bit = Bitacora("medir", grabar=False)
        s = g.resolver(mundo, caso, bit)
        salida.append((s, bit.cuenta))
    return salida


def caso_de(nivel, clave, intentos):
    n, k = NIVELES[nivel][0], NIVELES[nivel][1]
    return {"titulo": "El candado · nivel %d" % nivel, "ruedas": n, "digitos": k,
            "intentos": [[list(t), v, a] for (t, v, a) in intentos], "clave": list(clave)}


def fabricar_todo():
    import casos_candado
    import mundo
    casos = {}
    for nivel in sorted(NIVELES):
        n, k, maximo, cuantos, semilla = NIVELES[nivel]
        azar = random.Random(semilla)
        mejor = None
        for _ in range(cuantos):
            hecho = fabricar(n, k, maximo, azar)
            if hecho is None:
                continue
            caso = caso_de(nivel, *hecho)
            casos_candado.CASOS[99] = caso
            (s2, c2), (s3, c3) = medir(mundo.cargar(99))
            if s2 != 1 or s3 != 1:
                raise RuntimeError("Una generacion no hallo la solucion unica: %r" % caso)
            # puntaje: G2 debe tropezar mucho y G3 poco; se prefieren los que usan la regla 4
            puntaje = (c2["rechazar"] - 3 * c3["rechazar"]) + 15 * c3["deducir"] - 4 * len(hecho[1])
            if mejor is None or puntaje > mejor[0]:
                mejor = (puntaje, caso, c2, c3)
        del casos_candado.CASOS[99]
        _, caso, c2, c3 = mejor
        casos[nivel] = caso
        print("nivel %d: clave %s, %d intentos | G2 pasos %d tropiezos %d | G3 pasos %d tropiezos %d deduce %d poda %d"
              % (nivel, caso["clave"], len(caso["intentos"]), c2["avanzar"], c2["rechazar"],
                 c3["avanzar"], c3["rechazar"], c3["deducir"], c3["podar"]))
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write("# casos_candado.py  ---  los niveles del candado (datos, no programa)\n")
        f.write("# Cada caso tiene una sola solucion. Lo fabrico herramientas/generar_casos_candado.py.\n")
        f.write("# Cada intento es [digitos, luces verdes, luces amarillas]: verde es un digito en su\n")
        f.write("# sitio; amarilla, un digito que esta en la clave pero en otra rueda.\n")
        f.write("CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")


def revisar():
    """Recorre TODAS las claves posibles (con repetidos incluidos) y cuenta cuantas no violan nada."""
    import importlib
    import casos_candado
    import mundo
    importlib.reload(casos_candado)
    importlib.reload(mundo)
    bien = True
    for nivel in mundo.casos():
        caso = mundo.cargar(nivel)
        n, k = caso["ruedas"], caso["digitos"]
        claves = [[]]
        for _ in range(n):
            claves = [c + [d] for c in claves for d in range(k)]
        soluciones = [c for c in claves if mundo.viola(caso, {"clave": c}) == ""]
        ok = len(soluciones) == 1 and soluciones[0] == caso["clave"]
        bien = bien and ok
        print("nivel %d: %d claves revisadas, %d solucion(es) %s  %s"
              % (nivel, len(claves), len(soluciones), soluciones, "bien" if ok else "MAL"))
    return bien


if __name__ == "__main__":
    if not (len(sys.argv) > 1 and sys.argv[1] == "revisar"):
        fabricar_todo()
    sys.exit(0 if revisar() else 1)
