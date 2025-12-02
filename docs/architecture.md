# 🏗️ Arquitectura

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

---

