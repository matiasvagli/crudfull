# Migración a Pydantic 2.12+ - Checklist

## ✅ Completado hoy:
- [x] Actualizado `pyproject.toml` a `pydantic>=2.12.0`

## 📋 Para revisar mañana:

### 1. Verificar templates de schemas
Los templates actuales usan `Config` que es válido en Pydantic 2, pero podría haber warnings:

**Archivo:** `crudfull/templates/sql/schemas.jinja2`
```python
class Config:
    from_attributes = True  # ← Esto está bien en Pydantic 2
```

**Alternativa moderna (ConfigDict):**
```python
from pydantic import BaseModel, ConfigDict

class {{ model_name }}Response({{ model_name }}Base):
    id: int
    
    model_config = ConfigDict(from_attributes=True)
```

### 2. Verificar templates de auth
**Archivo:** `crudfull/templates/auth/schemas.jinja2`
- Revisar que use `EmailStr` correctamente
- Verificar `Config` vs `ConfigDict`

### 3. Actualizar requirements.txt template
**Archivo:** `crudfull/templates/project/requirements.jinja2`
- Ya usa `pydantic` sin versión específica (hereda de crudfull)

### 4. Probar warnings
```bash
# Crear proyecto de prueba
crudfull new test_pydantic --db sql
cd test_pydantic
crudfull generate resource products name:str price:float

# Verificar warnings
python -W all -m pytest tests/
```

### 5. Posibles warnings a resolver:
- `Config` → `ConfigDict` (deprecation warning)
- `EmailStr` importado de `pydantic` en lugar de `pydantic_extra_types`
- `validator` → `field_validator` (si usamos validadores custom)

## 🔧 Cambios recomendados:

### Opción 1: Mantener compatibilidad (actual)
- Usar `Config` class (funciona pero puede dar warnings)
- Más compatible con versiones anteriores

### Opción 2: Modernizar (recomendado)
- Usar `ConfigDict` 
- Sintaxis más moderna de Pydantic 2
- Sin warnings

## 📚 Referencias:
- https://docs.pydantic.dev/latest/migration/
- https://docs.pydantic.dev/latest/api/config/
