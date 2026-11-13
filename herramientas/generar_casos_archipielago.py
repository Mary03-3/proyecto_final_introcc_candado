# generar_casos_archipielago.py  ---  fabrica los niveles del archipielago (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_archipielago.py            fabrica, verifica y escribe los casos
#       python3 herramientas/generar_casos_archipielago.py verificar  solo verifica los casos ya escritos
#
# Como se fabrica un nivel:
#   1. Se pone una isla al azar y se van tendiendo puentes (de 1 o 2) hacia islas nuevas,
#      sin cruzar puentes ya tendidos. Asi la solucion existe y esta conectada.
#   2. Se agregan, al azar, algunos puentes extra entre islas que se ven.
#   3. El numero de cada isla es la suma de sus puentes. Se borran los puentes y se recortan
#      las filas y columnas del borde que son pura agua: queda el mapa.
#   4. Se cuentan TODAS las soluciones del mapa por fuerza bruta (las 3^P maneras de poner
#      0, 1 o 2 puentes en los P pares), sin usar ningun agente. Se guarda solo si hay una.
# El archivo que escribe queda congelado en el repositorio.
import itertools
import os
import pprint
import random
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
CARPETA = os.path.join(AQUI, "..", "mundos", "archipielago")

# nivel: (filas, columnas, islas, pares que debe tener el mapa (de, a), semilla, mapas candidatos)
TALLAS = {1: (5, 5, 6, (5, 6), 1, 60),
          2: (6, 6, 8, (7, 8), 2, 100),
          3: (7, 7, 10, (10, 11), 5, 400),
          4: (8, 8, 11, (12, 12), 6, 300)}
# Entre los candidatos (mapas con solucion unica, en el orden en que salen de la semilla) se
# escoge el que mejor cuenta la historia: en los niveles 3 y 4, que la generacion 3 tenga que
# probar al menos una vez; y entre esos, el que mas pasos le cuesta a la generacion 2.
# "python3 generar_casos_archipielago.py buscar" repite esa busqueda y
# dice cual candidato gano. Aqui quedo anotado, para fabricar sin repetirla.
ELEGIDO = {1: 51, 2: 66, 3: 44, 4: 58}

DIRS = ((0, 1), (1, 0), (0, -1), (-1, 0))


def sembrar(filas, columnas, n_islas, azar):
    """Pasos 1 a 3. Devuelve el mapa (lista de textos) o None si no se logro."""
    islas = {}                      # (f, c) -> numero
    ocupada = set()                 # agua por donde ya pasa un puente
    puentes = {}                    # frozenset({a, b}) -> 1 o 2
    inicio = (azar.randrange(filas), azar.randrange(columnas))
    islas[inicio] = 0
    intentos = 0
    while len(islas) < n_islas and intentos < 4000:
        intentos += 1
        f, c = azar.choice(sorted(islas))
        df, dc = azar.choice(DIRS)
        largo = azar.randint(2, max(filas, columnas) - 1)
        g, d = f + df * largo, c + dc * largo
        if not (0 <= g < filas and 0 <= d < columnas) or (g, d) in islas or (g, d) in ocupada:
            continue
        camino = [(f + df * k, c + dc * k) for k in range(1, largo)]
        if any(x in islas or x in ocupada for x in camino):
            continue
        if any((g + a, d + b) in islas for (a, b) in DIRS):      # nada de islas pegadas
            continue
        islas[(g, d)] = 0
        ocupada.update(camino)
        puentes[frozenset([(f, c), (g, d)])] = azar.choice((1, 2))
    if len(islas) < n_islas:
        return None
    # paso 2: puentes extra entre islas que se ven, sin cruzar
    for (f, c) in sorted(islas):
        for (df, dc) in ((0, 1), (1, 0)):
            g, d = f + df, c + dc
            camino = []
            while 0 <= g < filas and 0 <= d < columnas and (g, d) not in islas:
                camino.append((g, d))
                g, d = g + df, d + dc
            par = frozenset([(f, c), (g, d)])
            if (g, d) in islas and camino and par not in puentes and azar.random() < 0.3:
                if not any(x in ocupada for x in camino):
                    ocupada.update(camino)
                    puentes[par] = azar.choice((1, 2))
    for par, k in puentes.items():
        for isla in par:
            islas[isla] += k
    if any(n > 8 for n in islas.values()):
        return None
    mapa = []
    for f in range(filas):
        mapa.append("".join(str(islas[(f, c)]) if (f, c) in islas else "." for c in range(columnas)))
    return recortar(mapa)


def recortar(mapa):
    """Quita las filas y columnas del borde que son pura agua: en la escena solo estorban."""
    while all(x == "." for x in mapa[0]):
        mapa = mapa[1:]
    while all(x == "." for x in mapa[-1]):
        mapa = mapa[:-1]
    while all(fila[0] == "." for fila in mapa):
        mapa = [fila[1:] for fila in mapa]
    while all(fila[-1] == "." for fila in mapa):
        mapa = [fila[:-1] for fila in mapa]
    return mapa


def leer(mapa):
    """Islas, pares, agua de cada par: lo mismo que calcula mundo.cargar, escrito aparte."""
    islas = [(f, c, int(mapa[f][c])) for f in range(len(mapa)) for c in range(len(mapa[0])) if mapa[f][c].isdigit()]
    donde = {(f, c): i for i, (f, c, _) in enumerate(islas)}
    pares, agua = [], []
    for i, (f, c, _) in enumerate(islas):
        for (df, dc) in ((0, 1), (1, 0)):
            g, d, celdas = f + df, c + dc, []
            while g < len(mapa) and d < len(mapa[0]) and (g, d) not in donde:
                celdas.append((g, d))
                g, d = g + df, d + dc
            if (g, d) in donde and celdas:
                pares.append((i, donde[(g, d)]))
                agua.append(set(celdas))
    return islas, pares, agua


def contar(mapa, tope=None):
    """Paso 4: cuenta las soluciones probando las 3^P combinaciones, una por una."""
    islas, pares, agua = leer(mapa)
    P = len(pares)
    cruzan = [(p, q) for p in range(P) for q in range(p + 1, P) if agua[p] & agua[q]]
    toca = [[p for p in range(P) if i in pares[p]] for i in range(len(islas))]
    soluciones = []
    for k in itertools.product((0, 1, 2), repeat=P):
        if any(sum(k[p] for p in toca[i]) != islas[i][2] for i in range(len(islas))):
            continue
        if any(k[p] and k[q] for (p, q) in cruzan):
            continue
        # conectadas: recorrer desde la isla 0
        vistas, pila = {0}, [0]
        while pila:
            i = pila.pop()
            for p in toca[i]:
                if k[p]:
                    otra = pares[p][0] if pares[p][1] == i else pares[p][1]
                    if otra not in vistas:
                        vistas.add(otra)
                        pila.append(otra)
        if len(vistas) == len(islas):
            soluciones.append(k)
            if tope and len(soluciones) >= tope:
                break
    return soluciones


def contar_rapido(mapa, tope=2):
    """Un filtro rapido para descartar mapas: cuenta soluciones con retroceso, hasta tope.
    El mapa que pase este filtro se confirma despues con contar(), la fuerza bruta."""
    islas, pares, agua = leer(mapa)
    P = len(pares)
    cruza = [[q for q in range(P) if q != p and agua[p] & agua[q]] for p in range(P)]
    ultimo = {}                                   # isla -> el ultimo par que la toca
    for p, (i, j) in enumerate(pares):
        ultimo[i] = p
        ultimo[j] = p
    tiene = [0] * len(islas)
    k = [0] * P
    cuenta = [0]

    def conectada():
        vistas, pila = {0}, [0]
        while pila:
            i = pila.pop()
            for p, (a, b) in enumerate(pares):
                if k[p] and i in (a, b):
                    otra = b if a == i else a
                    if otra not in vistas:
                        vistas.add(otra)
                        pila.append(otra)
        return len(vistas) == len(islas)

    def ir(p):
        if cuenta[0] >= tope:
            return
        if p == P:
            if conectada():
                cuenta[0] += 1
            return
        i, j = pares[p]
        for v in (0, 1, 2):
            if v and any(k[q] for q in cruza[p] if q < p):
                break
            if tiene[i] + v > islas[i][2] or tiene[j] + v > islas[j][2]:
                break
            tiene[i] += v
            tiene[j] += v
            k[p] = v
            if not ((ultimo[i] == p and tiene[i] != islas[i][2]) or (ultimo[j] == p and tiene[j] != islas[j][2])):
                ir(p + 1)
            tiene[i] -= v
            tiene[j] -= v
            k[p] = 0

    if any(not any(i in par for par in pares) for i in range(len(islas))):
        return 0
    ir(0)
    return cuenta[0]


def candidatos(nivel):
    """Los mapas con solucion unica, en el orden en que salen de la semilla del nivel."""
    filas, columnas, n_islas, n_pares, semilla, _ = TALLAS[nivel]
    azar = random.Random(semilla)
    while True:
        mapa = sembrar(filas, columnas, n_islas, azar)
        if mapa is None:
            continue
        _, pares, _ = leer(mapa)
        if n_pares[0] <= len(pares) <= n_pares[1] and contar_rapido(mapa) == 1:
            yield mapa


def puntaje(nivel, mapa):
    """Cuanto le cuesta el mapa a las generaciones 2 y 3 (las de referencia)."""
    raiz = os.path.join(AQUI, "..")
    for sub in ("Recursos", "mundos/archipielago", "ejemplo_hacienda", "referencia/archipielago"):
        if os.path.join(raiz, sub) not in sys.path:
            sys.path.insert(0, os.path.join(raiz, sub))
    import casos_archipielago
    import mundo
    import g2_con_hilo
    import g3_archipielago
    from bitacora import Bitacora
    casos_archipielago.CASOS[0] = {"titulo": "prueba", "mapa": mapa, "solucion": []}
    caso = mundo.cargar(0)
    b2, b3 = Bitacora("g2", grabar=False), Bitacora("g3", grabar=False)
    g2_con_hilo.resolver(mundo, caso, b2)
    g3_archipielago.resolver(mundo, caso, b3)
    prueba = b3.cuenta["avanzar"] > 0 or nivel < 3
    return (prueba, b2.cuenta["avanzar"]), b2.cuenta["avanzar"], b3.cuenta["avanzar"]


def buscar(nivel):
    mejor = None
    for k, mapa in enumerate(candidatos(nivel)):
        if k >= TALLAS[nivel][5]:
            break
        p, g2, g3 = puntaje(nivel, mapa)
        if mejor is None or p > mejor[0]:
            mejor = (p, k, g2, g3, mapa)
    print("nivel %d: gana el candidato %d (generacion 2: %d pasos; generacion 3: %d pruebas)" % ((nivel,) + mejor[1:4]))
    return mejor[1]


def fabricar(nivel):
    k = ELEGIDO[nivel]
    if k is None:
        k = buscar(nivel)
    for j, mapa in enumerate(candidatos(nivel)):
        if j == k:
            sols = contar(mapa)                 # la confirmacion, por fuerza bruta
            assert len(sols) == 1, "el candidato %d del nivel %d no tiene solucion unica" % (k, nivel)
            return mapa, sols[0], k


def escribir(casos):
    with open(os.path.join(CARPETA, "casos_archipielago.py"), "w", encoding="utf-8") as f:
        f.write("# casos_archipielago.py  ---  los niveles del archipielago (datos, no programa)\n"
                "# '.' es agua; un digito es una isla y dice cuantos puentes salen de ella.\n"
                "# Cada mapa tiene una sola manera de tender los puentes. Lo fabrico\n"
                "# herramientas/generar_casos_archipielago.py, que tambien lo verifica.\n"
                "CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")


def verificar():
    datos = {}                                   # se lee el archivo tal como quedo escrito
    with open(os.path.join(CARPETA, "casos_archipielago.py"), encoding="utf-8") as f:
        exec(f.read(), datos)
    CASOS = datos["CASOS"]
    bien = True
    for nivel in sorted(CASOS):
        mapa = CASOS[nivel]["mapa"]
        islas, pares, _ = leer(mapa)
        sols = contar(mapa)
        print("nivel %d | %dx%d | %d islas | %d pares | soluciones: %d"
              % (nivel, len(mapa), len(mapa[0]), len(islas), len(pares), len(sols)))
        if len(sols) != 1 or list(sols[0]) != CASOS[nivel]["solucion"]:
            bien = False
            print("   ¡ese nivel no tiene exactamente la solucion guardada!")
    print("todos los niveles tienen exactamente una solucion" if bien else "HAY NIVELES MALOS")
    return bien


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verificar":
        sys.exit(0 if verificar() else 1)
    if len(sys.argv) > 1 and sys.argv[1] == "buscar":
        for nivel in sorted(TALLAS):
            buscar(nivel)
        sys.exit(0)
    casos = {}
    for nivel in sorted(TALLAS):
        mapa, sol, k = fabricar(nivel)
        casos[nivel] = {"titulo": "El archipiélago · nivel %d" % nivel, "mapa": mapa, "solucion": list(sol)}
        print("nivel %d: candidato %d" % (nivel, k))
        for fila in mapa:
            print("   " + fila)
    escribir(casos)
    print("escrito casos_archipielago.py")
    verificar()
