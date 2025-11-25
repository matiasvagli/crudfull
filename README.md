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
crudfull new mi_proyecto --db sql --docker
cd mi_proyecto
```
Esto genera:
```
mi_proyecto/
├── app/
│   ├── main.py
│   ├── db/
│   │   └── session.py
│   └── core/   # opcional, auth
├── tests/
├── crudfull.json
├── requirements.txt
├── .gitignore
├── docker-compose.yml
├── Dockerfile
└── .env.example
```

### Generar recursos (detecta DB automáticamente)
```bash
crudfull generate resource products name:str price:float stock:int
crudfull generate resource users name:str email:str
```
Cada recurso crea `schemas.py`, `models.py`, `service.py` y `router.py`.

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
crudfull add auth
```
Genera módulo `auth/` con JWT. Instala dependencias:
```bash
pip install crudfull[auth]
```
Protege rutas con el CLI:
```bash
crudfull protect products create
crudfull protect products all
```

---

## 📚 Comandos CLI
- `crudfull new <name> --db [sql|mongo|ghost] [--docker]`
- `crudfull generate resource <name> <field>:<type> ...`
- `crudfull add auth`
- `crudfull protect <resource> <action|all> [--func <func>]`
- `crudfull sync-routers run`

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

**Planned**
- 🛠️ Migraciones (Alembic)
- 🔐 OAuth2 (Google, GitHub)
- 🔗 Relaciones entre modelos (ForeignKey)
- 🌐 GraphQL support
- 🖥️ Admin panel

---

## 📄 Licencia
MIT

---

## 🤝 Contribuir
¡Las contribuciones son bienvenidas! Abre un issue o pull request.

---

**CRUDFULL** fue creado con pasión y café por **Matías Vagliviello**.
> *“Hecho en Argentina, para el mundo. Pensado para que crear CRUDs sea tan rápido como escribir una idea.”*
