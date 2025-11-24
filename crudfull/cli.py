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

generate_app = typer.Typer(help="Generar recursos CRUD")
app.add_typer(generate_app, name="generate")

add_app = typer.Typer(help="Agregar funcionalidades al proyecto")
app.add_typer(add_app, name="add")

version_app = typer.Typer(help="Ver versión de crudfull")
app.add_typer(version_app, name="version")

sync_app = typer.Typer(help="Sincronizar routers en main.py")
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
# ADD AUTH
# ===========================
@add_app.command("auth")
def add_auth(
    auth_type: str = typer.Option("jwt", "--type", help="jwt | oauth2 | session"),
):
    """
    Agrega autenticación al proyecto actual.
    """
    typer.echo(f"🔐 Agregando autenticación ({auth_type}) al proyecto...")
    
    # Check if we're in a crudfull project
    config_path = os.path.join(os.getcwd(), "crudfull.json")
    if not os.path.exists(config_path):
        typer.echo("❌ No se encontró crudfull.json. ¿Estás en un proyecto crudfull?")
        typer.echo("💡 Tip: Ejecutá 'crudfull new mi_proyecto' primero")
        raise typer.Exit(code=1)
    
    # Read project config
    import json
    with open(config_path, "r") as f:
        config = json.load(f)
    
    db = config.get("db", "sql")
    
    context = {
        "db": db,
        "auth_type": auth_type
    }
    
    # Create auth module directory
    auth_dir = os.path.join("app", "auth")
    os.makedirs(auth_dir, exist_ok=True)
    write_file(auth_dir, "__init__.py", "")
    
    # Create core directory for security config
    core_dir = os.path.join("app", "core")
    os.makedirs(core_dir, exist_ok=True)
    write_file(core_dir, "__init__.py", "")
    
    # Generate auth files
    schemas_content = render_template("auth/schemas.jinja2", context)
    write_file(auth_dir, "schemas.py", schemas_content)
    
    models_content = render_template("auth/models.jinja2", context)
    write_file(auth_dir, "models.py", models_content)
    
    service_content = render_template("auth/service.jinja2", context)
    write_file(auth_dir, "service.py", service_content)
    
    router_content = render_template("auth/router.jinja2", context)
    write_file(auth_dir, "router.py", router_content)
    
    dependencies_content = render_template("auth/dependencies.jinja2", context)
    write_file(auth_dir, "dependencies.py", dependencies_content)
    
    security_content = render_template("auth/security.jinja2", context)
    write_file(core_dir, "security.py", security_content)
    
    # Auto-register router in main.py
    main_path = os.path.join("app", "main.py")
    if os.path.exists(main_path):
        with open(main_path, "r") as f:
            main_content = f.read()
        
        import_line = "from app.auth.router import router as auth_router"
        include_line = "app.include_router(auth_router)"
        
        # Add import if not present
        if import_line not in main_content:
            # Find the last import line
            lines = main_content.split("\n")
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    import_idx = i + 1
            lines.insert(import_idx, import_line)
            main_content = "\n".join(lines)
        
        # Add include_router if not present
        if include_line not in main_content:
            # Find where to insert (after app = FastAPI(...))
            lines = main_content.split("\n")
            for i, line in enumerate(lines):
                if "app = FastAPI" in line:
                    # Find the closing parenthesis
                    j = i
                    while j < len(lines) and ")" not in lines[j]:
                        j += 1
                    lines.insert(j + 1, f"\n{include_line}")
                    break
            main_content = "\n".join(lines)
        
        with open(main_path, "w") as f:
            f.write(main_content)
        
        typer.echo(f"✅ Router 'auth' registrado automáticamente en main.py")

    typer.echo("\n✅ Módulo de autenticación generado exitosamente!")
    typer.echo(f"📂 app/auth/ - Módulo de autenticación")
    typer.echo(f"📂 app/core/security.py - Configuración JWT")
    typer.echo("\n📝 Próximos pasos:")
    typer.echo("1. Instalar dependencias: pip install 'crudfull[auth]'")
    typer.echo("2. Proteger rutas con:")
    typer.echo("   from app.auth.dependencies import get_current_user")
    typer.echo("   @router.get('/protected')")
    typer.echo("   async def protected(user = Depends(get_current_user)):")


# ===========================
# NEW PROJECT
# ===========================
@app.command("new")
def new_project(
    name: str = typer.Argument(..., help="Nombre del proyecto"),
    db: str = typer.Option("sql", "--db", help="ghost | sql | mongo"),
    docker: bool = typer.Option(False, "--docker", help="Incluir Dockerfile y docker-compose.yml"),
):
    """
    Crea un nuevo proyecto FastAPI con la arquitectura modular recomendada.
    """
    typer.echo(f"✨ Creando nuevo proyecto: {name} (DB: {db})")

    project_dir = os.path.join(os.getcwd(), name)
    if os.path.exists(project_dir):
        typer.echo(f"❌ El directorio {name} ya existe.")
        raise typer.Exit(code=1)

    # Create directories
    os.makedirs(project_dir)
    os.makedirs(os.path.join(project_dir, "app"))
    os.makedirs(os.path.join(project_dir, "app", "db"))
    os.makedirs(os.path.join(project_dir, "tests"))

    context = {
        "project_name": name,
        "db": db
    }

    # Render and write files
    # 0. Root __init__.py (to make app importable)
    write_file(name, "__init__.py", "")
    
    # 1. main.py
    main_content = render_template("project/main.jinja2", context)
    write_file(os.path.join(name, "app"), "main.py", main_content)
    write_file(os.path.join(name, "app"), "__init__.py", "")

    # 2. Database setup
    if db == "sql":
        db_content = render_template("project/database_sql.jinja2", context)
        write_file(os.path.join(name, "app", "db"), "session.py", db_content)
        write_file(os.path.join(name, "app", "db"), "__init__.py", "")
    elif db == "mongo":
        db_content = render_template("project/database_mongo.jinja2", context)
        write_file(os.path.join(name, "app", "db"), "session.py", db_content)
        write_file(os.path.join(name, "app", "db"), "__init__.py", "")
    
    # 3.1 Test configuration (conftest.py)
    conftest_content = render_template("project/conftest.jinja2", context)
    write_file(os.path.join(name, "tests"), "conftest.py", conftest_content)
    write_file(os.path.join(name, "tests"), "__init__.py", "")

    # 3. Requirements
    req_content = render_template("project/requirements.jinja2", context)
    write_file(name, "requirements.txt", req_content)

    # 4. Gitignore
    git_content = render_template("project/gitignore.jinja2", context)
    write_file(name, ".gitignore", git_content)

    # 5. Docker files (optional)
    if docker:
        docker_compose_content = render_template("project/docker_compose.jinja2", context)
        write_file(name, "docker-compose.yml", docker_compose_content)
        
        dockerfile_content = render_template("project/dockerfile.jinja2", context)
        write_file(name, "Dockerfile", dockerfile_content)
        
        env_content = render_template("project/env.jinja2", context)
        write_file(name, ".env", env_content)
    
    # 5.1 Docker Dev files (always generated for SQL/Mongo)
    if db != 'ghost':
        docker_compose_dev_content = render_template("project/docker_compose_dev.jinja2", context)
        write_file(name, "docker-compose.dev.yml", docker_compose_dev_content)
        
        env_dev_content = render_template("project/env_dev.jinja2", context)
        write_file(name, ".env.dev", env_dev_content)

    # 6. Copy static assets (logos, CSS, etc.)
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_source = os.path.join(templates_dir, "project", "static")
    if os.path.exists(static_source):
        import shutil
        static_dest = os.path.join(name, "static")
        shutil.copytree(static_source, static_dest)
        typer.echo(f"📁 Static assets copied to {static_dest}/")

    typer.echo(f"\n🚀 Proyecto {name} creado exitosamente!")
    typer.echo(f"📂 cd {name}")
    if docker:
        typer.echo("\n🐳 Modo Producción:")
        typer.echo("   docker-compose up -d --build")
    if db != 'ghost':
        typer.echo("\n🔧 Modo Desarrollo (solo DB):")
        typer.echo("   docker-compose -f docker-compose.dev.yml up -d")
        typer.echo("   pip install -r requirements.txt")
        typer.echo("   uvicorn app.main:app --reload")
    if not docker and db == 'ghost':
        typer.echo("📦 pip install -r requirements.txt")
        typer.echo("▶️  uvicorn app.main:app --reload")
    
    # 6. Create crudfull.json config
    config = {
        "project_name": name,
        "db": db
    }
    import json
    with open(os.path.join(name, "crudfull.json"), "w") as f:
        json.dump(config, f, indent=2)


# ===========================
# VERSION
# ===========================
@version_app.command("show")
def show_version():
    typer.echo(f"crudfull v{__version__}")


# ===========================
# GENERATE RESOURCE (MODULAR DEFAULT)
# ===========================
@generate_app.command("resource")
def generate_resource(
    name: str = typer.Argument(..., help="Nombre del recurso (plural, ej: users)"),
    fields: list[str] = typer.Argument(..., help="Campos en formato nombre:tipo"),
    db: str = typer.Option(None, "--db", help="ghost | sql | mongo"),
    force: bool = typer.Option(False, "--force", "-f", help="Forzar sobrescritura"),
):
    # Try to load config
    config_path = os.path.join(os.getcwd(), "crudfull.json")
    if db is None and os.path.exists(config_path):
        import json
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
                db = config.get("db")
                typer.echo(f"⚙️  Usando configuración del proyecto: DB={db}")
        except Exception:
            pass
    
    if db is None:
        db = "sql" # Default fallback

    typer.echo(f"📦 Generando RECURSO (Modular): {name} con motor: {db}")

    # Parse fields (reuse logic or extract to helper)
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

    model_name = name.capitalize()
    # Remove 's' for singular if possible, very naive pluralization fix
    if model_name.endswith("s"):
        singular = model_name[:-1]
    else:
        singular = model_name
    
    resource = name.lower()

    context = {
        "model_name": singular, # Class name (User)
        "resource": resource,   # URL prefix (users)
        "singular": singular.lower(), # var name (user)
        "fields": parsed_fields,
        "has_optional": has_optional,
        "has_datetime": has_datetime,
        "has_uuid": has_uuid,
    }

    # Directory Structure
    base_path = os.path.join(os.getcwd(), "app", resource)
    os.makedirs(base_path, exist_ok=True)
    
    # Create __init__.py
    write_file(os.path.join("app", resource), "__init__.py", "")

    # Define templates based on DB
    if db == "sql":
        files = {
            "schemas.py": "sql/schemas.jinja2",
            "models.py": "sql/models.jinja2",
            "service.py": "sql/service.jinja2",
            "router.py": "sql/router.jinja2",
        }
    elif db == "mongo":
        files = {
            "schemas.py": "mongo/schemas.jinja2",
            "models.py": "mongo/models.jinja2",
            "service.py": "mongo/service.jinja2",
            "router.py": "mongo/router.jinja2",
        }
    elif db == "ghost":
        files = {
            "schemas.py": "ghost/schemas.jinja2",
            "service.py": "ghost/service.jinja2",
            "router.py": "ghost/router.jinja2",
        }
    else:
        typer.echo(f"❌ Motor {db} no soportado.")
        raise typer.Exit(code=1)

    # Generate files
    for filename, tpl_path in files.items():
        content = render_template(tpl_path, context)
        write_file(os.path.join("app", resource), filename, content)

    # Generate Test
    test_context = context.copy()
    test_context["db"] = db
    test_content = render_template("test_resource.jinja2", test_context)
    
    # Create tests/module_name directory
    test_dir = os.path.join("tests", resource)
    os.makedirs(test_dir, exist_ok=True)
    write_file(os.path.join("tests", resource), "__init__.py", "")
    write_file(os.path.join("tests", resource), f"test_{resource}.py", test_content)

    # Auto-register router in main.py
    main_path = os.path.join("app", "main.py")
    if os.path.exists(main_path):
        with open(main_path, "r") as f:
            main_content = f.read()
        
        import_line = f"from app.{resource}.router import router as {resource}_router"
        include_line = f"app.include_router({resource}_router)"
        
        # Add import if not present
        if import_line not in main_content:
            # Find the last import line
            lines = main_content.split("\n")
            import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("from ") or line.startswith("import "):
                    import_idx = i + 1
            lines.insert(import_idx, import_line)
            main_content = "\n".join(lines)
        
        # Add include_router if not present
        if include_line not in main_content:
            # Find where to insert (after app = FastAPI(...))
            lines = main_content.split("\n")
            for i, line in enumerate(lines):
                if "app = FastAPI" in line:
                    # Find the closing parenthesis
                    j = i
                    while j < len(lines) and ")" not in lines[j]:
                        j += 1
                    lines.insert(j + 1, f"\n{include_line}")
                    break
            main_content = "\n".join(lines)
        
        with open(main_path, "w") as f:
            f.write(main_content)
        
        typer.echo(f"✅ Router '{resource}' registrado automáticamente en main.py")

    typer.echo(f"\n🎉 Recurso '{name}' generado exitosamente!")
    typer.echo(f"📂 app/{resource}/ - Módulo completo")
    typer.echo(f"📂 tests/{resource}/ - Tests")
    typer.echo(f"📚 Docs: http://localhost:8000/docs")



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
    Detecta todos los routers:
    1. routers/*_router.py (Legacy/Flat)
    2. app/*/router.py (Modular)
    """
    import glob
    router_files = []

    # 1. Legacy routers/*_router.py
    routers_dir = os.path.join(os.getcwd(), "routers")
    if os.path.exists(routers_dir):
        for filename in os.listdir(routers_dir):
            if filename.endswith("_router.py"):
                name = filename.replace("_router.py", "")
                router_files.append({
                    "name": name,
                    "type": "legacy",
                    "module": f"routers.{name}_router"
                })
    
    # 2. Modular app/*/router.py
    pattern = os.path.join("app", "*", "router.py")
    for router_file in glob.glob(pattern):
        # Extraer el nombre del módulo (ej: app/users/router.py -> users)
        parts = router_file.split(os.sep)
        if len(parts) >= 2:
            module_name = parts[1]  # 'users' de app/users/router.py
            router_files.append({
                "name": module_name,
                "type": "modular", # Added type for consistency with original structure
                "module": f"app.{module_name}.router"
            })
    
    return router_files

@sync_app.command("run")
def sync_routers():
    """
    Escanea todos los routers existentes y los monta en main.py automáticamente.
    """

    typer.echo("🔎 Buscando routers...")

    routers = find_all_routers()

    if not routers:
        typer.echo("❌ No se encontraron routers.")
        raise typer.Exit()

    router_names = [r["name"] for r in routers]
    typer.echo(f"📡 Routers detectados: {', '.join(router_names)}")

    main_path = find_or_create_main()

    with open(main_path, "r") as f:
        content = f.read()

    lines = content.splitlines()
    modified = False

    for r in routers:
        name = r["name"]
        module_path = r["module"]
        
        import_line = f"from {module_path} import router as {name}_router  # agregado por CRUDfull"
        include_line = f"app.include_router({name}_router)  # agregado por CRUDfull"

        # ----------------------------
        # IMPORT
        # ----------------------------
        if import_line not in content:
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
# PROTECT ROUTES
# ===========================
# ===========================
# PROTECT ROUTES
# ===========================
@app.command("protect")
def protect(
    resource: str = typer.Argument(..., help="Nombre del recurso (ej: users)"),
    action: str = typer.Argument(None, help="Acción (list, create, read, update, delete) o 'all'"),
    func_name: str = typer.Option(None, "--func", help="Nombre específico de la función a proteger (ej: create_user)"),
):
    """
    Protege rutas de un recurso con autenticación (Depends(get_current_user)).
    Uso: 
      1. Por acción: crudfull protect <resource> <action|all>
      2. Por función: crudfull protect <resource> --func <nombre_funcion>
    """
    if not action and not func_name:
        typer.echo("❌ Debes especificar una acción o usar --func <nombre>")
        raise typer.Exit(code=1)

    # Locate router
    # Support both app/<resource>/router.py and routers/<resource>_router.py
    modular_path = os.path.join("app", resource, "router.py")
    legacy_path = os.path.join("routers", f"{resource}_router.py")
    
    if os.path.exists(modular_path):
        router_path = modular_path
    elif os.path.exists(legacy_path):
        router_path = legacy_path
    else:
        typer.echo(f"❌ No se encontró el router para '{resource}'")
        raise typer.Exit(code=1)

    with open(router_path, "r") as f:
        content = f.read()

    # 1. Add Imports
    modified_content = content
    
    if "from app.auth.dependencies import get_current_user" not in modified_content:
        # Insert after imports
        lines = modified_content.splitlines()
        last_import_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("from ") or line.startswith("import "):
                last_import_idx = i
        
        lines.insert(last_import_idx + 1, "from app.auth.dependencies import get_current_user")
        modified_content = "\n".join(lines)

    if "Depends" not in modified_content:
        # Try to append to fastapi import
        if "from fastapi import " in modified_content:
            modified_content = modified_content.replace("from fastapi import ", "from fastapi import Depends, ")
        else:
            # Fallback
            modified_content = "from fastapi import Depends\n" + modified_content

    lines = modified_content.splitlines()
    new_lines = []
    changes_made = False

    # ---------------------------
    # MODO 1: POR FUNCIÓN (--func)
    # ---------------------------
    if func_name:
        # Estrategia: Buscar la definición de la función y subir buscando el decorador
        target_def = f"def {func_name}("
        
        # Primero identificamos los índices de las líneas que queremos modificar
        lines_to_modify = set()
        
        for i, line in enumerate(lines):
            if target_def in line:
                # Encontramos la función, buscamos hacia arriba el decorador @router
                for j in range(i - 1, -1, -1):
                    prev_line = lines[j].strip()
                    if prev_line.startswith("@router.") or prev_line.startswith("@app."):
                        # Encontramos el decorador
                        lines_to_modify.add(j)
                        break
                    if prev_line == "" or prev_line.startswith("#"):
                        continue
                    # Si encontramos otra cosa que no sea decorador/comentario/vacío, paramos
                    if not prev_line.startswith("@"):
                        break
        
        if not lines_to_modify:
            typer.echo(f"⚠️  No se encontró la función '{func_name}' o su decorador en {router_path}")
        
        # Aplicamos cambios
        for i, line in enumerate(lines):
            if i in lines_to_modify:
                if "get_current_user" in line:
                    new_lines.append(line) # Ya protegido
                    continue
                
                if "dependencies=" in line:
                    typer.echo(f"⚠️  Saltando línea (ya tiene dependencies): {line.strip()}")
                    new_lines.append(line)
                    continue

                parts = line.rsplit(")", 1)
                if len(parts) >= 2:
                    line = parts[0] + ", dependencies=[Depends(get_current_user)])" + parts[1]
                    changes_made = True
            new_lines.append(line)

    # ---------------------------
    # MODO 2: POR ACCIÓN (action)
    # ---------------------------
    else:
        # Define targets
        targets = []
        if action == "all":
            targets = ["@router.get", "@router.post", "@router.put", "@router.patch", "@router.delete"]
        else:
            if action == "list": targets.append('@router.get("/",')
            elif action == "create": targets.append('@router.post("/",')
            elif action == "read": targets.append('@router.get("/{')
            elif action == "update": 
                targets.append('@router.patch("/{')
                targets.append('@router.put("/{')
            elif action == "delete": targets.append('@router.delete("/{')
            else:
                typer.echo(f"❌ Acción desconocida: {action}")
                raise typer.Exit(code=1)

        for line in lines:
            matched = False
            for t in targets:
                if t in line:
                    # Check if already protected
                    if "get_current_user" in line:
                        matched = True 
                        break
                    
                    if "dependencies=" in line:
                        typer.echo(f"⚠️  Saltando línea (ya tiene dependencies): {line.strip()}")
                        matched = True
                        break
                    else:
                        parts = line.rsplit(")", 1)
                        if len(parts) >= 2:
                            line = parts[0] + ", dependencies=[Depends(get_current_user)])" + parts[1]
                            changes_made = True
                            matched = True
                            break
            new_lines.append(line)

    if changes_made:
        with open(router_path, "w") as f:
            f.write("\n".join(new_lines))
        typer.echo(f"✅ Rutas protegidas en {router_path}")
    else:
        typer.echo("ℹ️  No se hicieron cambios (¿ya estaban protegidas?)")


# ===========================
# ENTRYPOINT
# ===========================
def main():
    app()

if __name__ == "__main__":
    main()

