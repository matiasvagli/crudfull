# ⚡️ CRUDFULL — FastAPI Project Generator

<div align="center">
  <img src="./loguito.jpeg" alt="CRUDFULL Logo" style="width: 850px; height: 350px;"/>
</div>

**CRUDFULL** te permite crear APIs REST completas en segundos, con arquitectura modular y soporte para múltiples bases de datos.

## 🎯 Características
- 🚀 Scaffolding de proyectos
- 🏗️ Arquitectura modular (schemas, models, service, router)
- 🔄 Auto‑registro de routers
- 🗄️ Multi‑DB (SQL, Mongo, Ghost)
- 🐳 Docker ready (producción y modo desarrollo)
- 🔐 Autenticación JWT
- 🧪 Tests incluidos
- 📚 Documentación automática (Swagger UI)
- ⚙️ Context‑aware
- ⚡ Alias de comandos (n, g, a, v, sync)
- 💡 CLI mejorado con ejemplos y ayuda detallada

---

## 📦 Instalación
### Completa (recomendada)
```bash
pip install crudfull
```
Incluye FastAPI, Uvicorn, SQLAlchemy + AsyncPG, Beanie + Motor, Pydantic, python‑dotenv.

### Ligera (solo CLI)
```bash
pip install crudfull[lite]
```
Solo `typer`, `jinja2` e `inflect`.

### Opcionales
- Tests: `pip install crudfull[test]`
- Auth: `pip install crudfull[auth]`

---

## 🚀 Inicio rápido
```bash
# Crear proyecto (usa alias 'n' para más rapidez)
crudfull new mi_proyecto --db sql --docker
# o más corto:
crudfull n mi_proyecto -d sql --docker

cd mi_proyecto
```
## 📁 Estructura del Proyecto

```text
{{ project_name }}/
├── app/
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── db/
│   │   └── session.py       # Configuración de base de datos
│   └── [recursos]/          # Módulos generados con crudfull
│       ├── models.py
│       ├── schemas.py
│       ├── repository.py   # Nuevo layer de acceso a datos
│       ├── service.py
│       └── router.py
├── tests/                   # Tests generados automáticamente
├── .env.example             # Variables de entorno (template)
├── docker-compose.dev.yml   # Solo DB para desarrollo local
{% if db != 'ghost' %}├── docker-compose.yml       # App + DB para producción{% endif %}
└── requirements.txt
```

## 📂 Patrón Repository

Se añadió una capa de **Repository** para abstraer el acceso a datos y desacoplar los servicios de la implementación concreta de la base de datos (MongoDB, SQL o Ghost). Cada recurso ahora incluye `repository.py` que expone métodos CRUD y es inyectado en los servicios.

### Generar recursos (detecta DB automáticamente)
```bash
# Forma completa
crudfull generate resource products name:str price:float stock:int

# Usando alias (más rápido)
crudfull g r users name:str email:str age:int
crudfull g r posts title:str content:str published:bool author_id:uuid
```
Cada recurso crea `schemas.py`, `models.py`, `service.py`, `router.py` y tests.

### Levantar la aplicación
#### Con Docker (producción)
```bash
docker-compose up -d --build
```
#### Modo desarrollo (solo DB en Docker, app local)
```bash
# 1. Copiar variables de entorno
cp .env.example .env
# 2. Levantar la DB
docker compose -f docker-compose.dev.yml up -d
# 3. Instalar dependencias
pip install -r requirements.txt
# 4. Ejecutar la app con hot‑reload
uvicorn app.main:app --reload
```
Visita `http://localhost:8000` (welcome) y `http://localhost:8000/docs` (Swagger).

---

## 🗄️ Bases de datos soportadas
### SQL (PostgreSQL, MySQL, SQLite)
```bash
crudfull new mi_api --db sql
```
Usa **SQLAlchemy Async + AsyncPG**.
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```
### MongoDB
```bash
crudfull new mi_api --db mongo
```
Usa **Beanie + Motor**.
```env
MONGO_URL=mongodb://localhost:27017
```
### Ghost (in‑memory)
```bash
crudfull new mi_api --db ghost
```
Ideal para prototipos.

---

## 🔐 Autenticación
```bash
# Forma completa
crudfull add auth

# Usando alias (más rápido)
crudfull a auth
crudfull a auth -t jwt
```
Genera módulo `auth/` con JWT. Instala dependencias:
```bash
pip install crudfull[auth]
```
Protege rutas con el CLI:
```bash
# Proteger todas las rutas de un recurso
crudfull protect products all

# Proteger rutas específicas
crudfull protect products create
crudfull protect users update

# Proteger función específica
crudfull protect posts --func create_post
crudfull protect posts --fn create_post  # alias
```

---

## 📚 Comandos CLI

### Comandos Principales

#### 🆕 Crear Proyecto
```bash
crudfull new <name> --db [sql|mongo|ghost] [--docker]
# Alias: crudfull n
crudfull n mi_api --db mongo
crudfull n mi_api -d sql --docker
```

#### 📦 Generar Recursos
```bash
crudfull generate resource <name> <field>:<type> ...
# Alias: crudfull gen, crudfull g, crudfull g r
crudfull g r users name:str email:str age:int
crudfull gen resource products title:str price:float stock:int description:str?

# 🆕 Generar múltiples recursos a la vez (separador +)
crudfull g r posts title:str content:str + users name:str email:str
```

**Tipos soportados**: `str`, `int`, `float`, `bool`, `datetime`, `uuid`  
**Campos opcionales**: Agregar `?` al final (ej: `bio:str?`)

#### 🔐 Agregar Autenticación
```bash
crudfull add auth [--type jwt|oauth2|session]
# Alias: crudfull a
crudfull a auth
crudfull a auth -t jwt
```

#### 🔒 Proteger Rutas
```bash
crudfull protect <resource> <action|all> [--func <function>]
crudfull protect users all
crudfull protect products create
crudfull protect posts --func create_post
crudfull protect posts --fn create_post  # alias de --func
```

#### 🔄 Sincronizar Routers
```bash
crudfull sync-routers run
# Alias: crudfull sync
crudfull sync run
```

#### 🔄 Sincronizar Modelos (MongoDB)
```bash
crudfull sync-models
```

#### ℹ️ Versión
```bash
crudfull version show
# Alias: crudfull v
crudfull v show
```

### ⚡ Tabla de Alias

| Comando Completo | Alias | Ejemplo |
|-----------------|-------|---------|
| `crudfull new` | `crudfull n` | `crudfull n mi_api -d mongo` |
| `crudfull generate` | `crudfull gen`, `crudfull g` | `crudfull g r users name:str` |
| `crudfull generate resource` | `crudfull g r`, `crudfull gen res` | `crudfull g r posts title:str` |
| `crudfull add` | `crudfull a` | `crudfull a auth -t jwt` |
| `crudfull version` | `crudfull v` | `crudfull v show` |
| `crudfull sync-routers` | `crudfull sync` | `crudfull sync run` |

### 💡 Opciones Cortas

- `--db` → `-d` (motor de base de datos)
- `--type` → `-t` (tipo de autenticación)
- `--force` → `-f` (forzar sobrescritura)
- `--func` → `--fn` (función específica)

---

## 🧪 Testing
Los tests usan `tests/conftest.py` con fixture `client`.
```bash
pytest
```
Para SQL se usa SQLite in‑memory, para Mongo una base de prueba aislada.

---

## 🛠️ Desarrollo
```bash
git clone https://github.com/matiasvagli/crudfull.git
cd crudfull
pip install -e .
```

---

## 📝 Roadmap

**Completed**
- ✅ Arquitectura modular
- ✅ Scaffolding de proyectos
- ✅ Docker support
- ✅ Context awareness
- ✅ Autenticación JWT
- ✅ Alias de comandos (n, g, a, v, sync)
- ✅ Opciones cortas (-d, -t, -f)
- ✅ Documentación mejorada del CLI
- ✅ MongoDB ObjectId serialization fix

**Planned**
- 🛠️ Migraciones (Alembic)
- 🔐 OAuth2 (Google, GitHub)
- 🔗 Relaciones entre modelos (ForeignKey)
- 🌐 GraphQL support
- 🖥️ Admin panel

---

## � Tips y Trucos

### Flujo de trabajo rápido
```bash
# 1. Crear proyecto con MongoDB
crudfull n blog -d mongo --docker

# 2. Generar recursos usando alias (múltiples a la vez)
cd blog
crudfull g r posts title:str content:str published:bool + users name:str email:str

# 3. Agregar autenticación
crudfull a auth

# 4. Proteger rutas
crudfull protect posts all
crudfull protect users all

# 5. Sincronizar modelos (MongoDB)
crudfull sync-models

# 6. Levantar la app
docker compose -f docker-compose.dev.yml up -d
uvicorn app.main:app --reload
```

### Comandos más usados
```bash
# Crear proyecto rápido
crudfull n api -d sql

# Generar recurso rápido
crudfull g r items name:str price:float

# Agregar auth rápido
crudfull a auth

# Ver ayuda de cualquier comando
crudfull --help
crudfull g r --help
crudfull a auth --help
```

### Ejecutar como módulo Python
```bash
# Si no tienes crudfull instalado globalmente
python -m crudfull --help
python -m crudfull n mi_api -d mongo
```

---

## �📄 Licencia
MIT

---

## 🤝 Contribuir
¡Las contribuciones son bienvenidas! Abre un issue o pull request.

---

**CRUDFULL** fue creado con pasión y café por **Matías Vagliviello**.
> *“Hecho en Argentina, para el mundo. Pensado para que crear CRUDs sea tan rápido como escribir una idea.”*
