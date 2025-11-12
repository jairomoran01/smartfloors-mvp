# SmartFloors Frontend

Dashboard web para el sistema de monitoreo SmartFloors (React + Vite + Tailwind + Chart.js).

## Requisitos
- Node.js 18+ (recomendado LTS actual).
- npm 9+ o pnpm/yarn (npm usado en ejemplos).
- Backend corriendo en `http://localhost:8000` (ver Quickstart del repo raíz).

## Quickstart (≤ 5 minutos)
1) Instalar dependencias
```powershell
cd "c:\Users\bymig\Desktop\HACKATON\smartfloors-mvp\frontend"
npm install --prefer-offline --no-audit --no-fund
```

2) Configurar la URL de la API (opcional)
- El frontend usa `VITE_API_URL`; si no existe, cae por defecto a `http://localhost:8000` (ver `src/services/api.js`).
- Para definirla explícitamente, crea `.env`:
```powershell
"VITE_API_URL=http://localhost:8000" | Out-File -FilePath .\.env -Encoding utf8
```

3) Ejecutar en desarrollo
```powershell
npm run dev
```
Abre `http://localhost:5173`.

Si aún no iniciaste el backend, sigue las instrucciones del `README.md` del proyecto (raíz) y vuelve aquí.

## Scripts disponibles
- `npm run dev`: inicia Vite en desarrollo (puerto 5173).
- `npm run build`: genera build de producción (dist/).
- `npm run preview`: sirve el build localmente para prueba.
- `npm run lint`: ejecuta ESLint.

## Configuración
- Variables de entorno (archivo `.env`):
	- `VITE_API_URL`: base de la API (p. ej. `http://localhost:8000`).
	- Por defecto, si no se define, se usa `http://localhost:8000`.
- Vite (ver `vite.config.js`): configuración estándar con plugins React y Tailwind.

## Estructura de componentes (resumen)
```
src/
├── components/
│   ├── Dashboard.jsx          # Componente principal
│   ├── FloorCard.jsx          # Tarjeta de estado por piso
│   ├── TrendChart.jsx         # Gráfico de tendencia
│   ├── PredictionChart.jsx    # Gráfico de predicciones por piso
│   ├── AlertsTable.jsx        # Tabla de alertas
│   ├── ThermalRiskIndicator.jsx # Indicador de riesgo térmico
│   └── FullScreenModal.jsx    # Modal de pantalla completa
├── pages/
│   └── Simulation.jsx         # Página de simulación/generación de datos
├── services/
│   └── api.js                 # Servicios HTTP (Axios)
├── App.jsx                    # Componente raíz
└── main.jsx                   # Punto de entrada
```

## Uso del Dashboard
El dashboard muestra:
1. Tarjetas por piso (1, 2, 3) con estado: OK / Informativa / Media / Crítica.
2. Gráficos de tendencia (últimas ~4 h) para temperatura, humedad y energía.
3. Tabla de alertas con filtros por piso y nivel.
4. Predicciones a +60 min (si el backend las expone).

Funciones clave:
- Ver detalles por piso desde tarjetas.
- Pantalla completa en gráficos/tablas.
- Filtros por piso/nivel.
- Reconocimiento de alertas (si el backend lo soporta).

## Producción / Deploy
Generar build y previsualizar:
```powershell
npm run build
npm run preview
```

Para Vercel/estático:
- Deploy estático del contenido de `dist/`.
- Asegúrate de configurar `VITE_API_URL` a la URL pública del backend.

## Solución de problemas
- Pantalla en blanco o datos vacíos: confirma que el backend responde en `http://localhost:8000/health`.
- CORS: el backend trae CORS abierto (`*`) para desarrollo; si cambias dominios en producción, ajusta CORS en el backend.
- 404/500 al llamar APIs: valida `VITE_API_URL` y rutas (`/api/v1/...`).
- Puerto ocupado 5173: especifica otro puerto `npm run dev -- --port 5174`.

## Tecnologías
- React 19, Vite 7.
- Tailwind CSS 4 (`@tailwindcss/vite`).
- Chart.js 4.5 + `react-chartjs-2`.
- TanStack React Query, Zustand.
- Axios, date-fns, lucide-react.
