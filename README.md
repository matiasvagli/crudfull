# ⚡️ CRUDFULL — Generador de CRUDs para FastAPI

**CRUDFULL** te permite crear recursos CRUD completos en segundos, soportando tres motores:

- 🟢 **ghost**: CRUD sin base de datos (prototipos, demos, tests)
- 🟦 **sql**: SQLAlchemy Async (PostgreSQL, MySQL, SQLite…)
- 🟩 **mongo**: MongoDB con Beanie (ODM basado en Pydantic)

## ✨ ¿Qué genera?

- Modelos Pydantic
- Modelos SQL/Mongo
- Servicios completos
- Routers FastAPI
- Ejemplos de conexión a DB
- Estructura lista para usar

---

## 🚀 Instalación (modo desarrollo)

```bash
git clone https://github.com/TU-USUARIO/crudfull.git
cd crudfull
pip install -e .
```

---

## 🧪 Crear un proyecto de prueba

```bash
mkdir crudfull_test
cd crudfull_test
```

---

## ⚙️ Uso del CLI

### 📍 Ver versión

```bash
crudfull version
```

---

## 🧱 Generar un recurso completo

```bash
crudfull generate resource <Nombre> <campos...> --db <motor>
```

Ejemplo de campos:  
`name:str age:int active:bool`

Motores disponibles:  
- `ghost` (default)
- `sql`
- `mongo`

---

### 👻 Modo GHOST (sin base de datos)

```bash
crudfull generate resource User name:str age:int --db ghost
```

Genera:
- `models/user.py`
- `services/user_service_ghost.py`
- `routers/user_router.py`

Perfecto para prototipos, pruebas y demos rápidas.

---

### 🟦 Modo SQL (SQLAlchemy Async)

```bash
crudfull generate resource Product title:str price:int --db sql
```

Genera:
- `models/product.py` (Pydantic)
- `models/product_sql.py` (SQLAlchemy)
- `services/product_service_sql.py`
- `routers/product_router.py`
- `database_examples/database_sql_example.py`

Listo para usar en FastAPI:

```python
from database_examples.database_sql_example import get_db
```

---

### 🟩 Modo Mongo (Beanie ODM)

```bash
crudfull generate resource Order amount:int code:str --db mongo
```

Genera:
- `models/order.py`
- `models/order_mongo.py`
- `services/order_service_mongo.py`
- `routers/order_router.py`
- `database_examples/database_mongo_example.py`

Inicializa con:

```python
from database_examples.database_mongo_example import init_db
```

---

## 📁 Estructura generada

```
models/
services/
routers/
database_examples/
```

Backend modular, limpio y escalable.

---

## 🧙‍♂️ Arquitectura de Templates

```
crudfull/
  templates/
    ghost/
    sql/
    mongo/
```

---

## 🛠️ Roadmap futuro

- 🧪 Generación automática de tests (pytest + httpx)
- 📦 Comando para generar un proyecto FastAPI completo (`crudfull new project`)
- 🗄️ Compatibilidad con más ORMs (Tortoise ORM, Prisma, SQLModel)
- ⚙️ Parámetros avanzados: soft deletes, timestamps, UUIDs, relaciones 1:N & N:M
- 🚀 Publicación oficial en PyPI
- 📘 Documentación completa con MkDocs + GH Pages
- 🧩 Plantillas personalizables para el usuario
- 🛡️ Validaciones avanzadas, manejo de errores y respuestas estándar
- 🔌 Integración con OpenAPI/Swagger extendida
- 🧰 Generación de CLI para testear CRUDs automáticamente

---

## 👨‍💻 Autores

**CRUDfull** fue creado con pasión y café por:

- **Matías Vagliviello** — Desarrollador & Arquitecto del proyecto  
- **DevGPT 5.1** — IA colaborativa / Co-autor del motor y CLI  

> *“Hecho en Argentina, para el mundo. Pensado para que crear CRUDs sea tan rápido como escribir una idea.”*
