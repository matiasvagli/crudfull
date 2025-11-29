import typer
from . import __version__
from jinja2 import Environment, FileSystemLoader
import os
import inflect

 # Colored terminal helpers
def success(msg: str):
    typer.echo(f"\033[1;32m{msg}\033[0m")

def warning(msg: str):
    typer.echo(f"\033[1;33m{msg}\033[0m")

def error(msg: str):
    typer.echo(f"\033[1;31m{msg}\033[0m")


# ===========================
# LOGO
# ===========================
def show_logo():
    logo = "CRUD-FULL — Modes: ghost | sql | mongo"
    typer.echo(logo)


# ===========================
# APP ROOT
# ===========================

app = typer.Typer(
    help="🚀 crudfull - FastAPI CRUD Generator with superpowers",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

generate_app = typer.Typer(
    help="📦 Generate CRUD resources (models, schemas, services, routers, tests)",
    no_args_is_help=True,
)
app.add_typer(generate_app, name="generate")
app.add_typer(generate_app, name="gen", hidden=True)  # Alias
app.add_typer(generate_app, name="g", hidden=True)    # Alias

add_app = typer.Typer(
    help="➕ Add features to your project (auth, middleware, etc.)",
    no_args_is_help=True,
)
app.add_typer(add_app, name="add")
app.add_typer(add_app, name="a", hidden=True)  # Alias

version_app = typer.Typer(
    help="ℹ️  Show crudfull version information",
    no_args_is_help=True,
)
app.add_typer(version_app, name="version")
app.add_typer(version_app, name="v", hidden=True)  # Alias

sync_app = typer.Typer(
    help="🔄 Sync routers in main.py automatically",
    no_args_is_help=True,
)
app.add_typer(sync_app, name="sync-routers")
app.add_typer(sync_app, name="sync", hidden=True)  # Alias



# ===========================
# CALLBACK TO SHOW LOGO
# ===========================
@app.callback()
def main_callback():
    """Show the logo at the start of any command."""
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

    success(f"File generated: {file_path}")


def render_template(path: str, context: dict) -> str:
    base_dir = os.path.join(os.path.dirname(__file__), "templates")
    template_dir = os.path.join(base_dir, os.path.dirname(path))
    file_name = os.path.basename(path)

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template(file_name)
    return template.render(context)


def add_router_to_main(router_name: str, module_path: str):
    """
    Add a router import and include to main.py, keeping imports grouped together.
    
    Args:
        router_name: Name of the router (e.g., 'auth', 'products')
        module_path: Import path (e.g., 'app.auth.router', 'app.products.router')
    """
    main_path = os.path.join("app", "main.py")
    if not os.path.exists(main_path):
        return
    
    with open(main_path, "r") as f:
        content = f.read()
    
    import_line = f"from {module_path} import router as {router_name}_router"
    include_line = f"app.include_router({router_name}_router)"
    
    # Skip if already present
    if import_line in content and include_line in content:
        return
    
    lines = content.split("\n")
    
    # Add import if not present
    if import_line not in content:
        # Find the last router import or last import from app.*
        last_router_import_idx = -1
        last_app_import_idx = -1
        last_import_idx = -1
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith("from app.") and "import router as" in stripped:
                last_router_import_idx = i
            elif stripped.startswith("from app."):
                last_app_import_idx = i
            elif stripped.startswith(("from ", "import ")):
                last_import_idx = i
        
        # Insert after last router import, or after last app import, or after last import
        insert_idx = last_router_import_idx + 1 if last_router_import_idx >= 0 else \
                     last_app_import_idx + 1 if last_app_import_idx >= 0 else \
                     last_import_idx + 1
        
        lines.insert(insert_idx, import_line)
    
    # Add include_router if not present
    if include_line not in content:
        # Find where to insert (after app = FastAPI(...))
        for i, line in enumerate(lines):
            if "app = FastAPI" in line:
                # Find the closing parenthesis
                j = i
                while j < len(lines) and ")" not in lines[j]:
                    j += 1
                lines.insert(j + 1, f"\n{include_line}")
                break
    
    with open(main_path, "w") as f:
        f.write("\n".join(lines))
    
    success(f"Router '{router_name}' auto-registered in main.py")


def add_model_to_session(model_name: str, module_path: str):
    """
    Add a model import to app/db/session.py for MongoDB projects.
    
    Args:
        model_name: Name of the model class (e.g., 'User', 'Product')
        module_path: Import path (e.g., 'app.auth.models', 'app.users.models')
    """
    session_path = os.path.join("app", "db", "session.py")
    if not os.path.exists(session_path):
        return
    
    with open(session_path, "r") as f:
        content = f.read()
    
    # Check if this is a MongoDB session file (contains 'beanie')
    if 'beanie' not in content:
        return  # Not a MongoDB project, skip
    
    import_line = f"from {module_path} import {model_name}"
    
    # Skip if already present
    if import_line in content:
        return
    
    lines = content.split("\n")
    
    # Find where to insert the import - after the comment block, before async def
    insert_idx = -1
    for i, line in enumerate(lines):
        # Look for the end of the comment block
        if "# ============================================================" in line:
            # Find the next line after this comment block ends
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "" or lines[j].strip().startswith("#"):
                    continue
                # Found the line after comments (should be async def or another import)
                insert_idx = j
                break
            break
    
    if insert_idx == -1:
        warning("Could not find insertion point in session.py")
        return
    
    # Insert the import
    lines.insert(insert_idx, import_line)
    
    # Now find and update document_models = []
    for i, line in enumerate(lines):
        if "document_models = []" in line:
            # Collect all model imports
            imported_models = []
            for prev_line in lines[:i]:
                if prev_line.strip().startswith("from app.") and ".models import" in prev_line:
                    # Extract model name
                    parts = prev_line.split("import")
                    if len(parts) == 2:
                        model = parts[1].strip()
                        imported_models.append(model)
            
            if imported_models:
                # Replace the line with the models list
                indent = len(line) - len(line.lstrip())
                lines[i] = " " * indent + f"document_models = [{', '.join(imported_models)}]  # Auto-registered models"
            break
    
    with open(session_path, "w") as f:
        f.write("\n".join(lines))
    
    success(f"Model '{model_name}' auto-registered in app/db/session.py")



# ---------------------------
# Docker-compose helpers (.dev) non-invasive
# ---------------------------
def ensure_env_file(env_path: str, vars: dict):
    """Create or update .env, adding missing variables (does not overwrite existing ones)."""
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
            warning(f"Updated variables in {env_path}")
        else:
            warning(f"{env_path} already contained all required variables")
    else:
        with open(env_path, "w") as f:
            for k, v in vars.items():
                f.write(f"{k}={v}\n")
        success(f"{env_path} created")


def ensure_compose_has_service(compose_path: str, service_key: str, service_block: str, volumes: list[str]):
    """Add a service block to compose (non-invasive). If the service exists, do nothing.
    If compose does not exist, create it with version 3.8 and the service.
    """
    if os.path.exists(compose_path):
        with open(compose_path, "r") as f:
            content = f.read()

        if service_key in content:
            warning(f"Service '{service_key}' already exists in {compose_path}")
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

        success(f"Service '{service_key}' added to {compose_path}")
    else:
        # crear nuevo compose con el servicio
        base = "version: '3.8'\nservices:\n"
        content = base + service_block + "\nvolumes:\n"
        for v in volumes:
            content += f"  {v}:\n"
        with open(compose_path, "w") as f:
            f.write(content)
        success(f"{compose_path} created with service '{service_key}'")


# ===========================
# ADD AUTH
# ===========================
@add_app.command("auth")
def add_auth(
    auth_type: str = typer.Option(
        "jwt", 
        "--type", "-t",
        help="Tipo de autenticación: jwt | oauth2 | session"
    ),
):
    """
    🔐 Agrega autenticación completa al proyecto actual.
    
    Genera:
    - Módulo de autenticación (app/auth/)
    - Modelos de usuario
    - Endpoints de login/register
    - JWT token management
    - Tests de autenticación
    
    Ejemplos:
      crudfull add auth
      crudfull add auth --type jwt
      crudfull a auth -t oauth2
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
    
    # Generate Auth Tests
    test_auth_dir = os.path.join("tests", "auth")
    os.makedirs(test_auth_dir, exist_ok=True)
    write_file(test_auth_dir, "__init__.py", "")
    
    test_auth_content = render_template("auth/test_auth.jinja2", context)
    write_file(test_auth_dir, "test_auth.py", test_auth_content)
    
    # Auto-register router in main.py
    add_router_to_main("auth", "app.auth.router")
    
    # Auto-register User model in session.py for MongoDB
    if db == "mongo":
        add_model_to_session("User", "app.auth.models")

    # Update requirements.txt
    req_path = os.path.join(os.getcwd(), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path, "r") as f:
            req_content = f.read()
        
        new_deps = []
        if "pydantic[email]" not in req_content and "email-validator" not in req_content:
            # Replace pydantic with pydantic[email] if present, else add it
            if "pydantic" in req_content and "pydantic[email]" not in req_content:
                req_content = req_content.replace("pydantic", "pydantic[email]")
                typer.echo("📦 Actualizado 'pydantic' a 'pydantic[email]' en requirements.txt")
            else:
                new_deps.append("pydantic[email]")
        
        auth_deps = ["python-jose[cryptography]", "passlib[bcrypt]", "python-multipart"]
        for dep in auth_deps:
            if dep.split("[")[0] not in req_content: # Check base name
                new_deps.append(dep)
        
        if new_deps:
            with open(req_path, "a") as f:
                f.write("\n" + "\n".join(new_deps) + "\n")
            typer.echo(f"📦 Dependencias agregadas a requirements.txt: {', '.join(new_deps)}")
    else:
        warning("⚠️  No se encontró requirements.txt. Asegúrate de instalar: pydantic[email], python-jose[cryptography], passlib[bcrypt], python-multipart")

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
@app.command("n", hidden=True)  # Alias
def new_project(
    name: str = typer.Argument(..., help="Nombre del proyecto"),
    db: str = typer.Option(
        "sql", 
        "--db", "-d",
        help="Motor de base de datos: ghost (sin DB) | sql (PostgreSQL) | mongo (MongoDB)"
    ),
    docker: bool = typer.Option(
        False, 
        "--docker",
        help="Incluir Dockerfile y docker-compose.yml para producción"
    ),
):
    """
    ✨ Crea un nuevo proyecto FastAPI con arquitectura modular.
    
    Genera:
    - Estructura de proyecto completa
    - Configuración de base de datos
    - Docker setup (opcional)
    - Tests configurados
    - README con instrucciones
    
    Ejemplos:
      crudfull new mi_api
      crudfull new mi_api --db mongo
      crudfull new mi_api --db sql --docker
      crudfull n mi_api -d ghost
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
    
    # 1.1 welcome.html
    welcome_content = render_template("project/welcome.html.jinja2", context)
    write_file(os.path.join(name, "app"), "welcome.html", welcome_content)

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

    # 4.1 Pytest config
    pytest_content = render_template("project/pytest.jinja2", context)
    write_file(name, "pytest.ini", pytest_content)

    # 4.2 README
    readme_content = render_template("project/readme.jinja2", context)
    write_file(name, "README.md", readme_content)

    # 5. Docker files (optional)
    if docker:
        docker_compose_content = render_template("project/docker_compose.jinja2", context)
        write_file(name, "docker-compose.yml", docker_compose_content)
        
        dockerfile_content = render_template("project/dockerfile.jinja2", context)
        write_file(name, "Dockerfile", dockerfile_content)
    
    # 5.2 Env Example (always generated)
    env_example_content = render_template("project/env_example.jinja2", context)
    write_file(name, ".env.example", env_example_content)
    
    # 5.1 Docker Dev files (only if docker requested)
    if docker and db != 'ghost':
        docker_compose_dev_content = render_template("project/docker_compose_dev.jinja2", context)
        write_file(name, "docker-compose.dev.yml", docker_compose_dev_content)
        


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
    if docker and db != 'ghost':
        typer.echo("\n🔧 Modo Desarrollo (solo DB):")
        typer.echo("   cp .env.example .env")
        typer.echo("   docker-compose -f docker-compose.dev.yml up -d")
        typer.echo("   pip install -r requirements.txt")
        if db == 'mongo':
            typer.echo("\n📝 MongoDB: Después de generar recursos, registrá los modelos:")
            typer.echo("   crudfull sync-models  # Auto-registra todos los modelos")
            typer.echo("   # O editá manualmente app/db/session.py")
        typer.echo("   uvicorn app.main:app --reload")
    if not docker:
        if db != 'ghost':
            typer.echo("\n⚠️  Nota: No se generaron archivos Docker.")
            typer.echo("   Asegúrate de tener una base de datos corriendo.")
            typer.echo("   cp .env.example .env  # Configura tus credenciales")
        
        typer.echo("\n📦 pip install -r requirements.txt")
        if db == 'mongo':
            typer.echo("\n📝 MongoDB: Después de generar recursos:")
            typer.echo("   crudfull sync-models  # Registra modelos en app/db/session.py")
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
    """
    ℹ️  Muestra la versión instalada de crudfull.
    
    Ejemplo:
      crudfull version show
      crudfull v show
    """
    typer.echo(f"crudfull v{__version__}")


# ===========================
# GENERATE RESOURCE (MODULAR DEFAULT)
# ===========================
@generate_app.command("resource")
@generate_app.command("r", hidden=True)   # Alias
@generate_app.command("res", hidden=True) # Alias
def generate_resource(
    name: str = typer.Argument(
        ..., 
        help="Nombre del recurso en plural (ej: users, products, posts)"
    ),
    fields: list[str] = typer.Argument(
        ..., 
        help="Campos en formato nombre:tipo (ej: name:str email:str age:int)"
    ),
    db: str = typer.Option(
        None, 
        "--db", "-d",
        help="Forzar motor de DB: ghost | sql | mongo (usa config del proyecto por defecto)"
    ),
    force: bool = typer.Option(
        False, 
        "--force", "-f", 
        help="Sobrescribir archivos existentes sin preguntar"
    ),
):
    """
    📦 Genera un recurso CRUD completo con toda la arquitectura.
    
    Genera:
    - Models (SQLAlchemy/Beanie/Ghost)
    - Schemas (Pydantic)
    - Service (lógica de negocio)
    - Router (endpoints REST)
    - Tests completos
    
    Tipos soportados:
      str, int, float, bool, datetime, uuid
      Agregar '?' al final para campos opcionales (ej: bio:str?)
    
    Ejemplos:
      crudfull generate resource users name:str email:str age:int
      crudfull gen resource products title:str price:float stock:int description:str?
      crudfull g r posts title:str content:str + users name:str email:str
    """
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

    # Parse multiple resources
    resources_to_generate = []
    current_resource_name = name
    current_fields = []

    for item in fields:
        if item == "+":
            # Save current resource
            resources_to_generate.append({
                "name": current_resource_name,
                "fields": current_fields
            })
            # Reset for next (will be set by next iteration logic, but we need to handle the name)
            current_resource_name = None 
            current_fields = []
        elif current_resource_name is None:
            # This item is the name of the next resource
            current_resource_name = item
        else:
            # This item is a field
            current_fields.append(item)
    
    # Append the last resource
    if current_resource_name:
        resources_to_generate.append({
            "name": current_resource_name,
            "fields": current_fields
        })

    # Generate each resource
    for res in resources_to_generate:
        _generate_single_resource(res["name"], res["fields"], db)


def _generate_single_resource(name: str, fields: list[str], db: str):
    """Helper to generate a single resource"""
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
    add_router_to_main(resource, f"app.{resource}.router")
    
    # Auto-register model in session.py for MongoDB
    if db == "mongo":
        add_model_to_session(singular, f"app.{resource}.models")

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
    🔄 Sincroniza todos los routers en main.py automáticamente.
    
    Escanea:
    - app/*/router.py (arquitectura modular)
    - routers/*_router.py (arquitectura legacy)
    
    Y los registra automáticamente en main.py.
    
    Ejemplo:
      crudfull sync-routers run
      crudfull sync run
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
    resource: str = typer.Argument(
        ..., 
        help="Nombre del recurso a proteger (ej: users, products)"
    ),
    action: str = typer.Argument(
        None, 
        help="Acción específica: list | create | read | update | delete | all"
    ),
    func_name: str = typer.Option(
        None, 
        "--func", "--fn",
        help="Nombre específico de la función a proteger (ej: create_user)"
    ),
):
    """
    🔒 Protege rutas con autenticación JWT.
    
    Agrega Depends(get_current_user) a los endpoints especificados.
    Requiere haber ejecutado 'crudfull add auth' primero.
    
    Ejemplos:
      crudfull protect users all
      crudfull protect products create
      crudfull protect posts update
      crudfull protect users --func create_user
      crudfull protect posts --fn create_post
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
# SYNC MODELS (MongoDB)
# ===========================
@app.command("sync-models")
def sync_models():
    """
    🔄 Auto-registra modelos de MongoDB en app/db/session.py.
    
    Escanea todos los archivos app/*/models.py y registra automáticamente
    las clases Document en la configuración de Beanie.
    
    Solo para proyectos MongoDB.
    
    Ejemplo:
      crudfull sync-models
    """
    session_path = os.path.join("app", "db", "session.py")
    
    if not os.path.exists(session_path):
        error("❌ No se encontró app/db/session.py")
        typer.echo("💡 Tip: Ejecutá este comando desde la raíz del proyecto")
        raise typer.Exit(code=1)
    
    with open(session_path, "r") as f:
        content = f.read()
    
    # Check if this is a MongoDB project
    if 'beanie' not in content:
        error("❌ Este proyecto no usa MongoDB/Beanie")
        raise typer.Exit(code=1)
    
    # Find all model files in app/*/models.py
    import glob
    model_files = glob.glob(os.path.join("app", "*", "models.py"))
    
    if not model_files:
        warning("⚠️  No se encontraron archivos models.py")
        typer.echo("💡 Tip: Generá recursos primero con 'crudfull generate resource'")
        raise typer.Exit(code=0)
    
    # Extract model information
    models_to_import = []
    for model_file in model_files:
        # Extract module name (e.g., app/users/models.py -> users)
        parts = model_file.split(os.sep)
        if len(parts) >= 3:
            module_name = parts[1]  # 'users' from app/users/models.py
            
            # Read the file to find Document classes
            try:
                with open(model_file, "r") as f:
                    model_content = f.read()
                
                # Simple heuristic: look for class definitions that inherit from Document
                import re
                # Match: class ClassName(Document): or class ClassName(BaseModel, Document):
                class_matches = re.findall(r'class\s+(\w+)\s*\([^)]*Document[^)]*\):', model_content)
                
                for class_name in class_matches:
                    models_to_import.append({
                        'module': f"app.{module_name}.models",
                        'class': class_name
                    })
            except Exception:
                pass
    
    if not models_to_import:
        warning("⚠️  No se encontraron modelos Document en los archivos")
        raise typer.Exit(code=0)
    
    # Update session.py
    lines = content.split("\n")
    
    # Find the comment block and document_models line
    comment_end_idx = -1
    models_list_idx = -1
    
    for i, line in enumerate(lines):
        if "# ============================================================" in line:
            # We want the LAST occurrence of this separator before the imports
            # But simpler: just find the one before async def init_db
            pass
            
    # Better strategy: Find 'async def init_db' and work backwards to find the comment block
    async_def_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("async def init_db"):
            async_def_idx = i
            break
            
    if async_def_idx != -1:
        # Search backwards for the comment separator
        for i in range(async_def_idx - 1, -1, -1):
            if "# ============================================================" in lines[i]:
                comment_end_idx = i
                break
    
    # Find document_models line (can be empty or populated)
    for i, line in enumerate(lines):
        if "document_models =" in line:
            models_list_idx = i
            break
    
    if comment_end_idx == -1 or models_list_idx == -1:
        # Fallback for comment block: try to find the first double separator
        if comment_end_idx == -1:
             separators = [i for i, line in enumerate(lines) if "# ============================================================" in line]
             if len(separators) >= 2:
                 comment_end_idx = separators[1]

    if comment_end_idx == -1 or models_list_idx == -1:
        error("❌ No se pudo encontrar la estructura esperada en session.py")
        typer.echo("ℹ️  Se busca:")
        typer.echo("   1. Un bloque de comentarios '# ============================================================'")
        typer.echo("   2. Una variable 'document_models = ...'")
        raise typer.Exit(code=1)
    
    # Remove old imports (between comment block and async def)
    # Use async_def_idx found earlier or find it again
    if async_def_idx == -1:
        for i in range(comment_end_idx, len(lines)):
            if lines[i].strip().startswith("async def"):
                async_def_idx = i
                break
    
    # Remove lines between comment_end and async_def that are imports
    if async_def_idx != -1:
        new_lines = lines[:comment_end_idx + 1]
        new_lines.append("")  # Empty line after comment
        
        # Add new imports
        for model in models_to_import:
            new_lines.append(f"from {model['module']} import {model['class']}")
        
        new_lines.append("")  # Empty line before async def
        new_lines.extend(lines[async_def_idx:])
        lines = new_lines
        
        # Recalculate models_list_idx because lines changed
        for i, line in enumerate(lines):
            if "document_models =" in line:
                models_list_idx = i
                break
    
    # Update document_models list
    model_names = [m['class'] for m in models_to_import]
    if models_list_idx != -1:
        line = lines[models_list_idx]
        indent = len(line) - len(line.lstrip())
        lines[models_list_idx] = " " * indent + f"document_models = [{', '.join(model_names)}]  # Auto-registered models"
    
    # Write back
    with open(session_path, "w") as f:
        f.write("\n".join(lines))
    
    success(f"✅ {len(models_to_import)} modelo(s) registrado(s) en app/db/session.py:")
    for model in models_to_import:
        typer.echo(f"   - {model['class']} ({model['module']})")


# ===========================
# ENTRYPOINT
# ===========================
def main():
    app()

if __name__ == "__main__":
    main()

