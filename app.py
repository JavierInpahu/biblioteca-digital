import os
from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import create_engine, text
from html import escape

load_dotenv()

app = FastAPI()

conexion = create_engine(
    os.environ["DATABASE_URL"],
    pool_pre_ping=True
)

TABLAS = {
    "categorias": {
        "titulo": "Categorías",
        "pk": "id_categoria",
        "campos": ["nombre"]
    },
    "libros": {
        "titulo": "Libros",
        "pk": "id_libro",
        "campos": ["titulo", "autor", "isbn", "id_categoria"]
    },
    "usuarios": {
        "titulo": "Usuarios",
        "pk": "id_usuario",
        "campos": ["nombre", "correo"]
    },
    "reservas": {
        "titulo": "Reservas",
        "pk": "id_reserva",
        "campos": ["fecha_reserva", "id_usuario", "id_libro"]
    }
}

ETIQUETAS = {
    "nombre": "Nombre",
    "titulo": "Título",
    "autor": "Autor",
    "isbn": "ISBN",
    "correo": "Correo electrónico",
    "id_categoria": "Categoría",
    "fecha_reserva": "Fecha",
    "id_usuario": "Usuario",
    "id_libro": "Libro"
}

# ---------------------------------------------------------------
# Estilos (morado, blanco y negro). Se guarda como texto normal
# para no tener que duplicar las llaves del CSS.
# ---------------------------------------------------------------
ESTILOS = """
:root {
    --morado: #6A0DAD;
    --morado-oscuro: #4B0082;
    --morado-claro: #F3E8FF;
    --negro: #111111;
    --gris-texto: #4B5563;
    --gris-borde: #E5E1EC;
    --fondo: #F6F4FA;
    --blanco: #FFFFFF;
    --rojo: #C62828;
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; scroll-padding-top: 80px; }

body {
    margin: 0;
    font-family: "Segoe UI", system-ui, -apple-system, Roboto, Arial, sans-serif;
    background: var(--fondo);
    color: var(--negro);
    line-height: 1.5;
}

/* ---------- Barra superior ---------- */
.topbar {
    background: var(--negro);
    border-bottom: 3px solid var(--morado);
    position: sticky;
    top: 0;
    z-index: 10;
}

.topbar-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    flex-wrap: wrap;
}

.marca {
    color: var(--blanco);
    text-decoration: none;
    font-size: 22px;
    font-weight: 700;
    letter-spacing: .3px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.marca .logo {
    background: var(--morado);
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
}

.marca small {
    color: #C4B5FD;
    font-weight: 400;
    font-size: 13px;
    display: block;
    margin-top: -2px;
}

nav { display: flex; gap: 6px; flex-wrap: wrap; }

nav a {
    color: #E5E7EB;
    text-decoration: none;
    font-weight: 600;
    font-size: 14px;
    padding: 8px 14px;
    border-radius: 8px;
    transition: background .15s, color .15s;
}

nav a:hover { background: var(--morado); color: var(--blanco); }

/* ---------- Contenido ---------- */
.contenedor {
    width: 100%;
    max-width: 1200px;
    margin: 28px auto;
    padding: 0 20px;
}

.aviso {
    background: var(--morado-claro);
    border-left: 5px solid var(--morado);
    color: var(--morado-oscuro);
    padding: 14px 18px;
    margin-bottom: 22px;
    border-radius: 8px;
    font-weight: 600;
}

/* ---------- Tarjetas de resumen ---------- */
.resumen {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 16px;
    margin-bottom: 26px;
}

.tarjeta {
    background: var(--blanco);
    border-radius: 14px;
    padding: 18px 20px;
    text-decoration: none;
    color: var(--negro);
    border: 1px solid var(--gris-borde);
    border-top: 4px solid var(--morado);
    box-shadow: 0 2px 10px rgba(75, 0, 130, .06);
    transition: transform .15s, box-shadow .15s;
}

.tarjeta:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(75, 0, 130, .15);
}

.tarjeta .numero {
    font-size: 34px;
    font-weight: 800;
    color: var(--morado);
    line-height: 1.1;
}

.tarjeta .nombre {
    color: var(--gris-texto);
    font-weight: 600;
    font-size: 14px;
}

/* ---------- Paneles ---------- */
.panel {
    background: var(--blanco);
    padding: 24px;
    margin-bottom: 26px;
    border-radius: 14px;
    border: 1px solid var(--gris-borde);
    box-shadow: 0 2px 10px rgba(75, 0, 130, .06);
    overflow-x: auto;
}

.panel-cabecera {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    flex-wrap: wrap;
    margin-bottom: 14px;
}

h2 {
    margin: 0;
    color: var(--negro);
    font-size: 22px;
    display: flex;
    align-items: center;
    gap: 10px;
}

h2::before {
    content: "";
    width: 6px;
    height: 24px;
    border-radius: 3px;
    background: var(--morado);
    display: inline-block;
}

.contador {
    background: var(--morado-claro);
    color: var(--morado-oscuro);
    font-size: 12px;
    font-weight: 700;
    padding: 3px 10px;
    border-radius: 999px;
}

/* ---------- Tablas ---------- */
table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin-top: 6px;
    overflow: hidden;
    border-radius: 10px;
    border: 1px solid var(--gris-borde);
}

th {
    background: var(--negro);
    color: var(--blanco);
    padding: 13px 14px;
    text-align: left;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: .6px;
}

th:first-child { border-top-left-radius: 9px; }
th:last-child  { border-top-right-radius: 9px; }

td {
    padding: 12px 14px;
    border-bottom: 1px solid var(--gris-borde);
    color: var(--gris-texto);
}

tr:last-child td { border-bottom: none; }
tr:nth-child(even) td { background: #FAF8FD; }
tbody tr:hover td { background: var(--morado-claro); color: var(--negro); }

.vacio {
    text-align: center;
    color: #9CA3AF;
    padding: 26px;
    font-style: italic;
}

.acciones { white-space: nowrap; text-align: right; }

/* ---------- Botones ---------- */
.btn {
    display: inline-block;
    padding: 9px 16px;
    border: 2px solid transparent;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 700;
    text-decoration: none;
    cursor: pointer;
    margin: 2px;
    font-family: inherit;
    transition: background .15s, color .15s, border-color .15s, transform .1s;
}

.btn:active { transform: scale(.97); }

.btn-primario { background: var(--morado); color: var(--blanco); }
.btn-primario:hover { background: var(--morado-oscuro); }

.btn-oscuro { background: var(--negro); color: var(--blanco); }
.btn-oscuro:hover { background: #333; }

.btn-borde {
    background: var(--blanco);
    color: var(--negro);
    border-color: var(--negro);
}
.btn-borde:hover { background: var(--negro); color: var(--blanco); }

.btn-peligro {
    background: var(--blanco);
    color: var(--rojo);
    border-color: var(--rojo);
}
.btn-peligro:hover { background: var(--rojo); color: var(--blanco); }

/* ---------- Formularios ---------- */
.formulario { max-width: 640px; margin: 0 auto 26px; }

label {
    display: block;
    font-weight: 700;
    font-size: 14px;
    color: var(--negro);
    margin-top: 6px;
}

input, select {
    width: 100%;
    padding: 12px 14px;
    margin: 8px 0 18px;
    border: 2px solid var(--gris-borde);
    border-radius: 8px;
    font-size: 15px;
    font-family: inherit;
    background: var(--blanco);
    color: var(--negro);
    transition: border-color .15s, box-shadow .15s;
}

input:focus, select:focus {
    outline: none;
    border-color: var(--morado);
    box-shadow: 0 0 0 4px rgba(106, 13, 173, .15);
}

.barra-botones { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 8px; }

/* ---------- Pie ---------- */
footer {
    text-align: center;
    padding: 26px 20px 34px;
    color: #6B7280;
    font-size: 14px;
}

footer strong { color: var(--morado); }

/* ---------- Pantallas pequeñas ---------- */
@media (max-width: 640px) {
    .topbar-inner { justify-content: center; }
    .marca { font-size: 19px; }
    .panel { padding: 16px; }
    th, td { padding: 10px; font-size: 13px; }
    .acciones { white-space: normal; }
}
"""


def pagina(contenido, mensaje=""):

    aviso = ""

    if mensaje:
        aviso = f'<div class="aviso">{escape(mensaje)}</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Biblioteca Digital</title>
        <style>{ESTILOS}</style>
    </head>

    <body>

        <div class="topbar">
            <div class="topbar-inner">
                <a class="marca" href="/">
                    <span class="logo">📚</span>
                    <span>Biblioteca Digital
                        <small>Sistema de gestión</small>
                    </span>
                </a>

                <nav>
                    <a href="/">Inicio</a>
                    <a href="/#categorias">Categorías</a>
                    <a href="/#libros">Libros</a>
                    <a href="/#usuarios">Usuarios</a>
                    <a href="/#reservas">Reservas</a>
                </nav>
            </div>
        </div>

        <div class="contenedor">
            {aviso}
            {contenido}
        </div>

        <footer>
            <strong>Biblioteca Digital</strong> · FastAPI · MySQL · Docker
        </footer>

    </body>
    </html>
    """


def panel_mensaje(titulo, contenido_html):
    return pagina(f"""
        <div class="panel formulario">
            <div class="panel-cabecera"><h2>{titulo}</h2></div>
            {contenido_html}
            <div class="barra-botones">
                <a class="btn btn-primario" href="/">Volver</a>
            </div>
        </div>
    """)


def boton_nuevo(tipo):
    return f'<a class="btn btn-primario" href="/nuevo/{tipo}">+ Agregar</a>'


def tarjeta_resumen(tipo, cantidad):
    return f"""
    <a class="tarjeta" href="/#{tipo}">
        <div class="numero">{cantidad}</div>
        <div class="nombre">{TABLAS[tipo]["titulo"]}</div>
    </a>
    """


def tabla(tipo, filas, columnas):

    config = TABLAS[tipo]

    resultado = f"""
    <div class="panel" id="{tipo}">
        <div class="panel-cabecera">
            <h2>{config["titulo"]} <span class="contador">{len(filas)}</span></h2>
            {boton_nuevo(tipo)}
        </div>

        <table>
        <tr>
    """

    for columna, etiqueta in columnas:
        resultado += f"<th>{etiqueta}</th>"

    resultado += '<th style="text-align:right">Acciones</th></tr>'

    if not filas:
        resultado += f"""
        <tr>
            <td class="vacio" colspan="{len(columnas) + 1}">
                Aún no hay registros. Usa «Agregar» para crear el primero.
            </td>
        </tr>
        """

    for fila in filas:

        resultado += "<tr>"

        for columna, etiqueta in columnas:
            valor = escape(str(fila.get(columna, "")))
            resultado += f"<td>{valor}</td>"

        identificador = fila[config["pk"]]

        resultado += f"""
        <td class="acciones">

            <a class="btn btn-oscuro"
               href="/editar/{tipo}/{identificador}">
               Editar
            </a>

            <form method="post"
                  action="/eliminar/{tipo}/{identificador}"
                  style="display:inline"
                  onsubmit="return confirm('¿Deseas eliminar este registro?')">

                <button class="btn btn-peligro" type="submit">
                    Eliminar
                </button>

            </form>

        </td>
        </tr>
        """

    resultado += "</table></div>"

    return resultado


@app.get("/", response_class=HTMLResponse)
def inicio(mensaje: str = ""):

    with conexion.connect() as conn:

        categorias = conn.execute(
            text("SELECT * FROM categorias")
        ).mappings().all()

        libros = conn.execute(text("""
            SELECT l.id_libro, l.titulo, l.autor,
                   l.isbn, c.nombre AS categoria
            FROM libros l
            LEFT JOIN categorias c
            ON l.id_categoria = c.id_categoria
        """)).mappings().all()

        usuarios = conn.execute(
            text("SELECT * FROM usuarios")
        ).mappings().all()

        reservas = conn.execute(text("""
            SELECT r.id_reserva, r.fecha_reserva,
                   u.nombre AS usuario,
                   l.titulo AS libro
            FROM reservas r
            LEFT JOIN usuarios u
            ON r.id_usuario = u.id_usuario
            LEFT JOIN libros l
            ON r.id_libro = l.id_libro
        """)).mappings().all()

    contenido = '<div class="resumen">'
    contenido += tarjeta_resumen("categorias", len(categorias))
    contenido += tarjeta_resumen("libros", len(libros))
    contenido += tarjeta_resumen("usuarios", len(usuarios))
    contenido += tarjeta_resumen("reservas", len(reservas))
    contenido += "</div>"

    contenido += tabla(
        "categorias",
        categorias,
        [("id_categoria", "ID"), ("nombre", "Nombre")]
    )

    contenido += tabla(
        "libros",
        libros,
        [
            ("id_libro", "ID"),
            ("titulo", "Título"),
            ("autor", "Autor"),
            ("isbn", "ISBN"),
            ("categoria", "Categoría")
        ]
    )

    contenido += tabla(
        "usuarios",
        usuarios,
        [
            ("id_usuario", "ID"),
            ("nombre", "Nombre"),
            ("correo", "Correo")
        ]
    )

    contenido += tabla(
        "reservas",
        reservas,
        [
            ("id_reserva", "ID"),
            ("fecha_reserva", "Fecha"),
            ("usuario", "Usuario"),
            ("libro", "Libro")
        ]
    )

    return pagina(contenido, mensaje)


def formulario(tipo, datos=None, editar=False):

    config = TABLAS[tipo]
    datos = datos or {}

    titulo = "Editar" if editar else "Agregar"

    accion = (
        f"/actualizar/{tipo}/{datos[config['pk']]}"
        if editar else f"/crear/{tipo}"
    )

    contenido = f"""
    <div class="panel formulario">

        <div class="panel-cabecera">
            <h2>{titulo} {config["titulo"]}</h2>
        </div>

        <form method="post" action="{accion}">
    """

    with conexion.connect() as conn:

        for campo in config["campos"]:

            valor = escape(str(datos.get(campo, "")))

            contenido += f"<label>{ETIQUETAS[campo]}</label>"

            if campo == "id_categoria":

                opciones = conn.execute(
                    text("SELECT * FROM categorias")
                ).mappings().all()

                contenido += '<select name="id_categoria" required>'

                for opcion in opciones:
                    seleccionado = (
                        "selected"
                        if str(opcion["id_categoria"]) == valor
                        else ""
                    )

                    contenido += f"""
                    <option value="{opcion['id_categoria']}" {seleccionado}>
                        {escape(opcion['nombre'])}
                    </option>
                    """

                contenido += "</select>"

            elif campo == "id_usuario":

                opciones = conn.execute(
                    text("SELECT * FROM usuarios")
                ).mappings().all()

                contenido += '<select name="id_usuario" required>'

                for opcion in opciones:
                    seleccionado = (
                        "selected"
                        if str(opcion["id_usuario"]) == valor
                        else ""
                    )

                    contenido += f"""
                    <option value="{opcion['id_usuario']}" {seleccionado}>
                        {escape(opcion['nombre'])}
                    </option>
                    """

                contenido += "</select>"

            elif campo == "id_libro":

                opciones = conn.execute(
                    text("SELECT * FROM libros")
                ).mappings().all()

                contenido += '<select name="id_libro" required>'

                for opcion in opciones:
                    seleccionado = (
                        "selected"
                        if str(opcion["id_libro"]) == valor
                        else ""
                    )

                    contenido += f"""
                    <option value="{opcion['id_libro']}" {seleccionado}>
                        {escape(opcion['titulo'])}
                    </option>
                    """

                contenido += "</select>"

            else:

                tipo_input = (
                    "date" if campo == "fecha_reserva"
                    else "email" if campo == "correo"
                    else "text"
                )

                contenido += f"""
                <input type="{tipo_input}"
                       name="{campo}"
                       value="{valor}"
                       required>
                """

    contenido += """
            <div class="barra-botones">
                <button class="btn btn-primario" type="submit">
                    Guardar
                </button>

                <a class="btn btn-borde" href="/">
                    Cancelar
                </a>
            </div>

        </form>
    </div>
    """

    return pagina(contenido)


@app.get("/nuevo/{tipo}", response_class=HTMLResponse)
def nuevo(tipo: str):

    if tipo not in TABLAS:
        return HTMLResponse("Sección no encontrada", status_code=404)

    return formulario(tipo)


@app.post("/crear/{tipo}")
async def crear(tipo: str, request: Request):

    if tipo not in TABLAS:
        return HTMLResponse("Sección no encontrada", status_code=404)

    config = TABLAS[tipo]
    datos = await request.form()

    valores = {
        campo: datos.get(campo, "").strip()
        for campo in config["campos"]
    }

    try:
        for campo in ["id_categoria", "id_usuario", "id_libro"]:
            if campo in valores:
                valores[campo] = int(valores[campo])

        columnas = ", ".join(valores.keys())
        parametros = ", ".join(f":{campo}" for campo in valores)

        consulta = f"""
            INSERT INTO {tipo} ({columnas})
            VALUES ({parametros})
        """

        with conexion.begin() as conn:
            conn.execute(text(consulta), valores)

        return RedirectResponse(
            "/?mensaje=Registro+agregado+correctamente",
            status_code=303
        )

    except Exception as e:
        return HTMLResponse(
            panel_mensaje(
                "Error al guardar",
                f"<p>{escape(str(e))}</p>"
            ),
            status_code=400
        )


@app.get("/editar/{tipo}/{identificador}", response_class=HTMLResponse)
def editar(tipo: str, identificador: int):

    if tipo not in TABLAS:
        return HTMLResponse("Sección no encontrada", status_code=404)

    config = TABLAS[tipo]

    with conexion.connect() as conn:

        datos = conn.execute(
            text(f"""
                SELECT * FROM {tipo}
                WHERE {config['pk']} = :id
            """),
            {"id": identificador}
        ).mappings().first()

    if not datos:
        return HTMLResponse("Registro no encontrado", status_code=404)

    return formulario(tipo, datos, True)


@app.post("/actualizar/{tipo}/{identificador}")
async def actualizar(tipo: str, identificador: int, request: Request):

    if tipo not in TABLAS:
        return HTMLResponse("Sección no encontrada", status_code=404)

    config = TABLAS[tipo]
    datos = await request.form()

    valores = {
        campo: datos.get(campo, "").strip()
        for campo in config["campos"]
    }

    try:
        for campo in ["id_categoria", "id_usuario", "id_libro"]:
            if campo in valores:
                valores[campo] = int(valores[campo])

        asignaciones = ", ".join(
            f"{campo} = :{campo}"
            for campo in valores
        )

        valores["id"] = identificador

        with conexion.begin() as conn:
            resultado = conn.execute(
                text(f"""
                    UPDATE {tipo}
                    SET {asignaciones}
                    WHERE {config['pk']} = :id
                """),
                valores
            )

        if resultado.rowcount == 0:
            return HTMLResponse("Registro no encontrado", status_code=404)

        return RedirectResponse(
            "/?mensaje=Registro+actualizado+correctamente",
            status_code=303
        )

    except Exception as e:
        return HTMLResponse(
            panel_mensaje(
                "Error al actualizar",
                f"<p>{escape(str(e))}</p>"
            ),
            status_code=400
        )


@app.post("/eliminar/{tipo}/{identificador}")
def eliminar(tipo: str, identificador: int):

    if tipo not in TABLAS:
        return HTMLResponse("Sección no encontrada", status_code=404)

    config = TABLAS[tipo]

    try:
        with conexion.begin() as conn:

            if tipo == "categorias":
                cantidad = conn.execute(
                    text("""
                        SELECT COUNT(*) FROM libros
                        WHERE id_categoria = :id
                    """),
                    {"id": identificador}
                ).scalar()

                if cantidad > 0:
                    return HTMLResponse(
                        panel_mensaje(
                            "No se puede eliminar",
                            f"<p>Esta categoría tiene {cantidad} libro(s) asociado(s).</p>"
                        ),
                        status_code=409
                    )

            elif tipo == "usuarios":
                cantidad = conn.execute(
                    text("""
                        SELECT COUNT(*) FROM reservas
                        WHERE id_usuario = :id
                    """),
                    {"id": identificador}
                ).scalar()

                if cantidad > 0:
                    return HTMLResponse(
                        panel_mensaje(
                            "No se puede eliminar",
                            f"<p>Este usuario tiene {cantidad} reserva(s).</p>"
                        ),
                        status_code=409
                    )

            elif tipo == "libros":
                cantidad = conn.execute(
                    text("""
                        SELECT COUNT(*) FROM reservas
                        WHERE id_libro = :id
                    """),
                    {"id": identificador}
                ).scalar()

                if cantidad > 0:
                    return HTMLResponse(
                        panel_mensaje(
                            "No se puede eliminar",
                            f"<p>Este libro tiene {cantidad} reserva(s).</p>"
                        ),
                        status_code=409
                    )

            conn.execute(
                text(f"""
                    DELETE FROM {tipo}
                    WHERE {config['pk']} = :id
                """),
                {"id": identificador}
            )

        return RedirectResponse(
            "/?mensaje=Registro+eliminado+correctamente",
            status_code=303
        )

    except Exception as e:
        return HTMLResponse(
            panel_mensaje(
                "Error al eliminar",
                f"<p>{escape(str(e))}</p>"
            ),
            status_code=400
        )


@app.get("/prueba-db")
def prueba_db():

    with conexion.connect():
        return {"mensaje": "Conexion exitosa a MySQL"}
