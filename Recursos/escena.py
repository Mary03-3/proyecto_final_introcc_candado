# escena.py  ---  describir una escena en 3D con pocas ordenes
#
# La funcion dibujar(caso, estado) de cada mundo devuelve una Escena. No hay
# que saber de graficos: se dan ordenes como "aqui hay piso de este color",
# "aqui hay un muro", "aqui esta parado tal personaje". El visor 3D
# (animar3d.py) se encarga de la camara, la luz, las sombras y el movimiento.
#
# Las casillas se nombran (fila, columna); la fila 0 es la del fondo (el norte).
# Un personaje se reconoce por su NOMBRE: si en un estado esta en una casilla y
# en el siguiente en otra, el visor lo hace caminar de una a la otra.


class Escena:
    def __init__(self, filas, columnas, titulo="", ambiente="dia", pared="#4061B0"):
        self.filas = filas
        self.columnas = columnas
        self.titulo = titulo
        self.ambiente = ambiente          # "sala", "cueva" o "dia": la luz y el clima de la escena
        self.pared = pared                # en el ambiente "sala", el color de las paredes del fondo
        self.cosas = []
        self.lineas = None
        self.frase = ""
        self.barra = None

    def _casilla(self, f, c):
        if not (0 <= f < self.filas and 0 <= c < self.columnas):
            raise ValueError("La casilla (%s, %s) no existe en una escena de %d x %d."
                             % (f, c, self.filas, self.columnas))

    # ---- lo que no se mueve ----
    def piso(self, f, c, color="#dddddd"):
        self._casilla(f, c)
        self.cosas.append(["p", f, c, color])

    def muro(self, f, c, lado, bajo=False):
        """Un muro en el borde de la casilla. lado: "N", "S", "E" u "O". bajo: murito divisorio."""
        self._casilla(f, c)
        if lado not in ("N", "S", "E", "O"):
            raise ValueError("El lado de un muro es 'N', 'S', 'E' u 'O'.")
        self.cosas.append(["m", f, c, lado, 1 if bajo else 0])

    def mueble(self, f, c, tipo, color="#8a5a3b"):
        self._casilla(f, c)
        self.cosas.append(["b", f, c, tipo, color])

    def rotulo(self, f, c, texto):
        """Un texto escrito sobre el piso de la casilla."""
        self._casilla(f, c)
        self.cosas.append(["r", f, c, str(texto)])

    def roca(self, f, c):
        """Una casilla llena de roca: por ahi no se pasa."""
        self._casilla(f, c)
        self.cosas.append(["q", f, c])

    def salida(self, f, c):
        """El punto de partida: un parche de rayas en el piso."""
        self._casilla(f, c)
        self.cosas.append(["s", f, c])

    def meta(self, f, c):
        """La meta: un parche verde en el piso."""
        self._casilla(f, c)
        self.cosas.append(["g", f, c])

    def hueco(self, f, c):
        """Una casilla sin piso (un pozo, agua, vacio)."""
        self._casilla(f, c)
        self.cosas.append(["u", f, c])

    # ---- lo que cambia de un estado a otro ----
    def personaje(self, nombre, f, c, color="#e4572e", letra=""):
        self._casilla(f, c)
        self.cosas.append(["h", str(nombre), f, c, color, str(letra)])

    def conejo(self, f, c, nombre="Pixie"):
        """El agente con cuerpo, para los mundos donde alguien camina."""
        self._casilla(f, c)
        self.cosas.append(["j", str(nombre), f, c])

    def caja(self, nombre, f, c, color="#c58b4e"):
        """Un objeto que se puede mover (un bulto, una caja). Se reconoce por su nombre."""
        self._casilla(f, c)
        self.cosas.append(["o", str(nombre), f, c, color])

    def cofre(self, f, c):
        self._casilla(f, c)
        self.cosas.append(["k", "Cofre", f, c])

    def equis(self, f, c, color="#d64545"):
        """Una equis sobre el piso: casilla descartada."""
        self._casilla(f, c)
        self.cosas.append(["x", f, c, color])

    def luz(self, f, c, color="#ffe066"):
        """Resalta una casilla (una meta, una pista, una casilla segura)."""
        self._casilla(f, c)
        self.cosas.append(["l", f, c, color])

    def brisa(self, f, c):
        """Aire que se mueve sobre la casilla: algo se percibe aqui."""
        self._casilla(f, c)
        self.cosas.append(["w", f, c])

    def hilo(self, casillas):
        """Un hilo que recorre, en orden, la lista de casillas: el camino hecho hasta ahora."""
        for (f, c) in casillas:
            self._casilla(f, c)
        self.cosas.append(["i", [[f, c] for (f, c) in casillas]])

    def runa(self, f, c, color="#ff4d4d"):
        """Una marca luminosa sobre la casilla: lo que el agente dedujo de ella."""
        self._casilla(f, c)
        self.cosas.append(["n", f, c, color])

    def ficha(self, f, c, texto, color="#1f2430"):
        """Un numero o una letra parados sobre la casilla."""
        self._casilla(f, c)
        self.cosas.append(["f", f, c, str(texto), color])

    # ---- lo que se lee al lado ----
    def panel(self, titulo, lineas):
        """Una lista de textos al lado de la escena. Cada linea es (texto, marca, resaltada):
        marca es "bien", "mal" o ""; resaltada es True o False."""
        self.lineas = [str(titulo)] + [[str(t), str(m), 1 if r else 0] for (t, m, r) in lineas]

    def medidor(self, nombre, valor, maximo):
        """Una barra con nombre: algo que se gasta (aceite, combustible, tiempo)."""
        self.barra = [str(nombre), valor, maximo]

    def veredicto(self, frase):
        """La respuesta a la pregunta de la ficcion, cuando ya se sabe."""
        self.frase = str(frase)

    def datos(self):
        return {"n": [self.filas, self.columnas], "t": self.titulo, "a": self.ambiente, "w": self.pared, "c": self.cosas,
                "p": self.lineas, "v": self.frase, "m": self.barra}
