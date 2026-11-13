# generar_casos_hacienda.py  ---  fabrica los niveles de la hacienda (lo corre el profesor)
# Uso:  python3 herramientas/generar_casos_hacienda.py
# Cada caso tiene una sola solucion; el archivo que escribe queda congelado en el repositorio.
import os, pprint, random, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "Recursos"))
sys.path.insert(0, os.path.join(AQUI, "..", "mundos", "hacienda"))

PLANOS = {
 1: dict(titulo="El robo en la hacienda · nivel 1",
         plano=[[0,0,1,1],[0,0,1,1],[2,2,2,3],[2,2,3,3]],
         habitaciones=["la sala","la cocina","el patio","la despensa"],
         muebles=[[(0,0),"piano"],[(1,3),"estufa"],[(3,0),"planta"]],
         personas=["Amparo","Benicio","Clemencia"]),
 2: dict(titulo="El robo en la hacienda · nivel 2",
         plano=[[0,0,0,1,1],[0,0,0,1,1],[2,2,3,3,1],[2,2,3,3,4],[2,2,3,4,4]],
         habitaciones=["la sala","la cocina","el patio","el comedor","la despensa"],
         muebles=[[(0,1),"piano"],[(1,4),"estufa"],[(3,0),"fuente"],[(2,2),"mesa"],[(4,3),"barril"]],
         personas=["Amparo","Benicio","Clemencia","Dámaso"]),
 3: dict(titulo="El robo en la hacienda · nivel 3",
         plano=[[0,0,0,1,1,1],[0,0,0,1,1,1],[2,2,3,3,4,4],[2,2,3,3,4,4],[5,5,5,3,4,4],[5,5,5,6,6,6]],
         habitaciones=["la sala","la cocina","la alcoba","el patio","el comedor","el beneficiadero","la despensa"],
         muebles=[[(0,2),"piano"],[(1,5),"estufa"],[(2,0),"cama"],[(3,3),"fuente"],[(2,5),"mesa"],[(5,0),"telar"],[(5,4),"barril"],[(0,4),"planta"]],
         personas=["Amparo","Benicio","Clemencia","Dámaso","Eulalia"]),
 4: dict(titulo="El robo en la hacienda · nivel 4",
         plano=[[0,0,0,1,1,1,1],[0,0,0,1,1,1,1],[2,2,3,3,3,4,4],[2,2,3,3,3,4,4],[2,2,3,3,3,4,4],[5,5,5,5,6,6,6],[5,5,5,5,6,6,6]],
         habitaciones=["la sala","la cocina","la alcoba","el patio","el comedor","el beneficiadero","la despensa"],
         muebles=[[(0,1),"piano"],[(1,6),"estufa"],[(2,0),"cama"],[(3,3),"fuente"],[(4,6),"mesa"],[(6,0),"telar"],[(6,5),"barril"],[(0,4),"planta"],[(5,2),"barril"],[(4,1),"planta"]],
         personas=["Amparo","Benicio","Clemencia","Dámaso","Eulalia","Fermín"]),
}

import mundo
import casos_hacienda
COFRE = "Cofre"

def caso_de(base, pistas):
    casos_hacienda.CASOS[99] = dict(base, pistas=pistas)
    return mundo.cargar(99)

def contar(caso, tope):
    """Cuenta soluciones (hasta tope): primero filtra por las pistas propias, luego retroceso."""
    libres = mundo.casillas_libres(caso)
    cand = {p: [x for x in libres if not mundo.viola(caso, {"lugar": {p: x}})] for p in caso["orden"]}
    orden = sorted(caso["orden"], key=lambda p: len(cand[p]))
    cuenta = [0]
    def bus(i, lugar):
        if cuenta[0] >= tope: return
        if i == len(orden):
            cuenta[0] += 1; return
        for x in cand[orden[i]]:
            lugar[orden[i]] = x
            if not mundo.viola(caso, {"lugar": lugar}):
                bus(i + 1, lugar)
            del lugar[orden[i]]
    bus(0, {}); return cuenta[0]

def fabricar(nivel, semilla):
    base = PLANOS[nivel]; rnd = random.Random(semilla)
    vacio = caso_de(base, [])
    n = vacio["n"]; orden = vacio["orden"]; libres = mundo.casillas_libres(vacio)
    # 1. una solucion al azar: uno por fila y columna, y exactamente uno a solas con el cofre
    while True:
        cols = list(range(n)); rnd.shuffle(cols)
        filas = list(range(n)); rnd.shuffle(filas)
        lugar = {orden[i]: (filas[i], cols[i]) for i in range(n)}
        if any(v not in libres for v in lugar.values()): continue
        if len(mundo.acompanantes(vacio, lugar)) == 1: break
    ladron = mundo.acompanantes(vacio, lugar)[0]
    # 2. todas las pistas verdaderas
    pozo = []
    for p in orden:
        h = mundo.habitacion_de(vacio, lugar[p])
        pozo.append(("en", p, h))
        for otra in vacio["habitaciones"]:
            if otra != h: pozo.append(("no_en", p, otra))
        for m in set(vacio["muebles"].values()):
            if mundo.junto_a_mueble(vacio, lugar[p], m): pozo.append(("junto", p, m)); pozo.append(("junto", p, m)); pozo.append(("junto", p, m))
        for q in orden:
            if q == p: continue
            if mundo.habitacion_de(vacio, lugar[q]) == h:
                if COFRE not in (p, q): pozo.append(("con", p, q)); pozo.append(("con", p, q)); pozo.append(("con", p, q))
            elif COFRE not in (p, q): pozo.append(("sin", p, q)); pozo.append(("sin", p, q))
            if lugar[p][0] < lugar[q][0]: pozo.append(("norte", p, q))
            if lugar[p][1] < lugar[q][1]: pozo.append(("oeste", p, q))
        if p != COFRE and all(mundo.habitacion_de(vacio, lugar[q]) != h for q in orden if q != p):
            pozo.append(("solo", p)); pozo.append(("solo", p))
    pozo.append(("fila", rnd.choice(orden), None)); pozo.append(("columna", rnd.choice(orden), None))
    pozo = [(t, p, lugar[p][0]) if t == "fila" else ((t, p, lugar[p][1]) if t == "columna" else tuple([t, p] + list(r)))
            for (t, p, *r) in pozo]
    rnd.shuffle(pozo)
    # 3. una pista por cada uno, y despues las que hagan falta hasta que la solucion sea unica
    elegidas = []
    for p in orden:
        for pista in pozo:
            if pista[1] == p and pista[0] not in ("en", "fila", "columna") and pista not in elegidas:
                elegidas.append(pista); break
    TOPE = 400
    actual = contar(caso_de(base, elegidas), TOPE)
    for pista in pozo:
        if actual == 1: break
        if pista in elegidas: continue
        nuevo = contar(caso_de(base, elegidas + [pista]), TOPE)
        if nuevo < actual or actual >= TOPE:
            elegidas.append(pista); actual = nuevo
    assert actual == 1, "no se logro solucion unica"
    # 4. quitar las que sobran, sin dejar a nadie sin pista
    for pista in list(elegidas):
        resto = [x for x in elegidas if x != pista]
        if any(x[1] == pista[1] for x in resto) and contar(caso_de(base, resto), 2) == 1:
            elegidas = resto
    elegidas.sort(key=lambda x: orden.index(x[1]))
    final = dict(base, pistas=[list(x) for x in elegidas], solucion={p: list(lugar[p]) for p in orden}, ladron=ladron)
    return final

if __name__ == "__main__":
    SEMILLAS = {1: 7, 2: 11, 3: 5, 4: 3}
    casos = {}
    for nivel in sorted(PLANOS):
        casos[nivel] = fabricar(nivel, SEMILLAS[nivel])
        c = casos[nivel]
        print("nivel", nivel, "| pistas:", len(c["pistas"]), "| ladron:", c["ladron"])
    for c in casos.values():
        c["muebles"] = [[list(k), v] for (k, v) in c["muebles"]]
    with open(os.path.join(AQUI, "..", "mundos", "hacienda", "casos_hacienda.py"), "w", encoding="utf-8") as f:
        f.write("# casos_hacienda.py  ---  los niveles de la hacienda (datos, no programa)\n"
                "# Cada caso tiene una sola solucion. Lo fabrico herramientas/generar_casos_hacienda.py.\n"
                "# Para inventar un caso propio: copien uno, cambien el plano, los muebles y las pistas,\n"
                "# y comprueben con su agente que tiene exactamente una solucion.\n"
                "CASOS = " + pprint.pformat(casos, width=110, sort_dicts=False) + "\n")
    print("escrito casos_hacienda.py")
