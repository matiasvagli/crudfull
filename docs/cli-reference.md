# 📚 Comandos CLI

## Comandos Principales

### 🆕 Crear Proyecto
```bash
crudfull new <name> --db [sql|mongo|ghost] [--docker]
# Alias: crudfull n
crudfull n mi_api --db mongo
crudfull n mi_api -d sql --docker
```

### 📦 Generar Recursos
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

### 🔐 Agregar Autenticación
```bash
crudfull add auth [--type jwt|oauth2|session]
# Alias: crudfull a
crudfull a auth
crudfull a auth -t jwt
```

### 🔒 Proteger Rutas
```bash
crudfull protect <resource> <action|all> [--func <function>]
crudfull protect users all
crudfull protect products create
crudfull protect posts --func create_post
crudfull protect posts --fn create_post  # alias de --func
```

### 🔄 Sincronizar Routers
```bash
crudfull sync-routers run
# Alias: crudfull sync
crudfull sync run
```

### 🔄 Sincronizar Modelos (MongoDB)
```bash
crudfull sync-models
```

### ℹ️ Versión
```bash
crudfull version show
# Alias: crudfull v
crudfull v show
```

## ⚡ Tabla de Alias

| Comando Completo | Alias | Ejemplo |
|-----------------|-------|---------|
| `crudfull new` | `crudfull n` | `crudfull n mi_api -d mongo` |
| `crudfull generate` | `crudfull gen`, `crudfull g` | `crudfull g r users name:str` |
| `crudfull generate resource` | `crudfull g r`, `crudfull gen res` | `crudfull g r posts title:str` |
| `crudfull add` | `crudfull a` | `crudfull a auth -t jwt` |
| `crudfull version` | `crudfull v` | `crudfull v show` |
| `crudfull sync-routers` | `crudfull sync` | `crudfull sync run` |

## 💡 Opciones Cortas

- `--db` → `-d` (motor de base de datos)
- `--type` → `-t` (tipo de autenticación)
- `--force` → `-f` (forzar sobrescritura)
- `--func` → `--fn` (función específica)

---
