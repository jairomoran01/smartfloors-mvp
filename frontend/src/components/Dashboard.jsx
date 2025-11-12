import { useQuery } from '@tanstack/react-query';
import { useState } from 'react';
import { getDashboardSummary } from '../services/api';
import FloorCard from './FloorCard';
import TrendChart from './TrendChart';
import PredictionChart from './PredictionChart';
import ThermalRiskIndicator from './ThermalRiskIndicator';
import AlertsTable from './AlertsTable';

export default function Dashboard() {
  const [selectedPiso, setSelectedPiso] = useState(null);
  const [pisoFilter, setPisoFilter] = useState(null);
  const [nivelFilter, setNivelFilter] = useState(null);
  const [orderBy, setOrderBy] = useState('desc'); // 'asc' o 'desc'

  const { data: dashboardData, isLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: getDashboardSummary,
    refetchInterval: 30000,
  });

  const pisos = dashboardData?.pisos || [];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f5f5f5] dark:bg-gray-900">
      {/* Header con fondo de color diferente */}
      <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="max-w-[1920px] mx-auto px-6 py-5">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-semibold text-gray-900 dark:text-white mb-1">
                SmartFloors Dashboard
              </h1>
              <p className="text-gray-600 dark:text-gray-400 text-sm">
                Monitoreo de condiciones ambientales y eléctricas
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-[1920px] mx-auto px-6 py-6">
        {/* Tarjetas por Piso - Mejoradas */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {pisos.map((piso) => (
            <FloorCard
              key={piso.piso}
              piso={piso.piso}
              summary={piso}
              onViewDetails={(piso) => setSelectedPiso(piso)}
            />
          ))}
        </div>

        {/* Gráficos de Tendencia y Predicciones */}
        {selectedPiso ? (
          <div className="mb-8 space-y-6">
            {/* Header de sección con breadcrumb */}
            <div className="flex items-center justify-between bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700 mb-4">
              <div className="flex items-center gap-3">
                <button
                  onClick={() => setSelectedPiso(null)}
                  className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  title="Volver"
                >
                  <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                    Análisis Detallado - Piso {selectedPiso}
                  </h2>
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    Visualización completa de métricas y predicciones
                  </p>
                </div>
              </div>
            </div>
            
            {/* Indicador de Riesgo Térmico */}
            <ThermalRiskIndicator piso={selectedPiso} />

            {/* Gráficos de Tendencia Histórica */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm border border-gray-200 dark:border-gray-700 mb-4">
              <div className="flex items-center gap-2 mb-5">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Tendencia Histórica
                </h3>
                <span className="text-xs text-gray-500 dark:text-gray-400">(Últimas 4 horas)</span>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <TrendChart
                  piso={selectedPiso}
                  variable="temp"
                  label="Temperatura"
                  unit="°C"
                  color="rgb(239, 68, 68)"
                />
                <TrendChart
                  piso={selectedPiso}
                  variable="humedad"
                  label="Humedad Relativa"
                  unit="%"
                  color="rgb(59, 130, 246)"
                />
                <TrendChart
                  piso={selectedPiso}
                  variable="energia"
                  label="Energía"
                  unit="kW"
                  color="rgb(34, 197, 94)"
                />
              </div>
            </div>

            {/* Gráficos de Predicción */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm border border-gray-200 dark:border-gray-700 mb-4">
              <div className="flex items-center gap-2 mb-5">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Predicciones
                </h3>
                <span className="text-xs text-gray-500 dark:text-gray-400">(+60 minutos)</span>
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <PredictionChart
                  piso={selectedPiso}
                  variable="temperatura"
                  label="Temperatura"
                  unit="°C"
                  color="rgb(239, 68, 68)"
                />
                <PredictionChart
                  piso={selectedPiso}
                  variable="humedad"
                  label="Humedad Relativa"
                  unit="%"
                  color="rgb(59, 130, 246)"
                />
              </div>
            </div>
          </div>
        ) : (
          <div className="mb-6">
            <div className="flex items-center gap-2 mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Gráficos de Tendencia
              </h2>
              <span className="text-xs text-gray-500 dark:text-gray-400">(Últimas 4 horas)</span>
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map((piso) => (
                <div key={piso} className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow-sm border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 pb-2 border-b border-gray-200 dark:border-gray-700">
                    Piso {piso}
                  </h3>
                  <div className="space-y-4">
                    <TrendChart
                      piso={piso}
                      variable="temp"
                      label="Temperatura"
                      unit="°C"
                      color="rgb(239, 68, 68)"
                    />
                    <TrendChart
                      piso={piso}
                      variable="humedad"
                      label="Humedad"
                      unit="%"
                      color="rgb(59, 130, 246)"
                    />
                    <TrendChart
                      piso={piso}
                      variable="energia"
                      label="Energía"
                      unit="kW"
                      color="rgb(34, 197, 94)"
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tabla de Alertas con Filtros - Mejorada */}
        <div className="mb-6">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between p-5 border-b border-gray-200 dark:border-gray-700 gap-4">
              <div className="flex items-center gap-3">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
                  Sistema de Alertas
                </h2>
              </div>
              <div className="flex flex-wrap gap-3">
                {/* Filtro por Piso */}
                <div className="flex flex-col">
                  <label className="text-xs text-gray-500 dark:text-gray-400 mb-1">Piso</label>
                  <select
                    value={pisoFilter || ''}
                    onChange={(e) => setPisoFilter(e.target.value || null)}
                    className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white hover:border-gray-400 dark:hover:border-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Todos</option>
                    <option value="1">Piso 1</option>
                    <option value="2">Piso 2</option>
                    <option value="3">Piso 3</option>
                  </select>
                </div>

                {/* Filtro por Nivel */}
                <div className="flex flex-col">
                  <label className="text-xs text-gray-500 dark:text-gray-400 mb-1">Nivel</label>
                  <select
                    value={nivelFilter || ''}
                    onChange={(e) => setNivelFilter(e.target.value || null)}
                    className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white hover:border-gray-400 dark:hover:border-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Todos</option>
                    <option value="informativa">Informativa</option>
                    <option value="media">Media</option>
                    <option value="critica">Crítica</option>
                  </select>
                </div>

                {/* Filtro por Ordenamiento */}
                <div className="flex flex-col">
                  <label className="text-xs text-gray-500 dark:text-gray-400 mb-1">Ordenar por Tiempo</label>
                  <select
                    value={orderBy}
                    onChange={(e) => setOrderBy(e.target.value)}
                    className="px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white hover:border-gray-400 dark:hover:border-gray-500 transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="desc">Más recientes primero</option>
                    <option value="asc">Más antiguas primero</option>
                  </select>
                </div>
              </div>
            </div>
            <div className="p-5 pt-0">
              <AlertsTable pisoFilter={pisoFilter} nivelFilter={nivelFilter} orderBy={orderBy} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

