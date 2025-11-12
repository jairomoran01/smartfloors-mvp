# SmartFloors MVP — Arranque en ≤5 minutos (Windows/PowerShell)

Estas instrucciones te levantan el backend (API + Postgres + Redis) y, opcionalmente, el frontend, en menos o igual a 5 minutos usando Docker. Todo probado con PowerShell en Windows.

## Requisitos
- Docker Desktop instalado y corriendo.
- PowerShell (`pwsh.exe`).
- Opcional (solo para frontend local): Node.js 18+ y npm.

## Backend (Docker) — 3 pasos rápidos
1) Posiciónate en la carpeta del proyecto
```powershell
cd "c:\Users\bymig\Desktop\HACKATON\smartfloors-mvp"
```

2) Levanta base de datos, Redis y API
```powershell
# Arranca servicios de base (db, redis) y la API
docker compose up -d --build
```

3) Inicializa la base (umbrales e índices)
```powershell
docker compose exec backend python init_db.py
```

Listo. Verifica:
- Salud: `http://localhost:8000/health`
- Docs (Swagger): `http://localhost:8000/docs`

## (Opcional) Cargar datos de ejemplo en segundos
Con el backend arriba, importa el JSON de ejemplo:
```powershell
Invoke-RestMethod -Method POST \ 
	-Uri "http://localhost:8000/api/v1/data/import" \ 
	-ContentType "application/json" \ 
	-InFile ".\backend\example_data.json"
```

También puedes generar datos sintéticos (últimas ~2-4h):
```powershell
$body = @{ count = 30; interval_minutes = 1; scenario = "normal" } | ConvertTo-Json
Invoke-RestMethod -Method POST \ 
	-Uri "http://localhost:8000/api/v1/data/generate" \ 
	-ContentType "application/json" \ 
	-Body $body
```

Endpoints útiles (prueba rápida):
- Lecturas: `GET http://localhost:8000/api/v1/readings?piso=1&limit=10`
- Dashboard: `GET http://localhost:8000/api/v1/dashboard/summary`
- Alertas: `GET http://localhost:8000/api/v1/alerts?limit=10`

## Frontend (opcional)
El backend ya se puede usar desde Swagger o cualquier cliente HTTP. Si quieres la UI web:
```powershell
cd .\frontend
npm install --prefer-offline --no-audit --no-fund
npm run dev
```
Abre `http://localhost:5173` (la app apunta por defecto a `http://localhost:8000`).

## Tips y solución rápida de problemas
- Si `backend` intenta arrancar antes de que Postgres esté listo, espera unos segundos y revisa logs:
	```powershell
	docker compose logs -f backend
	```
- Para reiniciar la base limpia (borra datos locales):
	```powershell
	docker compose down
	Remove-Item -Recurse -Force .\data\db -ErrorAction SilentlyContinue
	docker compose up -d --build
	docker compose exec backend python init_db.py
	```
- Variables externas (opcional): puedes definir `GEMINI_API_KEY` si usas recomendaciones IA.

## Estructura rápida
- Backend FastAPI en `backend/` (Swagger en `/docs`).
- Postgres y Redis orquestados vía `docker-compose.yml`.
- Frontend React/Vite en `frontend/` (API base `http://localhost:8000`).

¡Eso es todo! Con lo anterior deberías tener API funcional en ~3–5 minutos.