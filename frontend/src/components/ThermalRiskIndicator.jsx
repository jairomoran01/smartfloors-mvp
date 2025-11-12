import { useQuery } from '@tanstack/react-query';
import { getPredictions } from '../services/api';
import { AlertTriangle, CheckCircle2, AlertCircle, XCircle } from 'lucide-react';

const riskConfig = {
  normal: {
    icon: CheckCircle2,
    color: 'text-green-500',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    borderColor: 'border-green-200 dark:border-green-800',
    label: 'Normal',
    description: 'Condiciones térmicas dentro del rango óptimo',
  },
  bajo: {
    icon: AlertCircle,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
    label: 'Bajo',
    description: 'Riesgo térmico bajo, monitorear tendencias',
  },
  medio: {
    icon: AlertTriangle,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
    label: 'Medio',
    description: 'Riesgo térmico medio, requiere atención',
  },
  alto: {
    icon: XCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    borderColor: 'border-red-200 dark:border-red-800',
    label: 'Alto',
    description: 'Riesgo térmico alto, acción inmediata requerida',
  },
};

export default function ThermalRiskIndicator({ piso }) {
  const { data, isLoading } = useQuery({
    queryKey: ['predictions', piso, 'risk'],
    queryFn: () => getPredictions(piso, 60),
    refetchInterval: 60000,
  });

  const riesgo = data?.predictions?.riesgo_termico || 'normal';
  const config = riskConfig[riesgo] || riskConfig.normal;
  const Icon = config.icon;

  if (isLoading) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
        <div className="animate-pulse">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
        </div>
      </div>
    );
  }

  return (
    <div className={`relative overflow-hidden rounded-xl border-2 ${config.borderColor} ${config.bgColor} p-6 shadow-lg bg-white dark:bg-gray-800`}>
      {/* Barra decorativa superior */}
      <div className={`absolute top-0 left-0 right-0 h-1.5 ${config.borderColor.replace('border-', 'bg-')}`}></div>
      
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-xl ${config.bgColor} shadow-sm`}>
          <Icon className={`w-10 h-10 ${config.color}`} />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-semibold text-gray-600 dark:text-gray-400 mb-2 uppercase tracking-wide">
            Riesgo Térmico Predicho
          </h3>
          <p className={`text-3xl font-bold ${config.color} mb-2`}>
            {config.label}
          </p>
          <p className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed">
            {config.description}
          </p>
        </div>
      </div>
      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Basado en predicciones de temperatura y consumo energético para los próximos 60 minutos</span>
        </div>
      </div>
    </div>
  );
}

