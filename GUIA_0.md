# Guía 0: el repositorio del equipo

Esta guía se hace **una sola vez**, antes de la guía de la semana 1. Al terminarla, su equipo tiene un repositorio propio en GitHub, cada integrante tiene una copia en su computador y esa copia sabe traer lo que publique el profesor.

Cada paso tiene tres partes. **Hágalo** dice qué hacer. **Qué deben ver** dice cómo saber si salió bien. **Por qué se hace así** explica la razón. Si lo que ven no se parece a lo que dice el paso, miren la sección «Si algo sale mal» antes de seguir.

| Paso | Qué hacen | Quién |
|---|---|---|
| 1 | Crear la cuenta de GitHub | Cada integrante |
| 2 | Crear el repositorio del equipo | Una sola persona |
| 3 | Invitar a los demás | Esa misma persona |
| 4 | Instalar git y decirle quiénes son | Cada integrante |
| 5 | Clonar el repositorio del equipo | Cada integrante |
| 6 | Conectarlo con el repositorio del curso | Cada integrante |
| 7 | Conocer la rutina de cada día | Todos |

---

## Paso 1. Crear la cuenta de GitHub

**Hágalo.** Entren a <https://github.com/signup> y creen una cuenta con su correo. Si ya tienen una, usen esa. Anoten su nombre de usuario: lo van a necesitar en el paso 3.

**Qué deben ver.** Al entrar a <https://github.com> aparece su foto o su inicial arriba a la derecha.

**Por qué se hace así.** Cada integrante necesita su propia cuenta porque git anota quién hizo cada cambio. Si todo el equipo sube con la cuenta de una sola persona, el historial dice que esa persona hizo todo el proyecto.

---

## Paso 2. Crear el repositorio del equipo

**Hágalo.** Esto lo hace **una sola persona**. Con su cuenta abierta, entre a <https://github.com/cmorregof/proyecto_final_introcc> y oprima el botón **Fork**, arriba a la derecha. En la página que aparece, deje el nombre como está y oprima **Create fork**.

**Qué deben ver.** GitHub los lleva a una página con la dirección `https://github.com/SU-USUARIO/proyecto_final_introcc`. Debajo del nombre dice *forked from cmorregof/proyecto_final_introcc*. Esa dirección es la del repositorio del equipo.

**Por qué se hace así.** Un *fork* es una copia del repositorio del curso que le pertenece a ustedes. En el repositorio del curso no tienen permiso de escribir, y así nadie puede dañar por accidente el material de los demás. En la copia sí, y por eso su trabajo vive allá. La copia recuerda de dónde salió, y eso permite traer después lo que publique el profesor.

---

## Paso 3. Invitar a los demás

**Hágalo.** La misma persona del paso 2 entra al repositorio del equipo y va a **Settings**, luego a **Collaborators**, y oprime **Add people**. Escribe el nombre de usuario de cada integrante y lo agrega. Cada invitado recibe un correo de GitHub y debe oprimir **Accept invitation**.

**Qué deben ver.** En la página de *Collaborators* aparecen todos los integrantes. Mientras alguien no acepte, a su lado dice *Pending invite*.

**Por qué se hace así.** El repositorio es de quien hizo el fork, y solo esa persona puede escribir en él. Al invitar a los demás como colaboradores, todos suben al mismo repositorio. Quien no acepte la invitación podrá clonar, pero no podrá subir.

---

## Paso 4. Instalar git y decirle quiénes son

**Hágalo.** Abran una terminal. En Windows, instalen primero Git desde <https://git-scm.com/download/win> con las opciones que vienen marcadas, y usen el programa **Git Bash** como terminal para todo el proyecto. En Mac, abran la aplicación Terminal. Escriban:

```bash
git --version
```

Si en Mac aparece una ventana que ofrece instalar las herramientas de línea de comandos, acepten y esperen a que termine. Después escriban estas dos líneas, con su nombre y con el correo de su cuenta de GitHub:

```bash
git config --global user.name "Nombre Apellido"
git config --global user.email "correo@ejemplo.com"
```

**Qué deben ver.** El primer comando responde algo como `git version 2.43.0`; el número puede ser otro. Los otros dos no responden nada. Para comprobar que quedaron:

```bash
git config --global user.name
```

debe responder el nombre que escribieron.

**Por qué se hace así.** Git firma cada cambio con ese nombre y ese correo. Si el correo es el de su cuenta de GitHub, la página del repositorio muestra su usuario al lado de cada cambio. Sin estos dos datos, git se niega a guardar cambios.

---

## Paso 5. Clonar el repositorio del equipo

**Hágalo.** En la terminal, vayan a la carpeta donde quieren guardar el proyecto y clonen. Cambien `USUARIO-DEL-EQUIPO` por el usuario de quien hizo el fork.

```bash
git clone https://github.com/USUARIO-DEL-EQUIPO/proyecto_final_introcc.git
cd proyecto_final_introcc
ls
```

**Qué deben ver.** El `clone` termina sin la palabra `fatal`. El `ls` muestra, entre otras cosas, `MANUAL_PILOTO.md`, `mundos`, `Recursos`, `ejemplo_cueva` y `semana1`.

**Por qué se hace así.** *Clonar* trae a su computador una copia completa del repositorio del equipo, con toda su historia. Desde ese momento trabajan en su computador y solo hablan con GitHub en dos momentos: cuando traen lo de los demás y cuando suben lo suyo.

---

## Paso 6. Conectarlo con el repositorio del curso

**Hágalo.** Dentro de la carpeta `proyecto_final_introcc`:

```bash
git remote add curso https://github.com/cmorregof/proyecto_final_introcc.git
git config pull.rebase false
git pull --no-edit curso main
git remote -v
```

**Qué deben ver.** El `pull` termina con `Already up to date.` o con una lista de archivos nuevos. El último comando muestra cuatro líneas:

```
curso   https://github.com/cmorregof/proyecto_final_introcc.git (fetch)
curso   https://github.com/cmorregof/proyecto_final_introcc.git (push)
origin  https://github.com/USUARIO-DEL-EQUIPO/proyecto_final_introcc.git (fetch)
origin  https://github.com/USUARIO-DEL-EQUIPO/proyecto_final_introcc.git (push)
```

**Por qué se hace así.** Su copia queda con dos orígenes, y cada uno sirve para una sola cosa. `origin` es el repositorio del equipo: de ahí traen lo de sus compañeros y ahí suben. `curso` es el del profesor: de ahí solo traen. La línea `pull.rebase false` le dice a git que junte las dos historias sin reescribir la de ustedes.

---

## Paso 7. Conocer la rutina de cada día

**Hágalo.** No hay nada que correr todavía. Lean la rutina, porque la van a repetir durante cinco semanas.

Al **sentarse a trabajar**:

```bash
git pull                          # lo que subieron sus compañeros
git pull --no-edit curso main     # lo que publicó el profesor
```

Al **terminar**:

```bash
git add equipo
git commit -m "Una frase que diga qué hicieron"
git push
```

**Qué deben ver.** El primer `git push` lo harán en el paso 10 de la guía de la semana 1. Esa primera vez, git les pide entrar a GitHub. En Windows se abre una ventana del navegador para iniciar sesión. Si en cambio la terminal pregunta `Username` y `Password`, lean la primera entrada de «Si algo sale mal».

**Por qué se hace así.** La rutina tiene un orden y una regla. El orden es traer antes de trabajar y subir al terminar, para que nadie trabaje sobre una copia vieja. La regla es que el equipo solo modifica la carpeta `equipo/`, y el profesor nunca la toca. Mientras se respete, los dos `pull` no chocan. Por eso el `git add` nombra esa carpeta y no usa un punto.

---

## Si algo sale mal

**La terminal pide `Password` y no acepta la clave de la cuenta.** GitHub no recibe la clave de la cuenta en la terminal. Pide un *token*, que es una clave larga creada para ese computador. En GitHub vayan a **Settings**, **Developer settings**, **Personal access tokens**, **Tokens (classic)** y **Generate new token (classic)**. Marquen la casilla **repo**, generen el token y cópienlo. En la terminal, escriban su usuario en `Username` y peguen el token en `Password`. Al pegar no se ve nada en pantalla; es normal.

**`remote: Permission to ... denied` o `error: 403` al hacer `push`.** Su usuario no es colaborador del repositorio del equipo, o no ha aceptado la invitación. Vuelvan al paso 3.

**`error: remote curso already exists.`** Ya lo habían agregado. No hay nada que arreglar.

**`fatal: not a git repository (or any of the parent directories): .git`** Están fuera de la carpeta del repositorio. Entren con `cd proyecto_final_introcc`.

**`Author identity unknown` y `*** Please tell me who you are.`** Falta el paso 4.

**`fatal: repository '...' not found` al clonar.** La dirección está mal escrita o el `USUARIO-DEL-EQUIPO` no es el de quien hizo el fork. Cópienla de la barra del navegador, en la página del repositorio del equipo.

**`CONFLICT` después de un `pull`.** Alguien cambió un archivo fuera de `equipo/`, o dos personas cambiaron la misma línea del mismo archivo. No sigan trabajando encima: llamen al profesor.

---

## Dos cosas que conviene saber

- El repositorio del equipo es **público**, igual que el del curso. Cualquiera puede verlo. No suban claves, tokens ni datos personales.
- Si su equipo ya había hecho el fork antes de leer esta guía, no lo repitan. Revisen que todos sean colaboradores (paso 3) y que cada copia tenga el remoto `curso` (paso 6).

Cuando terminen, sigan con la guía de la semana 1 de su mundo, en `semana1/guias/`.
