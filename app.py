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

        <style>
            * {{ box-sizing: border-box; }}

            body {{
                margin: 0;
                font-family: Arial;
                background: #f1f2f6;
                color: #333;
            }}

            header {{
                background: #6A0DAD;
                color: white;
                padding: 25px;
                text-align: center;
                font-size: 30px;
                font-weight: bold;
            }}

            nav {{
                background: #4B0082;
                padding: 15px;
                text-align: center;
            }}

            nav a {{
                color: white;
                text-decoration: none;
                margin: 10px;
                font-weight: bold;
            }}

            .contenedor {{
                width: 95%;
                max-width: 1200px;
                margin: 25px auto;
            }}

            .panel {{
                background: white;
                padding: 20px;
                margin-bottom: 25px;
                border-radius: 10px;
                box-shadow: 0 2px 8px #ccc;
                overflow-x: auto;
            }}

            h2 {{ color: #6A0DAD; }}

            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}

            th {{
                background: #6A0DAD;
                color: white;
                padding: 12px;
            }}

            td {{
                padding: 11px;
                border-bottom: 1px solid #ddd;
            }}

            tr:nth-child(even) {{
                background: #f5f5f5;
            }}

            .boton {{
                display: inline-block;
                padding: 9px 14px;
                border: none;
                border-radius: 6px;
                color: white;
                text-decoration: none;
                cursor: pointer;
                margin: 3px;
                font-size: 13px;
            }}

            .morado {{ background: #6A0DAD; }}
            .verde {{ background: #198754; }}
            .azul {{ background: #0d6efd; }}
            .rojo {{ background: #dc3545; }}

            input, select {{
                width: 100%;
                padding: 11px;
                margin: 8px 0 18px;
                border: 1px solid #ccc;
                border-radius: 6px;
            }}

            label {{ font-weight: bold; }}

            .aviso {{
                background: #d1e7dd;
                padding: 15px;
                margin-bottom: 20px;
                border-radius: 6px;
            }}

            .acciones {{ white-space: nowrap; }}

            footer {{
                text-align: center;
                padding: 20px;
                color: #666;
            }}
        </style>
    </head>

    <body>

        <header>📚 Biblioteca Digital</header>

        <nav>
            <a href="/">🏠 Inicio</a>
            <a href="/#categorias">Categorías</a>
            <a href="/#libros">Libros</a>
            <a href="/#usuarios">Usuarios</a>
            <a href="/#reservas">Reservas</a>
        </nav>

        <div class="contenedor">
            {aviso}
            {contenido}
        </div>

        <footer>Biblioteca Digital - Sistema de Gestión</footer>

    </body>
    </html>
    """


def boton_nuevo(tipo):
    return f'<a class="boton verde" href="/nuevo/{tipo}">➕ Agregar</a>'


def tabla(tipo, filas, columnas):

    config = TABLAS[tipo]

    resultado = f"""
    <div class="panel" id="{tipo}">
        <h2>{config["titulo"]}</h2>
        {boton_nuevo(tipo)}

        <table>
        <tr>
    """

    for columna, etiqueta in columnas:
        resultado += f"<th>{etiqueta}</th>"

    resultado += "<th>Acciones</th></tr>"

    for fila in filas:

        resultado += "<tr>"

        for columna, etiqueta in columnas:
            valor = escape(str(fila.get(columna, "")))
            resultado += f"<td>{valor}</td>"

        identificador = fila[config["pk"]]

        resultado += f"""
        <td class="acciones">

            <a class="boton azul"
               href="/editar/{tipo}/{identificador}">
               ✏️ Editar
            </a>

            <form method="post"
                  action="/eliminar/{tipo}/{identificador}"
                  style="display:inline"
                  onsubmit="return confirm('¿Deseas eliminar este registro?')">

                <button class="boton rojo" type="submit">
                    🗑️ Eliminar
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

    contenido = ""

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
    <div class="panel">

        <h2>{titulo} {config["titulo"]}</h2>

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
            <button class="boton verde" type="submit">
                💾 Guardar
            </button>

            <a class="boton rojo" href="/">
                Cancelar
            </a>

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
            f"Error al guardar: {escape(str(e))}<br><a href='/'>Volver</a>",
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
            f"Error al actualizar: {escape(str(e))}<br><a href='/'>Volver</a>",
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
                        pagina(
                            f"""
                            <div class="panel">
                                <h2>⚠️ No se puede eliminar</h2>
                                <p>Esta categoría tiene {cantidad} libro(s) asociado(s).</p>
                                <a class="boton morado" href="/">Volver</a>
                            </div>
                            """
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
                        pagina(
                            f"""
                            <div class="panel">
                                <h2>⚠️ No se puede eliminar</h2>
                                <p>Este usuario tiene {cantidad} reserva(s).</p>
                                <a class="boton morado" href="/">Volver</a>
                            </div>
                            """
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
                        pagina(
                            f"""
                            <div class="panel">
                                <h2>⚠️ No se puede eliminar</h2>
                                <p>Este libro tiene {cantidad} reserva(s).</p>
                                <a class="boton morado" href="/">Volver</a>
                            </div>
                            """
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
            pagina(
                f"""
                <div class="panel">
                    <h2>Error al eliminar</h2>
                    <p>{escape(str(e))}</p>
                    <a class="boton morado" href="/">Volver</a>
                </div>
                """
            ),
            status_code=400
        )


@app.get("/prueba-db")
def prueba_db():

    with conexion.connect():
        return {"mensaje": "Conexion exitosa a MySQL"}
