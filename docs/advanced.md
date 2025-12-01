# 🚀 Avanzado

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

## 🧪 Testing
Los tests usan `tests/conftest.py` con fixture `client`.
```bash
pytest
```
Para SQL se usa SQLite in‑memory, para Mongo una base de prueba aislada.
