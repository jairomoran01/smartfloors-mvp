# SmartFloors Frontend

Dashboard web para el sistema de monitoreo SmartFloors desarrollado con React, Chart.js y Tailwind CSS.

## Características

- ✅ Tarjetas de estado por piso (OK/Informativa/Media/Crítica)
- ✅ Gráficos de tendencia en tiempo real (Temperatura, Humedad, Energía)
- ✅ Tabla de alertas con filtros
- ✅ Modo pantalla completa para cada componente
- ✅ Diseño responsive
- ✅ Tema oscuro/claro automático
- ✅ Actualización automática cada 30 segundos

## Instalación

```bash
npm install
```

## Configuración

Crear archivo `.env` en la raíz del frontend:

```env
VITE_API_URL=http://localhost:8000
```

## Ejecución

```bash
npm run dev
```

El dashboard estará disponible en `http://localhost:5173`

## Estructura de Componentes

```
src/
├── components/
│   ├── Dashboard.jsx          # Componente principal
│   ├── FloorCard.jsx          # Tarjeta de estado por piso
│   ├── TrendChart.jsx         # Gráfico de tendencia
│   ├── AlertsTable.jsx        # Tabla de alertas
│   └── FullScreenModal.jsx    # Modal de pantalla completa
├── services/
│   └── api.js                 # Servicios de API
├── App.jsx                    # Componente raíz
└── main.jsx                   # Punto de entrada
```

## Uso

### Dashboard Principal

El dashboard muestra:
1. **Tarjetas por Piso**: Estado general de cada piso (1, 2, 3)
2. **Gráficos de Tendencia**: Últimas 4 horas de datos
3. **Tabla de Alertas**: Con filtros por piso y nivel

### Funcionalidades

- **Ver Detalles**: Click en "Ver detalles" en una tarjeta para ver gráficos específicos de ese piso
- **Pantalla Completa**: Click en el icono de maximizar en cualquier gráfico o tabla
- **Filtros**: Usar los selectores para filtrar alertas por piso y nivel
- **Reconocer Alertas**: Click en "Reconocer" en una alerta activa

## Tecnologías

- React 19
- Chart.js 4.5 + react-chartjs-2
- Tailwind CSS 4
- React Query (TanStack Query)
- Axios
- Lucide React (iconos)
- date-fns (formateo de fechas)
