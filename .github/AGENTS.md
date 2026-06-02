---
name: agents
description: "Custom agents para el proyecto de Sistema Coaching"
---

# Agentes Personalizados - Sistema Coaching

## 📋 Agentes Disponibles

### 1. **project-builder** ⭐ Recomendado
**Ubicación**: [.github/agents/project-builder.agent.md](.github/agents/project-builder.agent.md)

**Función**: Lee planes de implementación Markdown y crea automáticamente toda la estructura de carpetas y archivos necesarios.

**Cuándo usarlo**:
- Tienes un `PLAN_IMPLEMENTACION*.md` y quieres generar la estructura del proyecto
- Necesitas crear múltiples archivos basados en especificaciones documentadas
- Quieres transformar un documento técnico en código ejecutable

**Ejemplo de uso**:
```
"Implementa la estructura del PLAN_IMPLEMENTACION_SISTEMA_COACHING.md"

"@project-builder crea todas las carpetas y archivos Python"

"Quiero que generes la estructura completa incluyendo src/, config/, tests/"
```

**Lo que hace**:
✅ Extrae bloques de código Python del Markdown
✅ Crea directorios organizados
✅ Genera archivos con contenido completo
✅ Crea `.env.template` con variables requeridas
✅ Valida que no haya conflictos de nombres

**Output esperado**:
- Carpeta `src/` con scripts Python
- Carpeta `config/` con configuración
- `requirements.txt` con dependencias
- `scripts/` con utilidades
- `.env.template` con todas las variables necesarias
- Reporte de estructura creada

---

## 🚀 Quick Start

### Paso 1: Activar Project Builder
```
"Usa el project-builder para implementar la estructura del plan"
```

### Paso 2: Revisar la estructura generada
```bash
tree /F
```

### 2. **n8n-config**
**Ubicación**: [.github/agents/n8n-config.agent.md](.github/agents/n8n-config.agent.md)

**Función**: Configura flujos n8n para integrar Obsidian, Telegram y Strava según el plan de coaching.

**Cuándo usarlo**:
- Quieres crear la configuración n8n del proyecto
- Necesitas documentar e importar workflows para Strava/Telegram/Obsidian
- Deseas mapear credenciales y variables de entorno n8n

**Ejemplo de uso**:
```
"Configura los workflows n8n para Obsidian, Telegram y Strava"
"Genera la documentación n8n para el sistema de coaching"
"Crea la configuración de credenciales y workflows n8n"
```

**Lo que hace**:
- Diseña y propone workflows n8n
- Genera docs de importación y credenciales
- Crea un plan claro para conectar los servicios
- Ayuda a evitar errores de configuración de n8n

**Output esperado**:
- `docs/n8n/` con flujo y notas de configuración
- archivos de workflow n8n listos para importar
- `.env.template` con las variables clave

---

### Paso 3: Configurar variables de entorno
```bash
copy .env.template .env
# Editar .env con valores reales
```

### Paso 4: Instalar dependencias
```bash
pip install -r requirements.txt
```

---

## 📝 Notas

- El agente está configurado para detectar archivos `PLAN_IMPLEMENTACION*.md`
- Si quieres usarlo en otros proyectos, cópialos a tu perfil de usuario en `{{VSCODE_USER_PROMPTS_FOLDER}}/`
- Todos los agentes están ubicados en `.github/agents/` para fácil gestión en Git

---

## 🔗 Referencias

- [Agent Customization Guide](.github/README.md)
- [Project Builder Full Spec](.github/agents/project-builder.agent.md)
