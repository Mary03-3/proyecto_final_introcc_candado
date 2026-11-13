# g3_detective.py  ---  generacion 3: deducir antes de probar
#
# Este agente SI conoce la hacienda. Lleva, para cada persona (y para el cofre),
# la lista de casillas donde todavia podria estar: sus CANDIDATAS. Y aplica
# tres reglas de inferencia, que son implicaciones:
#
#   Regla 1 (la pista propia).  Si la pista de P dice algo de su casilla,
#       entonces las casillas que no lo cumplen quedan descartadas para P.
#   Regla 2 (fila y columna).   Si P esta en la fila f y la columna c,
#       entonces nadie mas esta en esa fila ni en esa columna.
#   Regla 3 (pistas de pareja). Si ya se sabe donde esta P y una pista relaciona
#       a P con Q, entonces las casillas de Q que contradicen la pista se descartan.
#
# Con las candidatas hace dos cosas mas:
#   - ubica primero a quien menos candidatas tiene (el mas acorralado);
#   - si alguien se queda sin candidatas, PODA: por aqui no hay solucion,
#     y lo sabe sin probar nada mas.
#
# Estas reglas hablan de filas, habitaciones y pistas: no sirven en otro mundo.


def resolver(mundo, caso, bit):
    """Busca todas las soluciones del caso. Devuelve cuantas hallo."""
    estado = mundo.inicio(caso)
    candidatas = {}
    for p in caso["orden"]:
        todas = mundo.casillas_libres(caso)
        quedan = []
        for casilla in todas:                              # Regla 1
            if sirve(mundo, caso, {p: casilla}):
                quedan.append(casilla)
        candidatas[p] = quedan
        if len(quedan) < len(todas):
            bit.registrar("deducir", mirar(estado, p, todas, quedan),
                          "por su pista, a %s le quedan %d casillas" % (p, len(quedan)))
    return buscar(mundo, caso, estado, candidatas, bit)


def sirve(mundo, caso, lugar):
    """¿Este reparto a medias respeta fila, columna y todas las pistas que ya se pueden revisar?"""
    return mundo.choca(caso, lugar) == ""


def mirar(estado, persona, antes, quedan):
    """La foto para la bitacora: el estado, a quien se mira y que casillas se le tacharon."""
    tachadas = []
    for casilla in antes:
        if casilla not in quedan:
            tachadas.append(casilla)
    return {"lugar": estado["lugar"], "foco": persona, "tachadas": tachadas}


def mas_acorralado(caso, estado, candidatas):
    """De los que faltan por ubicar, el que menos candidatas tiene."""
    mejor = None
    for p in caso["orden"]:
        if p not in estado["lugar"]:
            if mejor is None or len(candidatas[p]) < len(candidatas[mejor]):
                mejor = p
    return mejor


def buscar(mundo, caso, estado, candidatas, bit):
    if mundo.completo(caso, estado):
        falla = mundo.viola(caso, estado)
        if falla == "":
            bit.registrar("solucion", estado, mundo.respuesta(caso, estado))
            return 1
        bit.registrar("rechazar", estado, falla)
        return 0
    p = mas_acorralado(caso, estado, candidatas)
    total = 0
    for casilla in candidatas[p]:
        nuevo = mundo.aplicar(caso, estado, (p, casilla))
        bit.registrar("avanzar", nuevo, mundo.decir(caso, (p, casilla)))
        # Reglas 2 y 3: lo que esta decision implica para los que faltan
        nuevas = {}
        vacio = None
        apretado = None
        for q in caso["orden"]:
            if q in nuevo["lugar"]:
                continue
            quedan = []
            for otra in candidatas[q]:
                prueba = dict(nuevo["lugar"])
                prueba[q] = otra
                if sirve(mundo, caso, prueba):
                    quedan.append(otra)
            nuevas[q] = quedan
            if len(quedan) == 0 and vacio is None:
                vacio = q
            if apretado is None or len(quedan) < len(nuevas[apretado]):
                apretado = q
        if vacio is not None:
            bit.registrar("podar", mirar(nuevo, vacio, mundo.casillas_libres(caso), []),
                          "%s ya no cabe en ninguna casilla" % vacio)
        else:
            if apretado is not None:
                bit.registrar("deducir", mirar(nuevo, apretado, mundo.casillas_libres(caso), nuevas[apretado]),
                              "a %s le quedan %d casillas" % (apretado, len(nuevas[apretado])))
            total = total + buscar(mundo, caso, nuevo, nuevas, bit)
        bit.registrar("retroceder", estado)
    return total
