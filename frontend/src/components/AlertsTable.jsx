import { useQuery } from '@tanstack/react-query';
import { getAlerts, acknowledgeAlert } from '../services/api';
import { format } from 'date-fns';
import { AlertCircle, AlertTriangle, XCircle, CheckCircle2, Maximize2 } from 'lucide-react';
import { useState } from 'react';
import FullScreenModal from './FullScreenModal';

const nivelConfig = {
  informativa: {
    icon: AlertCircle,
    color: 'text-blue-500',
    bgColor: 'bg-blue-50 dark:bg-blue-900/20',
  },
  media: {
    icon: AlertTriangle,
    color: 'text-yellow-500',
    bgColor: 'bg-yellow-50 dark:bg-yellow-900/20',
  },
  critica: {
    icon: XCircle,
    color: 'text-red-500',
    bgColor: 'bg-red-50 dark:bg-red-900/20',
  },
};

export default function AlertsTable({ pisoFilter, nivelFilter, orderBy = 'desc' }) {
  const [isFullScreen, setIsFullScreen] = useState(false);
  const [acknowledging, setAcknowledging] = useState(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['alerts', pisoFilter, nivelFilter, orderBy],
    queryFn: () => getAlerts({
      piso: pisoFilter || undefined,
      nivel: nivelFilter || undefined,
      order_by: orderBy,
      limit: 50,
    }),
    refetchInterval: 30000,
  });

  const alerts = data?.alerts || [];

  const handleAcknowledge = async (alertId) => {
    setAcknowledging(alertId);
    try {
      await acknowledgeAlert(alertId);
      refetch();
    } catch (error) {
      console.error('Error acknowledging alert:', error);
    } finally {
      setAcknowledging(null);
    }
  };

  const tableContent = (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="text-xs text-gray-600 dark:text-gray-400 uppercase bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-700">
          <tr>
            <th className="px-4 py-3 font-medium text-left">
              <div className="flex items-center gap-2">
                <span>Timestamp</span>
                {orderBy === 'desc' ? (
                  <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                ) : (
                  <svg className="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                )}
              </div>
            </th>
            <th className="px-4 py-3 font-medium text-left">Piso</th>
            <th className="px-4 py-3 font-medium text-left">Variable</th>
            <th className="px-4 py-3 font-medium text-left">Nivel</th>
            <th className="px-4 py-3 font-medium text-left">Recomendación</th>
            <th className="px-4 py-3 font-medium text-left">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {isLoading ? (
            <tr>
              <td colSpan="6" className="px-4 py-8 text-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              </td>
            </tr>
          ) : alerts.length === 0 ? (
            <tr>
              <td colSpan="6" className="px-4 py-8 text-center text-gray-500 dark:text-gray-400">
                No hay alertas
              </td>
            </tr>
          ) : (
            alerts.map((alert) => {
              const config = nivelConfig[alert.nivel] || nivelConfig.informativa;
              const Icon = config.icon;

              return (
                <tr
                  key={alert.id}
                  className="border-b border-gray-100 dark:border-gray-700/30 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-colors"
                >
                          <td className="px-4 py-3 text-xs font-numeric text-gray-600 dark:text-gray-400">
                            {format(new Date(alert.timestamp), 'dd/MM/yyyy HH:mm')}
                          </td>
                  <td className="px-4 py-3">
                    <span className="px-2 py-0.5 bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-300 rounded text-xs font-medium border border-blue-200 dark:border-blue-800">
                      Piso {alert.piso}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className="capitalize text-sm text-gray-700 dark:text-gray-300">
                      {alert.variable}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-1.5">
                      <Icon className={`w-4 h-4 ${config.color}`} />
                      <span className={`capitalize text-sm font-medium ${config.color}`}>
                        {alert.nivel}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-3 max-w-md">
                    <p className="truncate text-sm text-gray-600 dark:text-gray-400" title={alert.recomendacion}>
                      {alert.recomendacion}
                    </p>
                  </td>
                  <td className="px-4 py-3">
                    {alert.estado === 'activa' && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={acknowledging === alert.id}
                        className="px-3 py-1.5 text-xs font-medium text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300 bg-blue-50 hover:bg-blue-100 dark:bg-blue-900/20 dark:hover:bg-blue-900/30 rounded border border-blue-200 dark:border-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {acknowledging === alert.id ? (
                          <span className="flex items-center gap-1">
                            <div className="w-3 h-3 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                            Procesando...
                          </span>
                        ) : (
                          'Reconocer'
                        )}
                      </button>
                    )}
                    {alert.estado === 'reconocida' && (
                      <span className="flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        Reconocida
                      </span>
                    )}
                  </td>
                </tr>
              );
            })
          )}
        </tbody>
      </table>
    </div>
  );

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className={`px-2.5 py-1 rounded text-xs font-medium ${
              alerts.length > 0 
                ? 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400 border border-red-200 dark:border-red-800' 
                : 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400 border border-green-200 dark:border-green-800'
            }`}>
              {alerts.length} {alerts.length === 1 ? 'alerta' : 'alertas'}
            </div>
            <h3 className="text-base font-semibold text-gray-900 dark:text-white">
              Registro de Alertas
            </h3>
          </div>
          <button
            onClick={() => setIsFullScreen(true)}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Pantalla completa"
          >
            <Maximize2 className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        <div className="max-h-96 overflow-y-auto">{tableContent}</div>
      </div>

      {isFullScreen && (
        <FullScreenModal
          title="Tabla de Alertas"
          onClose={() => setIsFullScreen(false)}
        >
          <div className="h-[80vh] overflow-y-auto">{tableContent}</div>
        </FullScreenModal>
      )}
    </>
  );
}

