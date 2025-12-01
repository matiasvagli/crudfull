# 🚀 Inicio rápido

## Crear un nuevo proyecto
```bash
# Crear proyecto (usa alias 'n' para más rapidez)
crudfull new mi_proyecto --db sql --docker
# o más corto:
crudfull n mi_proyecto -d sql --docker

cd mi_proyecto
```

## Levantar la aplicación

### Con Docker (producción)
```bash
docker-compose up -d --build
```

### Modo desarrollo (solo DB en Docker, app local)
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

## 💡 Tips y Trucos

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
