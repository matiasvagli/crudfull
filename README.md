<div align="center">
  <img src="./logo_enhanced.png" alt="CRUDFULL Logo" style="width: 850px; height: 350px;"/>
</div>

# ⚡️ CRUDFULL — FastAPI Project Generator

**CRUDFULL** te permite crear APIs REST completas en segundos, con arquitectura modular y soporte para múltiples bases de datos.

## 🎯 Características

- 🚀 **Scaffolding de proyectos** - Crea proyectos FastAPI completos con un comando
- 🏗️ **Arquitectura modular** - Cada recurso es auto-contenido (schemas, models, service, router)
- 🔄 **Auto-registro de routers** - Los endpoints se registran automáticamente en `main.py`
- 🗄️ **Multi-DB** - Soporte para SQL (PostgreSQL), MongoDB y Ghost (in-memory)
- 🐳 **Docker ready** - Genera `docker-compose.yml` y `Dockerfile` opcionales
- 🐳 **Docker dev** - Genera `docker-compose.dev.yml` para desarrollo rapido
- 🔐 **Autenticación JWT** - Sistema de auth completo con un comando
- 🧪 **Tests incluidos** - Tests automáticos para cada recurso
- 📚 **Documentación automática** - FastAPI Swagger UI out-of-the-box
- ⚙️ **Context-aware** - Detecta automáticamente la configuración del proyecto

---

## 📦 Instalación

### Instalación completa (recomendada)
Por defecto, `crudfull` instala todo lo necesario para desarrollar:

```bash
pip install crudfull
```

Incluye:
- FastAPI + Uvicorn
- SQLAlchemy + AsyncPG (SQL)
- Beanie + Motor (MongoDB)
- Pydantic + Python-dotenv

### Instalación ligera (solo CLI)
Si solo querés el generador de código sin dependencias de runtime:

```bash
pip install crudfull[lite]
```

Solo incluye: `typer`, `jinja2`, `inflect`

### Herramientas de testing
Para agregar pytest y httpx:

```bash
pip install crudfull[test]
```

### Autenticación JWT
Para agregar soporte de autenticación:

```bash
pip install crudfull[auth]
```

---

## 🚀 Inicio Rápido

### 1. Crear un nuevo proyecto

```bash
crudfull new mi_tienda --db sql --docker
cd mi_tienda
```

Esto genera:
```
mi_tienda/
├── app/
│   ├── main.py              # FastAPI app con HTML de bienvenida
│   ├── db/
│   │   └── session.py       # Configuración de base de datos
│   └── core/                # (opcional, con auth)
├── tests/
├── crudfull.json            # Configuración del proyecto
├── requirements.txt
├── .gitignore
├── docker-compose.yml       # (con --docker)
├── Dockerfile               # (con --docker)
└── .env                     # (con --docker)
```

### 2. Generar recursos (detecta DB automáticamente)

```bash
crudfull generate resource products name:str price:float stock:int
crudfull generate resource users name:str email:str
crudfull generate resource orders user_id:int product_id:int quantity:int
```

Cada recurso genera:
```
app/
  products/
    __init__.py
    schemas.py      # Pydantic models
    models.py       # DB models (SQLAlchemy/Beanie)
    service.py      # Lógica de negocio
    router.py       # Endpoints FastAPI (auto-registrado)
tests/
  products/
    test_products.py
```

### 3. Levantar el servidor

```bash
# Con Docker
docker-compose up -d

# O manualmente
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Visitá `http://localhost:8000` para ver la página de bienvenida y `http://localhost:8000/docs` para la documentación interactiva.

---

## 🔐 Autenticación

### Agregar autenticación JWT al proyecto

```bash
crudfull add auth
```

Esto genera:
```
app/
  auth/
    __init__.py
    schemas.py        # UserCreate, UserLogin, Token
    models.py         # User model
    service.py        # hash_password, create_token
    router.py         # /auth/register, /auth/login, /auth/me
    dependencies.py   # get_current_user
  core/
    security.py       # JWT config
```

### Instalar dependencias de auth

```bash
pip install crudfull[auth]
```

### Proteger rutas
Puedes proteger rutas manualmente o usando el CLI:

**Opción 1: Usando CLI (Recomendado)**

```bash
# Proteger una acción específica (list, create, read, update, delete)
crudfull protect "recurso" "metodo"
crudfull protect products create

# Proteger todas las rutas del recurso
crudfull protect "recurso" "all"
crudfull protect products all

# Proteger una función específica por su nombre
crudfull protect "recurso" "funcion"
crudfull protect products --func upload_file
```

**Opción 2: Manualmente**

```python
from fastapi import Depends
from app.auth.dependencies import get_current_user
from app.auth.models import User

@router.post("/products")
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_user)
):
    return {"created_by": current_user.email, "product": product}
```

### Endpoints de autenticación

- `POST /auth/register` - Registrar nuevo usuario
- `POST /auth/login` - Login y obtener token JWT
- `GET /auth/me` - Obtener info del usuario actual (requiere token)

---

## 📚 Comandos CLI

### `crudfull new`
Crea un nuevo proyecto FastAPI

```bash
crudfull new <nombre> --db [sql|mongo|ghost] [--docker]
```

**Opciones:**
- `--db`: Base de datos (sql, mongo, ghost). Default: sql
- `--docker`: Genera archivos Docker

**Ejemplo:**
```bash
crudfull new mi_api --db mongo --docker
```

### `crudfull generate resource`
Genera un recurso CRUD completo

```bash
crudfull generate resource <nombre> <campo1:tipo> <campo2:tipo> ...
```

**Tipos soportados:**
- `str`, `int`, `float`, `bool`
- `datetime`, `uuid`
- Agregar `?` para campos opcionales: `email:str?`

**Ejemplo:**
```bash
crudfull generate resource users name:str email:str age:int? created_at:datetime
```

### `crudfull add auth`
Agrega autenticación JWT al proyecto

```bash
crudfull add auth [--type jwt]
```

### `crudfull protect`
Protege rutas de un recurso con autenticación

```bash
crudfull protect <resource> <action|all> [--func <nombre>]
```

### `crudfull sync-routers run`
Sincroniza todos los routers existentes con `main.py`

```bash
crudfull sync-routers run
```

---

## 🗄️ Bases de Datos Soportadas

### SQL (PostgreSQL, MySQL, SQLite)
```bash
crudfull new mi_api --db sql
```

Usa SQLAlchemy Async + AsyncPG

**Variables de entorno:**
```env
DATABASE_URL=postgresql+asyncpg://user:password@localhost/dbname
```

### MongoDB
```bash
crudfull new mi_api --db mongo
```

Usa Beanie ODM + Motor

**Variables de entorno:**
```env
MONGO_URL=mongodb://localhost:27017
```

### Ghost (In-Memory)
```bash
crudfull new mi_api --db ghost
```

Sin base de datos real, ideal para prototipos y demos.

---

## 🐳 Docker

### Generar archivos Docker

```bash
crudfull new mi_api --db sql --docker
```

Esto crea:
- `docker-compose.yml` - Orquestación de servicios (app + DB)
- `Dockerfile` - Imagen de la aplicación
- `.env` - Variables de entorno

### Levantar con Docker

```bash
docker-compose up -d --build
```

La API estará disponible en `http://localhost:8000`

### Modo Desarrollo (solo DB)

Para desarrollo local, se genera automáticamente `docker-compose.dev.yml` que solo levanta la base de datos:

```bash
# 1. Levantar solo la DB en Docker
docker-compose -f docker-compose.dev.yml up -d

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Correr la app localmente (con hot reload)
uvicorn app.main:app --reload
```

**Ventajas del modo desarrollo:**
- ✅ DB en Docker (no necesitás instalar Postgres/Mongo)
- ✅ App en local (hot reload instantáneo)
- ✅ Fácil debugging con breakpoints
- ✅ Credenciales simples en `.env.dev`

**Archivos generados:**
- `docker-compose.dev.yml` - Solo servicio de DB
- `.env.dev` - Variables de entorno para desarrollo

---

## ⚙️ Configuración del Proyecto

El archivo `crudfull.json` almacena la configuración del proyecto:

```json
{
  "project_name": "mi_tienda",
  "db": "sql"
}
```

Esto permite que `crudfull generate resource` detecte automáticamente la base de datos sin necesidad de especificar `--db` cada vez.

---

## 🧪 Testing

Los tests se generan automáticamente para cada recurso con los tipos de datos correctos:

```bash
pytest
```

### Tests automáticos

Cada módulo tiene sus propios tests en `tests/<modulo>/test_<modulo>.py`. Los tests se generan **dinámicamente** basados en los campos que definís:

**Ejemplo:**
```bash
crudfull generate resource products name:str price:float stock:int
```

**Genera automáticamente:**
```python
def test_create_product(client):
    response = client.post("/products/", json={
        "name": "test",      # ← str
        "price": 1.0,        # ← float (automático!)
        "stock": 1,          # ← int
    })
    assert response.status_code == 200
```

### Tipos soportados en tests

| Tipo | Valor de test generado |
|------|------------------------|
| `str` | `"test"` |
| `int` | `1` |
| `float` | `1.0` |
| `bool` | `True` |
| `datetime` | `datetime.utcnow().isoformat()` |
| `uuid` | `str(uuid4())` |

### Fixture `client`

Todos los tests usan el fixture `client` definido en `tests/conftest.py`:

```python
@pytest.fixture(scope="function")
def client(test_db):
    # TestClient síncrono de FastAPI
    with TestClient(app) as test_client:
        yield test_client
```

**Características:**
- ✅ SQLite in-memory para tests rápidos (SQL)
- ✅ Base de datos de test aislada (Mongo)
- ✅ Limpieza automática después de cada test
- ✅ No requiere base de datos externa

---

## 📖 Ejemplo Completo

```bash
# 1. Crear proyecto
crudfull new tienda --db sql --docker

# 2. Entrar al proyecto
cd tienda

# 3. Generar recursos
crudfull generate resource products name:str price:float stock:int
crudfull generate resource users name:str email:str
crudfull generate resource orders user_id:int product_id:int quantity:int

# 4. Agregar autenticación
crudfull add auth
pip install crudfull[auth]

# 5. Levantar con Docker
docker-compose up -d

# 6. Visitar la API
# http://localhost:8000 - Página de bienvenida
# http://localhost:8000/docs - Documentación interactiva
```

---

## 🛠️ Desarrollo

### Instalar en modo desarrollo

```bash
git clone https://github.com/TU-USUARIO/crudfull.git
cd crudfull
pip install -e .
```

---

## 📝 Roadmap

- [x] Arquitectura modular
- [x] Project scaffolding (`crudfull new`)
- [x] Docker support
- [x] Context awareness (`crudfull.json`)
- [x] Autenticación JWT
- [ ] Migraciones (Alembic)
- [ ] OAuth2 (Google, GitHub)
- [ ] Relaciones entre modelos (ForeignKey)
- [ ] GraphQL support
- [ ] Admin panel

---

## 📄 Licencia

MIT

---

## 🤝 Contribuir

¡Las contribuciones son bienvenidas! Por favor, abrí un issue o pull request.

---



**CRUDfull** fue creado con pasión y café por:

**Matías Vagliviello** — Desarrollador & Arquitecto del proyecto  


> *“Hecho en Argentina, para el mundo. Pensado para que crear CRUDs sea tan rápido como escribir una idea.”*


