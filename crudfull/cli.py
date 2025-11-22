import typer
from . import __version__
from jinja2 import Environment, FileSystemLoader
import os
import inflect


# ===========================
# LOGO
# ===========================
def show_logo():
    logo = r"""
        🚀   CRUD-FULL — 
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


# ---------------------------
# Helpers Docker-compose (.dev) non-invasive
# ---------------------------
def ensure_env_file(env_path: str, vars: dict):
    """Crea o actualiza .env añadiendo variables que falten (no sobrescribe las existentes)."""
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            content = f.read()
        appended = False
        with open(env_path, "a") as f:
            for k, v in vars.items():
                if k not in content:
                    f.write(f"{k}={v}\n")
                    appended = True
        if appended:
            typer.echo(f"🔧 Actualizadas variables en {env_path}")
        else:
            typer.echo(f"ℹ️  {env_path} ya contenía las variables necesarias")
    else:
        with open(env_path, "w") as f:
            for k, v in vars.items():
                f.write(f"{k}={v}\n")
        typer.echo(f"🆕 {env_path} creado")


def ensure_compose_has_service(compose_path: str, service_key: str, service_block: str, volumes: list[str]):
    """Añade un bloque de servicio al compose (no invasivo). Si el servicio existe, no hace nada.
    Si no existe compose, lo crea con versión 3.8 y el servicio.
    """
    if os.path.exists(compose_path):
        with open(compose_path, "r") as f:
            content = f.read()

        if service_key in content:
            typer.echo(f"ℹ️  El servicio '{service_key}' ya existe en {compose_path}")
            # asegurar volúmenes
            for v in volumes:
                if v not in content:
                    # si existe 'volumes:' lo añadimos al final
                    if "\nvolumes:" in content:
                        content = content + f"\n{v}:\n"
                    else:
                        content = content + f"\nvolumes:\n  {v}:\n"
            with open(compose_path, "w") as f:
                f.write(content)
            return

        # Servicio no está presente: lo agregamos justo antes del bloque 'volumes:' si existe, sino al final
        if "\nvolumes:" in content:
            parts = content.split("\nvolumes:")
            new_content = parts[0].rstrip() + "\n\n" + service_block + "\n\nvolumes:" + parts[1]
        else:
            new_content = content.rstrip() + "\n\n" + service_block + "\n\nvolumes:\n"

        # asegurar volúmenes listados
        for v in volumes:
            if v not in new_content:
                new_content = new_content + f"  {v}:\n"

        with open(compose_path, "w") as f:
            f.write(new_content)

        typer.echo(f"✅ Servicio '{service_key}' añadido a {compose_path}")
    else:
        # crear nuevo compose con el servicio
        base = "version: '3.8'\nservices:\n"
        content = base + service_block + "\nvolumes:\n"
        for v in volumes:
            content += f"  {v}:\n"
        with open(compose_path, "w") as f:
            f.write(content)
        typer.echo(f"🆕 {compose_path} creado con el servicio '{service_key}'")


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
    docker: bool = typer.Option(False, "--docker", help="Crear docker-compose.yml y .env (solo para --db mongo)"),
    force: bool = typer.Option(False, "--force", "-f", help="Forzar sobrescritura si el recurso ya existe"),
):
    typer.echo(f"🔥 Generando RESOURCE: {name} con motor: {db}")

    # ---- Comprobación no invasiva de dependencias ----
    missing = []
    if db == "mongo":
        try:
            import beanie  # noqa: F401
            import motor  # noqa: F401
        except Exception:
            missing = ["beanie", "motor"]
    elif db == "sql":
        try:
            import sqlalchemy  # noqa: F401
            import asyncpg  # noqa: F401
        except Exception:
            missing = ["sqlalchemy", "asyncpg"]

    if missing:
        typer.secho("\n⚠️  Dependencias faltantes detectadas:", fg="yellow")
        typer.secho(f"  Para --db {db} faltan: {', '.join(missing)}\n", fg="yellow")
        typer.echo("Opciones para instalarlas:")
        # sugerencias pip y poetry
        if db == "mongo":
            typer.echo("  pip:\n    pip install motor beanie")
            typer.echo("  o (si usas extras del paquete):\n    pip install 'crudfull[mongo]'")
            typer.echo("  poetry:\n    poetry add motor beanie")
        elif db == "sql":
            typer.echo("  pip:\n    pip install sqlalchemy asyncpg")
            typer.echo("  o (si usas extras del paquete):\n    pip install 'crudfull[sql]'")
            typer.echo("  poetry:\n    poetry add sqlalchemy asyncpg")

        typer.echo("\nNota: No se instalarán paquetes automáticamente. Instálalos manualmente o activa un entorno adecuado (venv/poetry).\n")

    parsed_fields = {}
    has_optional = False
    has_datetime = False
    has_uuid = False

    for field in fields:
        if ":" not in field:
            typer.echo(f"❌ Error en campo '{field}'. Formato válido: nombre:tipo")
            raise typer.Exit(code=1)
        
        fname, ftype = field.split(":", 1)
        is_optional = False
        
        if ftype.endswith("?"):
            ftype = ftype[:-1]
            is_optional = True
            has_optional = True
        
        if ftype == "datetime":
            has_datetime = True
        if ftype == "uuid":
            has_uuid = True

        parsed_fields[fname] = {
            "type": ftype,
            "optional": is_optional
        }

    model_name = name
    model_file = name.lower()
    
    # Smart pluralization
    p = inflect.engine()
    resource = p.plural(model_file)
    
    singular = model_file

    context = {
        "model_name": model_name,
        "model_file": model_file,
        "fields": parsed_fields,
        "resource": resource,
        "singular": singular,
        "docker": docker,
        "has_optional": has_optional,
        "has_datetime": has_datetime,
        "has_uuid": has_uuid,
    }

    # --------------------------
    # PROTECCIÓN: evitar sobrescribir recursos existentes
    # --------------------------
    conflicts = []
    models_path = os.path.join(os.getcwd(), "models", f"{model_file}.py")
    routers_path = os.path.join(os.getcwd(), "routers", f"{model_file}_router.py")
    services_dir = os.path.join(os.getcwd(), "services")

    if os.path.exists(models_path):
        conflicts.append(models_path)
    if os.path.exists(routers_path):
        conflicts.append(routers_path)

    # comprobar cualquier servicio existente que comience con el prefijo del recurso
    if os.path.exists(services_dir):
        for fname in os.listdir(services_dir):
            if fname.startswith(f"{model_file}_service_"):
                conflicts.append(os.path.join(services_dir, fname))

    if conflicts and not force:
        typer.secho("\n❌ Error: Ya existen archivos para este recurso:\n", fg="red")
        for c in conflicts:
            typer.echo(f"  - {c}")
        typer.echo("\nSi quieres sobrescribirlos usa el flag `--force` o elimina manualmente los archivos existentes.")
        raise typer.Exit(code=1)
    elif conflicts and force:
        typer.secho("⚠️  Advertencia: se sobrescribirán los siguientes archivos:\n", fg="yellow")
        for c in conflicts:
            typer.echo(f"  - {c}")
        typer.echo("")

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
        
        # Generate create_tables script
        script_content = render_template("sql/create_tables.jinja2", context)
        write_file("scripts", "create_tables.py", script_content)

    if db == "mongo":
        example = render_template("mongo/database_mongo_example.jinja2", context)
        write_file("database_examples", "database_mongo_example.py", example)

    # --------------------------
    # GENERATE TESTS (Unified)
    # --------------------------
    conftest_tpl = {
        "sql": "sql/conftest.jinja2",
        "mongo": "mongo/conftest.jinja2",
        "ghost": "ghost/conftest.jinja2"
    }.get(db)

    test_tpl = {
        "sql": "sql/test_resource.jinja2",
        "mongo": "mongo/test_resource.jinja2",
        "ghost": "ghost/test_resource.jinja2"
    }.get(db)

    if conftest_tpl and not os.path.exists(os.path.join(os.getcwd(), "tests", "conftest.py")):
        conftest = render_template(conftest_tpl, context)
        write_file("tests", "conftest.py", conftest)

    if test_tpl:
        test_file = render_template(test_tpl, context)
        write_file("tests", f"test_{model_file}.py", test_file)
        
        typer.echo("\n🧪 Tests generados en tests/")
        typer.echo("   Para ejecutarlos, instala las dependencias de test:")
        typer.echo("   pip install 'crudfull[test]'")
        typer.echo("   Luego corre: pytest\n")

    # Si se pidió docker, generar/actualizar docker-compose de forma no invasiva
    if docker:
        compose_path = os.path.join(os.getcwd(), "docker-compose.dev.yml")
        env_path = os.path.join(os.getcwd(), ".env")

        if db == "mongo":
            typer.echo("📦 Asegurando servicio Mongo en docker-compose.dev.yml y variables en .env...")
            mongo_service = (
                "  mongo:\n"
                "    image: mongo:6.0\n"
                "    container_name: crudfull_mongo\n"
                "    ports:\n"
                "      - \"${MONGO_PORT}:27017\"\n"
                "    environment:\n"
                "      - MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME}\n"
                "      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD}\n"
                "      - MONGO_INITDB_DATABASE=${MONGO_DATABASE}\n"
                "    volumes:\n"
                "      - mongo_data:/data/db\n"
            )

            env_vars = {
                "MONGO_INITDB_ROOT_USERNAME": "crudfull_user",
                "MONGO_INITDB_ROOT_PASSWORD": "changeme",
                "MONGO_DATABASE": "mydb",
                "MONGO_HOST": "mongo",
                "MONGO_PORT": "27017",
            }

            ensure_compose_has_service(compose_path, "mongo:", mongo_service, ["mongo_data"])
            ensure_env_file(env_path, env_vars)

        if db == "sql":
            typer.echo("📦 Asegurando servicio Postgres en docker-compose.dev.yml y variables en .env...")
            pg_service = (
                "  postgres:\n"
                "    image: postgres:15\n"
                "    container_name: crudfull_postgres\n"
                "    ports:\n"
                "      - \"${POSTGRES_PORT}:5432\"\n"
                "    environment:\n"
                "      - POSTGRES_USER=${POSTGRES_USER}\n"
                "      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}\n"
                "      - POSTGRES_DB=${POSTGRES_DB}\n"
                "    volumes:\n"
                "      - postgres_data:/var/lib/postgresql/data\n"
            )

            env_vars = {
                "POSTGRES_USER": "crudfull_user",
                "POSTGRES_PASSWORD": "changeme",
                "POSTGRES_DB": "crudfulldb",
                "POSTGRES_HOST": "postgres",
                "POSTGRES_PORT": "5432",
            }

            ensure_compose_has_service(compose_path, "postgres:", pg_service, ["postgres_data"])
            ensure_env_file(env_path, env_vars)

    
    # --------------------------
    # AUTO-INTEGRAR EN main.py
    # --------------------------
    integrate_router_into_main(model_file)
    
    # --------------------------
    # Si es SQL, aseguramos que main.py inicialice las tablas en startup
    # --------------------------
    if db == "sql":
        main_path = find_or_create_main()

        with open(main_path, "r") as f:
            content = f.read()

        # 1) importar create_tables si no existe
        # (Opcional: ya no forzamos esto, el usuario usa el script)
        pass
    

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

