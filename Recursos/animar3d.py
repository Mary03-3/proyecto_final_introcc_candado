# animar3d.py  ---  de la bitacora a la pelicula en 3D
#
#   animar3d([(bit1, "Generación 1 · a ciegas"), (bit2, "Generación 2 · con hilo")],
#            dibujar, "pelicula.html", titulo="El robo en la hacienda")
#
# Recibe las bitacoras de las generaciones del agente, EN ORDEN, y la funcion
# dibujar(estado) que devuelve una Escena. Escribe UN archivo .html que se abre
# con doble clic: cada generacion es un capitulo de la pelicula. Tiene pausa,
# paso a paso, velocidad, salto al azar y un boton para grabar el video.
# No necesita internet: la libreria 3D (three.js, licencia MIT) va dentro del archivo.
import base64
import json
import os

from bitacora import TIPOS
from escena import Escena

FIJAS = ("p", "m", "b", "r", "u", "q", "s", "g")          # piso, muro, mueble, rotulo, hueco: no cambian


def animar3d(capitulos, dibujar, archivo="pelicula.html", titulo="", max_eventos=1500,
             velocidad=6, pregunta="", estilo="cine", guion=None, voces=None):
    """capitulos: lista de (bitacora, nombre), (bitacora, nombre, descripcion) o
        (bitacora, nombre, descripcion, velocidad): cada capitulo puede ir a su propio ritmo.
    dibujar: funcion que recibe un estado y devuelve una Escena.
    max_eventos: cuantos eventos de cada capitulo entran en la pelicula.
    pregunta: la pregunta de la ficcion; sale en la portada.
    guion: lo que dice el narrador. Una lista de (capitulo, evento, texto): el capitulo se cuenta
        desde 1 y el evento es el numero que muestra la pelicula (0 = al empezar el capitulo).
    voces: carpeta con los audios del narrador, si ya existen. Cada linea del guion busca su
        archivo g<capitulo>_e<evento>.mp3 (o .wav, .m4a, .ogg); por ejemplo g2_e030.mp3."""
    if len(capitulos) < 1:
        raise ValueError("Hace falta al menos un capitulo.")
    cuadros = []
    indice = {}
    fijo = None
    lista = []
    for cap in capitulos:
        bit, nombre = cap[0], cap[1]
        descripcion = cap[2] if len(cap) > 2 else ""
        if len(bit.eventos) == 0:
            raise ValueError("La bitacora de '%s' esta vacia." % nombre)
        filas = []
        numero = 0
        for (tipo, estado, nota, prof) in bit.eventos[:max_eventos]:
            numero = numero + 1
            try:
                escena = dibujar(estado)
            except Exception as e:
                raise RuntimeError("dibujar fallo en el evento %d ('%s') de '%s' con el estado %r. Error: %s"
                                   % (numero, tipo, nombre, estado, e))
            if not isinstance(escena, Escena):
                raise TypeError("dibujar(estado) debe devolver una Escena y devolvio "
                                + type(escena).__name__ + ". ¿Falta el return?")
            d = escena.datos()
            if fijo is None:
                fijo = {"n": d["n"], "a": d["a"], "w": d["w"], "c": [x for x in d["c"] if x[0] in FIJAS]}
            movil = {"c": [x for x in d["c"] if x[0] not in FIJAS], "p": d["p"], "v": d["v"], "m": d["m"]}
            clave = json.dumps(movil, ensure_ascii=False, separators=(",", ":"))
            if clave not in indice:
                indice[clave] = len(cuadros)
                cuadros.append(clave)
            filas.append([TIPOS.index(tipo), indice[clave], prof, nota])
        lista.append({"nombre": nombre, "desc": descripcion, "vel": cap[3] if len(cap) > 3 else 0, "ev": filas, "total": bit.total(),
                      "cuenta": [bit.cuenta[t] for t in TIPOS], "pila": bit.maxima})

    con_voz = 0
    for (k, evento, frase) in (guion or []):
        if not (1 <= k <= len(lista)):
            raise ValueError("El guion nombra el capitulo %s y la pelicula tiene %d." % (k, len(lista)))
        if not (0 <= evento <= len(lista[k - 1]["ev"])):
            raise ValueError("El guion nombra el evento %s del capitulo %d, que solo muestra %d eventos."
                             % (evento, k, len(lista[k - 1]["ev"])))
        audio = ""
        if voces:
            for ext, mime in ((".mp3", "audio/mpeg"), (".wav", "audio/wav"), (".m4a", "audio/mp4"), (".ogg", "audio/ogg")):
                ruta = os.path.join(voces, nombre_de_voz(k, evento) + ext)
                if os.path.exists(ruta):
                    with open(ruta, "rb") as f:
                        audio = "data:%s;base64,%s" % (mime, base64.b64encode(f.read()).decode("ascii"))
                    con_voz = con_voz + 1
                    break
        lista[k - 1].setdefault("voz", {})[str(evento)] = [str(frase), audio]

    datos = {"titulo": titulo, "pregunta": pregunta, "velocidad": velocidad, "fijo": fijo, "caps": lista}
    texto = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    texto = texto[:-1] + ',"cuadros":[' + ",".join(cuadros) + "]}"
    texto = texto.replace("</", "<\\/")
    aqui = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(aqui, "vendor", "three.min.js"), encoding="utf-8") as f:
        three = f.read().replace("</script", "<\\/script")
    with open(os.path.join(aqui, "visor_cine.html" if estilo == "cine" else "visor3d.html"), encoding="utf-8") as f:
        pagina = f.read()
    pagina = pagina.replace("/*THREE*/", three).replace("/*DATOS*/", texto)
    pagina = pagina.replace("<!--TITULO-->", str(titulo or "Película").replace("<", "&lt;"))
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(pagina)
    try:
        corto = os.path.relpath(archivo)
    except ValueError:
        corto = archivo
    print("Pelicula lista: %s (%d capitulos, %d escenas distintas, %.0f kB). Abrala con doble clic."
          % (corto, len(lista), len(cuadros), os.path.getsize(archivo) / 1024))
    if guion:
        print("  Narrador: %d lineas, %d con voz." % (len(guion), con_voz))
    for c in lista:
        if len(c["ev"]) < c["total"]:
            print("  Aviso: de '%s' entran los primeros %d eventos de %d." % (c["nombre"], len(c["ev"]), c["total"]))
    return archivo


def nombre_de_voz(capitulo, evento):
    """El nombre (sin extension) del audio de una linea del guion."""
    return "g%d_e%03d" % (capitulo, evento)


def escribir_guion(guion, carpeta):
    """Escribe carpeta/guion.txt: una linea por cada frase del narrador, con el nombre que
    debe llevar su audio. Es la lista de trabajo para grabar o generar las voces."""
    os.makedirs(carpeta, exist_ok=True)
    ruta = os.path.join(carpeta, "guion.txt")
    with open(ruta, "w", encoding="utf-8") as f:
        f.write("Guion del narrador. Guarden cada audio en esta carpeta con el nombre indicado (.mp3).\n\n")
        for (k, evento, frase) in guion:
            f.write("%s.mp3\n    %s\n\n" % (nombre_de_voz(k, evento), frase))
    print("Guion escrito en", ruta)
    return ruta
