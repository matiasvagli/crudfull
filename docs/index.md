# 📘 CRUDfull — Documentación Oficial

<div align="center">
  <img src="./statics/LT2.png" alt="CRUDFULL Logo" style="width: 450px; height: 250px;"/>
</div>

Bienvenido a la documentación oficial de **CRUDfull**, un generador de proyectos y recursos CRUD para FastAPI, diseñado para crear APIs escalables, modulares y listas para producción en cuestión de segundos.

**CRUDfull** automatiza las partes repetitivas del desarrollo backend y te deja concentrarte en la lógica del negocio.

## 🚀 Tabla de Contenidos

👉 [Instalación](./installation.md)

👉 [Primeros Pasos](./getting-started.md)

👉 [Referencia de la CLI](./cli-reference.md)

👉 [Arquitectura del Proyecto](./architecture.md)

👉 [Conceptos Avanzados](./advanced.md)

👉 [Contribuir a CRUDfull](./contributing.md)

---

## 🎯 ¿Qué es CRUDfull?

**CRUDfull** es una herramienta de línea de comandos que genera:

- Estructura completa de proyectos con FastAPI
- CRUDs modulares (schemas, models, repository, service, router)
- Tests automáticos por recurso
- Integración opcional con Docker
- Compatibilidad con múltiples motores:
  - PostgreSQL (SQLAlchemy)
  - MongoDB (Motor)
  - GhostDB (in-memory)

Su objetivo es ofrecer una base sólida, profesional y extensible para cualquier API moderna.

## 🧱 Filosofía del Proyecto

- **Menos repetición** → generación automática de boilerplate
- **Arquitectura limpia** → separación clara entre capas
- **Extensibilidad** → agregar nuevos motores de base de datos es simple
- **Estandarización** → todos los recursos siguen el mismo patrón
- **Productividad real** → prototipos rápidos y producción lista

## 🔧 Qué Podés Hacer con CRUDfull

- Crear un proyecto nuevo con arquitectura modular
- Generar recursos completos con un solo comando
- Integrar autenticación JWT
- Levantar un entorno completo con Docker en segundos
- Correr tests generados automáticamente
- Extender la herramienta con tus propios templates

## 📦 Instalación Rápida

```bash
pip install crudfull
```

## 🏁 Empezar Ahora

```bash
crudfull new my_project --db sql --docker
```

Esto genera:
- Proyecto FastAPI completo
- Dockerfile + docker-compose
- Base de datos lista
- Estructura de carpetas profesional

Después:

```bash
cd my_project
crudfull generate resource users name:str age:int?
```

---

## 🔗 Navegación

- 📥 [Instalación](./installation.md)
- � [Primeros Pasos](./getting-started.md)
- 🧰 [CLI Reference](./cli-reference.md)
- 🧱 [Arquitectura](./architecture.md)
- 🧠 [Conceptos Avanzados](./advanced.md)
- 🤝 [Contribuir](./contributing.md)

## 💬 Comunidad y Contacto

- **Autor**: Matías Vagliviello (Matiasdev)
- **GitHub**: [https://github.com/matiasvagli](https://github.com/matiasvagli)
- **Proyecto**: [https://github.com/matiasvagli/crudfull](https://github.com/matiasvagli/crudfull)
