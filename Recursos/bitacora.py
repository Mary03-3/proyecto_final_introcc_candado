# bitacora.py  ---  la tabla de seguimiento, pero la escribe el programa
#
# En clase llenamos tablas de seguimiento a mano: una fila por cada paso.
# Una Bitacora es eso mismo. Cada vez que su algoritmo hace algo, lo anota
# con   bit.registrar(tipo, estado, nota)   y la bitacora cuenta y guarda.
# Despues, animar.py convierte esas filas en una pelicula.
import copy
import json

# Los seis tipos de evento. No hay mas: todo lo que hace una busqueda cabe aqui.
TIPOS = ("avanzar", "rechazar", "deducir", "podar", "retroceder", "solucion")

LIMITE = 300000      # eventos que se guardan como maximo; despues solo se cuenta


class Bitacora:
    def __init__(self, nombre, grabar=True):
        self.nombre = nombre          # como se llama esta version en la pantalla
        self.grabar = grabar          # False: solo cuenta (para medir casos grandes)
        self.eventos = []             # una fila por evento: (tipo, estado, nota, profundidad)
        self.cuenta = {}
        for t in TIPOS:
            self.cuenta[t] = 0
        self.profundidad = 0          # cuantas decisiones hay tomadas ahora (la pila)
        self.maxima = 0
        self.recortada = False        # True si se lleno y dejo de guardar
        self.tope = None              # si es un numero, la busqueda se detiene al llegar a ese evento

    def registrar(self, tipo, estado=None, nota=""):
        """Anota un evento. tipo es uno de TIPOS; estado es lo que se va a dibujar."""
        if tipo not in TIPOS:
            raise ValueError("No existe el evento '" + str(tipo) + "'. Los eventos son: "
                             + ", ".join(TIPOS))
        if self.tope is not None and self.total() >= self.tope:
            raise StopIteration("la bitacora llego a su tope de %d eventos" % self.tope)
        self.cuenta[tipo] = self.cuenta[tipo] + 1
        if tipo == "avanzar":
            self.profundidad = self.profundidad + 1
            if self.profundidad > self.maxima:
                self.maxima = self.profundidad
        if tipo == "retroceder":
            self.profundidad = self.profundidad - 1
            if self.profundidad < 0:
                raise ValueError("Hay un 'retroceder' sin su 'avanzar': la busqueda "
                                 "deshizo una decision que nunca tomo.")
        if self.grabar:
            if len(self.eventos) >= LIMITE:
                self.grabar = False
                self.recortada = True
                return
            # Se guarda una COPIA del estado. Si se guardara el estado mismo,
            # todas las filas terminarian mostrando el ultimo tablero.
            self.eventos.append((tipo, copy.deepcopy(estado), str(nota), self.profundidad))

    def total(self):
        """Cuantos eventos ocurrieron en total (se hayan guardado o no)."""
        suma = 0
        for t in TIPOS:
            suma = suma + self.cuenta[t]
        return suma

    def resumen(self):
        """Un diccionario con el nombre y los seis contadores."""
        r = {"version": self.nombre}
        for t in TIPOS:
            r[t] = self.cuenta[t]
        r["eventos"] = self.total()
        r["pila_maxima"] = self.maxima
        return r

    def guardar(self, archivo):
        """Escribe la bitacora en un archivo de texto, una linea por evento."""
        with open(archivo, "w", encoding="utf-8") as f:
            f.write(json.dumps(self.resumen(), ensure_ascii=False) + "\n")
            for (tipo, estado, nota, prof) in self.eventos:
                fila = {"tipo": tipo, "pila": prof, "nota": nota, "estado": repr(estado)}
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
