# g2_con_hilo.py  ---  generacion 2: revisar en cada paso y devolverse a tiempo
#
# La unica diferencia con la generacion 1 es DONDE se pregunta por las reglas:
# aqui se pregunta despues de cada decision, no al final. Si la decision ya
# rompe una regla, no se sigue por ahi.
# Tampoco sabe nada de la hacienda: sirve igual en cualquier otro mundo.


def resolver(mundo, caso, bit):
    """Busca todas las soluciones del caso. Devuelve cuantas hallo."""
    return buscar(mundo, caso, mundo.inicio(caso), bit)


def buscar(mundo, caso, estado, bit):
    if mundo.completo(caso, estado):                       # caso base: todo decidido y nada roto
        bit.registrar("solucion", estado, mundo.respuesta(caso, estado))
        return 1
    total = 0
    for decision in mundo.opciones(caso, estado):
        nuevo = mundo.aplicar(caso, estado, decision)
        falla = mundo.viola(caso, nuevo)
        if falla == "":
            bit.registrar("avanzar", nuevo, mundo.decir(caso, decision))
            total = total + buscar(mundo, caso, nuevo, bit)
            bit.registrar("retroceder", estado)            # el hilo: volver a donde estaba
        else:
            bit.registrar("rechazar", nuevo, falla)
    return total
