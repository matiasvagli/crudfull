import typer
from . import __version__
from jinja2 import Environment, FileSystemLoader
import os


# ===========================
# LOGO
# ===========================
def show_logo():
    logo = r"""
   ____ ____  _   _ ____  _____ _   _ _      
  / ___/ ___|| | | |  _ \|  ___| | | | |     
 | |   \___ \| | | | |_) | |_  | | | | |     
 | |___ ___) | |_| |  _ <|  _| | |_| | |___  
  \____|____/ \___/|_| \_\_|    \___/|_____|
  
            🚀  CRUDFULL ENGINE  
        Modes: ghost | sql | mongo
"""
    typer.echo(logo)


# ===========================
# APP ROOT
# ===========================
app = typer.Typer(
    help="crudfull - generador de CRUDs para FastAPI",
    no_args_is_help=True,
)

generate_app = typer.Typer(help="Generador de recursos.")
app.add_typer(generate_app, name="generate")

version_app = typer.Typer(help="Versión de la librería.")
app.add_typer(version_app, name="version")
sync_app = typer.Typer(help="Sincroniza todos los routers existentes con main.py")
app.add_typer(sync_app, name="sync-routers")



# ===========================
# CALLBACK PARA MOSTRAR LOGO
# ===========================
@app.callback()
def main_callback():
    """Muestra el logo al inicio de cualquier comando."""
    show_logo()


# ===========================
# HELPERS
# ===========================
def write_file(folder: str, file_name: str, content: str):
    output_dir = os.path.join(os.getcwd(), folder)
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, file_name)

    with open(file_path, "w") as f:
        f.write(content)

    typer.echo(f"📝 Archivo generado: {file_path}")


def render_template(path: str, context: dict) -> str:
    base_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_dir = os.path.join(base_dir, os.path.dirname(path))
    file_name = os.path.basename(path)

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(file_name)
    return template.render(context)


# ===========================
# VERSION
# ===========================
@version_app.command("show")
def show_version():
    typer.echo(f"crudfull v{__version__}")


# ===========================
# GENERATE RESOURCE
# ===========================
@generate_app.command("resource")
def generate_resource(
    name: str = typer.Argument(..., help="Nombre del modelo"),
    fields: list[str] = typer.Argument(..., help="Campos en formato nombre:tipo"),
    db: str = typer.Option("ghost", "--db", help="ghost | sql | mongo"),
):
    typer.echo(f"🔥 Generando RESOURCE: {name} con motor: {db}")

    parsed_fields = {}
    for field in fields:
        if ":" not in field:
            typer.echo(f"❌ Error en campo '{field}'. Formato válido: nombre:tipo")
            raise typer.Exit(code=1)
        fname, ftype = field.split(":", 1)
        parsed_fields[fname] = ftype

    model_name = name
    model_file = name.lower()
    resource = model_file + "s"
    singular = model_file

    context = {
        "model_name": model_name,
        "model_file": model_file,
        "fields": parsed_fields,
        "resource": resource,
        "singular": singular,
    }

    # MODEL
    model_tpl = {
        "ghost": "ghost/model.jinja2",
        "sql": "sql/model_sql.jinja2",
        "mongo": "mongo/model_mongo.jinja2",
    }[db]

    model_code = render_template(model_tpl, context)
    write_file("models", f"{model_file}.py", model_code)

    # SERVICE
    service_tpl = {
        "ghost": "ghost/service.jinja2",
        "sql": "sql/service_sql.jinja2",
        "mongo": "mongo/service_mongo.jinja2",
    }[db]

    service_filename = f"{model_file}_service_{db}.py"
    service_code = render_template(service_tpl, context)
    write_file("services", service_filename, service_code)

    # ROUTER
    router_tpl = {
        "ghost": "ghost/router.jinja2",
        "sql": "sql/router_sql.jinja2",
        "mongo": "mongo/router_mongo.jinja2",
    }[db]

    router_code = render_template(router_tpl, context)
    write_file("routers", f"{model_file}_router.py", router_code)

    # DB EXAMPLES
    if db == "sql":
        example = render_template("sql/database_sql_example.jinja2", context)
        write_file("database_examples", "database_sql_example.py", example)

    if db == "mongo":
        example = render_template("mongo/database_mongo_example.jinja2", context)
        write_file("database_examples", "database_mongo_example.py", example)

    
    # --------------------------
    # AUTO-INTEGRAR EN main.py
    # --------------------------
    integrate_router_into_main(model_file)
    

    typer.echo("🚀 CRUD generado con éxito!")
    typer.echo("🔥 Listo para usar en FastAPI")


# =====================================================================
# AUTO-INTEGRACIÓN DEL ROUTER EN main.py
# =====================================================================

MAIN_CANDIDATES = [
    "main.py",
    os.path.join("app", "main.py"),
    os.path.join("src", "main.py"),
    os.path.join("api", "main.py"),
]


def find_or_create_main():
    """
    Busca un main.py en ubicaciones comunes.
    Si no existe, crea uno nuevo en ./main.py.
    """
    for path in MAIN_CANDIDATES:
        if os.path.exists(path):
            return path

    # Ninguno existe — creamos main.py en raíz
    default_main = "main.py"
    with open(default_main, "w") as f:
        f.write(
            "from fastapi import FastAPI\n\n"
            "app = FastAPI()\n"
        )
    typer.echo("🆕 No se encontró main.py — creado automáticamente en ./main.py")
    return default_main


def integrate_router_into_main(model_file: str):
    """
    Inserta automáticamente el import y app.include_router()
    en el main.py correspondiente.
    """
    main_path = find_or_create_main()

    with open(main_path, "r") as f:
        content = f.read()

    import_line = f"from routers.{model_file}_router import router as {model_file}_router  # agregado por CRUDfull"
    include_line = f"app.include_router({model_file}_router)  # agregado por CRUDfull"

    # ===========================
    # 1. Agregar import SI NO EXISTE
    # ===========================
    if import_line not in content:
        # insertar el import debajo de los primeros imports
        lines = content.splitlines()
        insert_idx = 0

        # buscar la última importación
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                insert_idx = i + 1

        lines.insert(insert_idx, import_line)
        content = "\n".join(lines)

    # ===========================
    # 2. Agregar include_router SI NO EXISTE
    # ===========================
    if include_line not in content:
        # buscamos la línea donde está "app = FastAPI"
        lines = content.splitlines()
        insert_idx = None

        for i, line in enumerate(lines):
            if "app = FastAPI" in line.replace(" ", ""):
                insert_idx = i + 1
                break

        if insert_idx is None:
            # si no lo encuentra, lo agregamos al final
            lines.append(include_line)
        else:
            lines.insert(insert_idx, include_line)

        content = "\n".join(lines)

    # ===========================
    # 3. Guardar cambios
    # ===========================
    with open(main_path, "w") as f:
        f.write(content)

    typer.echo(f"🔌 main.py actualizado automáticamente con el router: {model_file}_router")

    # ===========================
    # 4. Agregar endpoint raíz si falta
    # ===========================
    with open(main_path, "r") as f:
        content = f.read()

    if 'def root(' not in content and '@app.get("/")' not in content:
        root_endpoint = (
            '@app.get("/")\n'
            "def root():\n"
            '    return {"message": "🚀 CRUDfull FastAPI ready!"}\n'
        )
        with open(main_path, "a") as f:
            f.write("\n\n" + root_endpoint)

        typer.echo("🌟 Endpoint raíz agregado automáticamente: GET /")

def find_all_routers():
    """
    Detecta todos los archivos *_router.py en la carpeta routers/.
    Devuelve una lista como: ["user", "product", "order"]
    """
    routers_dir = os.path.join(os.getcwd(), "routers")
    router_files = []

    if not os.path.exists(routers_dir):
        return []

    for filename in os.listdir(routers_dir):
        if filename.endswith("_router.py"):
            name = filename.replace("_router.py", "")
            router_files.append(name)

    return router_files
@sync_app.command("run")
def sync_routers():
    """
    Escanea todos los routers existentes y los monta en main.py automáticamente.
    Ideal si agregaste routers manuales o tu main se desincronizó.
    """

    typer.echo("🔎 Buscando routers en ./routers/...")

    router_names = find_all_routers()

    if not router_names:
        typer.echo("❌ No se encontraron routers en la carpeta 'routers/'.")
        raise typer.Exit()

    typer.echo(f"📡 Routers detectados: {', '.join(router_names)}")

    main_path = find_or_create_main()

    with open(main_path, "r") as f:
        content = f.read()

    lines = content.splitlines()

    modified = False

    for name in router_names:
        import_line = f"from routers.{name}_router import router as {name}_router  # agregado por CRUDfull"
        include_line = f"app.include_router({name}_router)  # agregado por CRUDfull"

        # ----------------------------
        # IMPORT
        # ----------------------------
        if import_line not in content:
            # insertar bajo los imports existentes
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    insert_idx = i + 1
            lines.insert(insert_idx, import_line)
            modified = True

        # ----------------------------
        # INCLUDE ROUTER
        # ----------------------------
        if include_line not in content:
            inserted = False
            for i, line in enumerate(lines):
                if "app = FastAPI" in line.replace(" ", ""):
                    lines.insert(i + 1, include_line)
                    inserted = True
                    break

            if not inserted:
                lines.append(include_line)

            modified = True

    if modified:
        typer.echo("🔧 Actualizando main.py ...")
        with open(main_path, "w") as f:
            f.write("\n".join(lines))

        typer.echo("🚀 main.py sincronizado con todos los routers!")
    else:
        typer.echo("✨ Todo estaba sincronizado. No hubo cambios.")



# ===========================
# ENTRYPOINT
# ===========================
def main():
    app()

