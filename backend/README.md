# SmartFloors Backend API

Backend API para el sistema de monitoreo SmartFloors desarrollado con FastAPI.

## Requisitos

- Python 3.11+
- PostgreSQL 15+
- Redis (opcional, para tareas asíncronas)

## Instalación

1. Crear entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. Inicializar base de datos:
```bash
python init_db.py
```

## Ejecución

### Desarrollo local:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Con Docker:
```bash
docker-compose up backend
```

## Endpoints Principales

- `GET /` - Estado de la API
- `GET /docs` - Documentación interactiva (Swagger)
- `GET /health` - Health check

### Lecturas
- `POST /api/v1/readings` - Crear lectura
- `POST /api/v1/readings/batch` - Crear múltiples lecturas
- `GET /api/v1/readings` - Listar lecturas con filtros
- `GET /api/v1/readings/floors/{piso}/current` - Lectura actual de un piso

### Alertas
- `GET /api/v1/alerts` - Listar alertas con filtros
- `POST /api/v1/alerts/{alert_id}/acknowledge` - Reconocer alerta
- `GET /api/v1/alerts/export` - Exportar alertas (CSV/JSON)

### Predicciones
- `GET /api/v1/predictions/{piso}` - Obtener predicciones para un piso

### Dashboard
- `GET /api/v1/dashboard/summary` - Resumen del dashboard

### Importación y Generación de Datos
- `POST /api/v1/data/import` - Importar datos desde JSON
- `POST /api/v1/data/generate` - Generar datos de ejemplo (30+ datos)
- `GET /api/v1/data/export-template` - Obtener template JSON para importación

### Notificaciones
- `POST /api/v1/notifications/subscribe` - Suscribirse a notificaciones

## Estructura del Proyecto

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Aplicación principal
│   ├── config.py            # Configuración
│   ├── database.py          # Configuración de DB
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   ├── routers/             # Endpoints API
│   └── services/            # Lógica de negocio
├── alembic/                 # Migraciones de DB
├── init_db.py               # Script de inicialización
├── requirements.txt         # Dependencias
└── Dockerfile              # Imagen Docker
```

## Migraciones de Base de Datos

```bash
# Crear nueva migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

## Variables de Entorno

Ver `.env.example` para todas las variables disponibles.

Principales:
- `DATABASE_URL` - URL de conexión a PostgreSQL
- `REDIS_URL` - URL de conexión a Redis
- `GEMINI_API_KEY` - API key para Gemini (opcional)

