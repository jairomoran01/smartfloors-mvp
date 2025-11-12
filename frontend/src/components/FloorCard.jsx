import { useQuery } from '@tanstack/react-query';
import { getFloorCurrent } from '../services/api';
import { AlertCircle, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

const statusConfig = {
  OK: {
    icon: CheckCircle2,
    color: 'text-green-500',
    bgColor: 'bg-green-50 dark:bg-green-900/20',
    borderColor: 'border-green-200 dark:border-green-800',
  },
  INFORMATIVA: {
    icon: AlertCircle,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
    borderColor: 'border-blue-200 dark:border-blue-800',
  },
  MEDIA: {
    icon: AlertTriangle,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
    borderColor: 'border-yellow-200 dark:border-yellow-800',
  },
  CRITICA: {
    icon: XCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
    borderColor: 'border-red-200 dark:border-red-800',
  },
};

export default function FloorCard({ piso, summary, onViewDetails }) {
  const { data: current, isLoading } = useQuery({
    queryKey: ['floor-current', piso],
    queryFn: () => getFloorCurrent(piso),
    refetchInterval: 30000, // Actualizar cada 30 segundos
  });

  // Priorizar el status de la lectura actual sobre el summary
  // El summary puede tener datos antiguos, pero current siempre es la lectura más reciente
  const status = current?.status || summary?.estado || 'OK';
  const config = statusConfig[status] || statusConfig.OK;
  const Icon = config.icon;
  
  // Usar el resumen del summary si está disponible, sino generar uno basado en el estado actual
  const resumen = summary?.resumen || 
    (current?.status === 'OK' ? 'Condiciones normales' : 
     current?.status === 'INFORMATIVA' ? 'Condiciones ligeramente fuera del rango óptimo' :
     current?.status === 'MEDIA' ? 'Requiere atención' :
     current?.status === 'CRITICA' ? 'Acción inmediata requerida' :
     'Condiciones normales');

  return (
    <div className={`relative overflow-hidden rounded-xl border-2 ${config.borderColor} ${config.bgColor} p-6 transition-all hover:shadow-xl hover:scale-[1.02] bg-white dark:bg-gray-800 shadow-md`}>
      {/* Barra decorativa superior */}
      <div className={`absolute top-0 left-0 right-0 h-1 ${config.borderColor.replace('border-', 'bg-')}`}></div>
      
      <div className="flex items-center justify-between mb-5">
        <div className="flex items-center gap-3">
          <div className={`p-2 rounded-lg ${config.bgColor}`}>
            <Icon className={`w-6 h-6 ${config.color}`} />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white">
              Piso {piso}
            </h3>
            <span className={`text-xs font-medium ${config.color} uppercase tracking-wide`}>
              {status}
            </span>
          </div>
        </div>
      </div>

      <div className="mb-5">
        <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
          {resumen}
        </p>
      </div>

      {isLoading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div>
        </div>
      ) : current ? (
        <div className="grid grid-cols-3 gap-4 mb-5">
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wide font-medium">Temp</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white font-numeric">
              {current.temp_C?.toFixed(1) || 'N/A'}°C
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wide font-medium">Humedad</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white font-numeric">
              {current.humedad_pct?.toFixed(1) || 'N/A'}%
            </p>
          </div>
          <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-3 text-center">
            <p className="text-xs text-gray-500 dark:text-gray-400 mb-1 uppercase tracking-wide font-medium">Energía</p>
            <p className="text-lg font-bold text-gray-900 dark:text-white font-numeric">
              {current.energia_kW?.toFixed(1) || 'N/A'} kW
            </p>
          </div>
        </div>
      ) : null}

      <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${summary?.alertas_activas > 0 ? 'bg-red-500 animate-pulse' : 'bg-green-500'}`}></div>
          <span className="text-xs text-gray-500 dark:text-gray-400">
            {summary?.alertas_activas || 0} alerta(s) activa(s)
          </span>
        </div>
        <button
          onClick={() => onViewDetails?.(piso)}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors shadow-sm hover:shadow-md"
        >
          Ver detalles →
        </button>
      </div>
    </div>
  );
}

