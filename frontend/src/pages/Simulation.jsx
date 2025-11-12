import { useState } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { generateSampleData } from '../services/api';
import { Play, Loader2, CheckCircle2, AlertCircle, Activity } from 'lucide-react';

export default function Simulation() {
  const [selectedScenario, setSelectedScenario] = useState('normal');
  const [count, setCount] = useState(30);
  const queryClient = useQueryClient();

  const generateDataMutation = useMutation({
    mutationFn: generateSampleData,
    onSuccess: () => {
      // Refrescar datos después de generar
      queryClient.invalidateQueries(['dashboard-summary']);
      queryClient.invalidateQueries(['readings']);
      queryClient.invalidateQueries(['alerts']);
    },
  });

  const scenarios = [
    {
      id: 'normal',
      name: 'Normal',
      description: 'Condiciones normales con variaciones pequeñas alrededor de valores óptimos',
      icon: CheckCircle2,
      color: 'bg-green-500',
      textColor: 'text-green-700',
      bgColor: 'bg-green-50',
      darkBgColor: 'dark:bg-green-900/20',
      borderColor: 'border-green-200',
      darkBorderColor: 'dark:border-green-800',
    },
    {
      id: 'stress',
      name: 'Estrés',
      description: 'Condiciones de estrés: temperatura alta y consumo energético elevado (genera alertas)',
      icon: AlertCircle,
      color: 'bg-red-500',
      textColor: 'text-red-700',
      bgColor: 'bg-red-50',
      darkBgColor: 'dark:bg-red-900/20',
      borderColor: 'border-red-200',
      darkBorderColor: 'dark:border-red-800',
    },
    {
      id: 'mixed',
      name: 'Mixto',
      description: 'Mezcla de condiciones normales y de estrés para análisis variado',
      icon: Activity,
      color: 'bg-yellow-500',
      textColor: 'text-yellow-700',
      bgColor: 'bg-yellow-50',
      darkBgColor: 'dark:bg-yellow-900/20',
      borderColor: 'border-yellow-200',
      darkBorderColor: 'dark:border-yellow-800',
    },
  ];

  const handleGenerate = () => {
    generateDataMutation.mutate({
      count: count,
      interval_minutes: 1,
      scenario: selectedScenario,
    });
  };

  return (
    <div className="min-h-screen bg-[#f5f5f5] dark:bg-gray-900">
      <div className="max-w-6xl mx-auto px-6 py-6">
        {/* Header */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm border border-gray-200 dark:border-gray-700 mb-6">
          <h1 className="text-2xl font-semibold text-gray-900 dark:text-white mb-1">
            Simulación de Datos
          </h1>
          <p className="text-gray-600 dark:text-gray-400 text-sm">
            Genera datos de ejemplo para los 3 pisos con diferentes escenarios
          </p>
        </div>

        {/* Selección de Escenario */}
        <div className="mb-6">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Selecciona un Escenario
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {scenarios.map((scenario) => {
              const Icon = scenario.icon;
              const isSelected = selectedScenario === scenario.id;

              return (
                <button
                  key={scenario.id}
                  onClick={() => setSelectedScenario(scenario.id)}
                  className={`p-5 rounded-lg border transition-all text-left ${
                    isSelected
                      ? `${scenario.borderColor} ${scenario.darkBorderColor} ${scenario.bgColor} ${scenario.darkBgColor} border-2 shadow-sm`
                      : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600 hover:shadow-sm'
                  }`}
                >
                  <div className="flex items-start gap-4">
                    <div
                      className={`p-3 rounded-lg ${
                        isSelected
                          ? `${scenario.color} text-white`
                          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                      }`}
                    >
                      <Icon className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <h3
                        className={`text-lg font-semibold mb-2 ${
                          isSelected
                            ? scenario.textColor
                            : 'text-gray-900 dark:text-white'
                        }`}
                      >
                        {scenario.name}
                      </h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {scenario.description}
                      </p>
                    </div>
                    {isSelected && (
                      <div className="flex-shrink-0">
                        <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center">
                          <CheckCircle2 className="w-4 h-4 text-white" />
                        </div>
                      </div>
                    )}
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Configuración */}
        <div className="mb-6 bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm border border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
            Configuración
          </h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Número de lecturas por piso
              </label>
              <input
                type="number"
                min="1"
                max="1000"
                value={count}
                onChange={(e) => setCount(parseInt(e.target.value) || 30)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
                Se generarán {count * 3} lecturas en total ({count} por cada uno de los 3 pisos)
              </p>
            </div>
          </div>
        </div>

        {/* Botón de Generación */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-5 shadow-sm border border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">
                Generar Datos
              </h3>
              <p className="text-xs text-gray-600 dark:text-gray-400">
                {selectedScenario === 'normal' && 'Generará datos con condiciones normales'}
                {selectedScenario === 'stress' && 'Generará datos con condiciones de estrés (puede generar alertas)'}
                {selectedScenario === 'mixed' && 'Generará una mezcla de condiciones normales y de estrés'}
              </p>
            </div>
            <button
              onClick={handleGenerate}
              disabled={generateDataMutation.isPending}
              className="flex items-center gap-2 px-5 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white text-sm font-medium rounded-md shadow-sm hover:shadow transition-all disabled:cursor-not-allowed"
            >
              {generateDataMutation.isPending ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Generando...</span>
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  <span>Generar Datos</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Resultado */}
        {generateDataMutation.isSuccess && (
          <div className="mt-4 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-5">
            <div className="flex items-center gap-3">
              <CheckCircle2 className="w-6 h-6 text-green-600 dark:text-green-400" />
              <div>
                <h3 className="text-lg font-semibold text-green-800 dark:text-green-200 mb-1">
                  Datos generados exitosamente
                </h3>
                <p className="text-sm text-green-700 dark:text-green-300">
                  Se generaron {generateDataMutation.data.generated} lecturas. 
                  Puedes ver los datos en el Dashboard.
                </p>
              </div>
            </div>
          </div>
        )}

        {generateDataMutation.isError && (
          <div className="mt-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-5">
            <div className="flex items-center gap-3">
              <AlertCircle className="w-6 h-6 text-red-600 dark:text-red-400" />
              <div>
                <h3 className="text-lg font-semibold text-red-800 dark:text-red-200 mb-1">
                  Error al generar datos
                </h3>
                <p className="text-sm text-red-700 dark:text-red-300">
                  {generateDataMutation.error?.response?.data?.detail || 'Ocurrió un error inesperado'}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

