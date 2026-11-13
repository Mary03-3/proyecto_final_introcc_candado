# g1_a_ciegas.py  ---  generacion 1: ubicar a todos sin mirar nada y revisar al final
#
# Este agente no sabe nada de la hacienda. Solo usa el contrato del mundo:
# pregunta que decisiones hay, toma una, y sigue. Cuando ya no queda nada
# por decidir, pregunta si el resultado rompe alguna regla.
# Como solo usa el contrato, sirve IGUAL en cualquier otro mundo del proyecto.


def resolver(mundo, caso, bit):
    """Busca todas las soluciones del caso. Devuelve cuantas hallo."""
    return generar(mundo, caso, mundo.inicio(caso), bit)


def generar(mundo, caso, estado, bit):
    if mundo.completo(caso, estado):                       # caso base: todo decidido
        falla = mundo.viola(caso, estado)
        if falla == "":
            bit.registrar("solucion", estado, mundo.respuesta(caso, estado))
            return 1
        bit.registrar("rechazar", estado, falla)
        return 0
    total = 0
    for decision in mundo.opciones(caso, estado):
        nuevo = mundo.aplicar(caso, estado, decision)      # decide sin revisar
        bit.registrar("avanzar", nuevo, mundo.decir(caso, decision))
        total = total + generar(mundo, caso, nuevo, bit)
        bit.registrar("retroceder", estado)
    return total
