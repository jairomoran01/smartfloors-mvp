# SmartFloors Backend API

Backend API para el sistema de monitoreo SmartFloors (FastAPI + SQLAlchemy + PostgreSQL).

## Requisitos
- Opción A (recomendada en ≤5 min): Docker Desktop.
- Opción B (desarrollo local): Python 3.11+, PostgreSQL 15+, Redis 7+.

## Quickstart con Docker (≤ 5 minutos)
Ejecutar desde la raíz del proyecto (donde está `docker-compose.yml`). Comandos para PowerShell.

1) Levantar servicios y API
```powershell
cd "c:\Users\bymig\Desktop\HACKATON\smartfloors-mvp"
docker compose up -d --build
```

2) Inicializar la base de datos (umbrales e índices)
```powershell
docker compose exec backend python init_db.py
```

3) Verificar
- Salud: `http://localhost:8000/health`
- Docs (Swagger): `http://localhost:8000/docs`

4) (Opcional) Cargar datos de ejemplo
```powershell
Invoke-RestMethod -Method POST `
	-Uri "http://localhost:8000/api/v1/data/import" `
	-ContentType "application/json" `
	-InFile ".\backend\example_data.json"
```

5) (Opcional) Generar datos sintéticos
```powershell
$body = @{ count = 30; interval_minutes = 1; scenario = "normal" } | ConvertTo-Json
Invoke-RestMethod -Method POST `
	-Uri "http://localhost:8000/api/v1/data/generate" `
	-ContentType "application/json" `
	-Body $body
```

## Desarrollo local (sin Docker)
1) Crear y activar entorno virtual
```powershell
cd "c:\Users\bymig\Desktop\HACKATON\smartfloors-mvp\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Instalar dependencias
```powershell
pip install -r requirements.txt
```

3) Configurar variables de entorno
```powershell
Copy-Item .env.example .env
# Edita .env si necesitas cambiar DATABASE_URL/REDIS_URL
```
Por defecto (archivo `app/config.py`):
- `DATABASE_URL=postgresql+psycopg2://admin:admin@localhost:5432/smartfloors`
- `REDIS_URL=redis://localhost:6379`

Asegúrate de tener PostgreSQL y Redis locales corriendo con esas credenciales/puertos.

4) Inicializar base de datos
```powershell
python .\init_db.py
```

5) Ejecutar FastAPI
```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Endpoints principales
- `GET /` — Estado de la API
- `GET /docs` — Swagger
- `GET /health` — Health check

Lecturas
- `POST /api/v1/readings` — Crear lectura
- `POST /api/v1/readings/batch` — Crear múltiples lecturas
- `GET /api/v1/readings` — Listar lecturas con filtros
- `GET /api/v1/readings/floors/{piso}/current` — Lectura actual de un piso

Alertas
- `GET /api/v1/alerts` — Listar alertas con filtros
- `POST /api/v1/alerts/{alert_id}/acknowledge` — Reconocer alerta
- `GET /api/v1/alerts/export` — Exportar alertas (CSV/JSON)

Predicciones
- `GET /api/v1/predictions/{piso}` — Obtener predicciones para un piso

Dashboard
- `GET /api/v1/dashboard/summary` — Resumen de dashboard

Importación y generación de datos
- `POST /api/v1/data/import` — Importar datos JSON
- `POST /api/v1/data/generate` — Generar datos de ejemplo
- `GET /api/v1/data/export-template` — Template de importación

Notificaciones
- `POST /api/v1/notifications/subscribe` — Suscripciones (opcional)

## Estructura del proyecto
```
backend/
├── app/
│   ├── main.py              # Aplicación principal
│   ├── config.py            # Configuración (.env soportado)
│   ├── database.py          # Engine/Session
│   ├── models/              # Modelos SQLAlchemy
│   ├── schemas/             # Schemas Pydantic
│   ├── routers/             # Endpoints API
│   └── services/            # Lógica de negocio
├── alembic/                 # Migraciones (opcional)
├── init_db.py               # Seed de umbrales + índices
├── requirements.txt         # Dependencias
└── Dockerfile               # Imagen Docker
```

## Migraciones (Alembic)
> Nota: El proyecto crea tablas automáticamente vía `Base.metadata.create_all`. Si usas migraciones:
```powershell
# Crear nueva migración
alembic revision --autogenerate -m "descripcion"

# Aplicar migraciones
alembic upgrade head

# Revertir última
alembic downgrade -1
```

## Variables de entorno
Ver `.env.example`. Principales:
- `DATABASE_URL` — URL PostgreSQL
- `REDIS_URL` — URL Redis
- `GEMINI_API_KEY` — API key (opcional)

## Troubleshooting
- Ver logs de la API (Docker):
```powershell
docker compose logs -f backend
```
- Reinicio limpio de datos locales (Docker):
```powershell
docker compose down
Remove-Item -Recurse -Force ..\data\db -ErrorAction SilentlyContinue
docker compose up -d --build
docker compose exec backend python init_db.py
```
- DB no lista al inicio: espera 5–10s y reintenta `init_db.py`.

