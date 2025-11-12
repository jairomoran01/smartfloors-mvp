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
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-gray-700 dark:text-gray-300 uppercase bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800">
          <tr>
            <th className="px-6 py-4 font-semibold">
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
            <th className="px-6 py-4 font-semibold">Piso</th>
            <th className="px-6 py-4 font-semibold">Variable</th>
            <th className="px-6 py-4 font-semibold">Nivel</th>
            <th className="px-6 py-4 font-semibold">Recomendación</th>
            <th className="px-6 py-4 font-semibold">Acciones</th>
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
                  className="border-b border-gray-100 dark:border-gray-700/50 hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors"
                >
                          <td className="px-6 py-4 text-xs font-numeric">
                            {format(new Date(alert.timestamp), 'dd/MM/yyyy HH:mm')}
                          </td>
                  <td className="px-6 py-4">
                    <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 rounded-md text-xs font-semibold">
                      Piso {alert.piso}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="capitalize font-medium text-gray-700 dark:text-gray-300">
                      {alert.variable}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <Icon className={`w-5 h-5 ${config.color}`} />
                      <span className={`capitalize font-semibold ${config.color}`}>
                        {alert.nivel}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 max-w-md">
                    <p className="truncate text-gray-700 dark:text-gray-300" title={alert.recomendacion}>
                      {alert.recomendacion}
                    </p>
                  </td>
                  <td className="px-6 py-4">
                    {alert.estado === 'activa' && (
                      <button
                        onClick={() => handleAcknowledge(alert.id)}
                        disabled={acknowledging === alert.id}
                        className="px-4 py-2 text-xs font-medium text-white bg-blue-600 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm hover:shadow-md"
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
                      <span className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-green-700 dark:text-green-400 bg-green-50 dark:bg-green-900/30 rounded-lg">
                        <CheckCircle2 className="w-4 h-4" />
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
      <div className="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-3">
            <div className={`px-3 py-1 rounded-full text-xs font-semibold ${
              alerts.length > 0 
                ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400' 
                : 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
            }`}>
              {alerts.length} {alerts.length === 1 ? 'alerta' : 'alertas'}
            </div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Registro de Alertas
            </h3>
          </div>
          <button
            onClick={() => setIsFullScreen(true)}
            className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Pantalla completa"
          >
            <Maximize2 className="w-5 h-5 text-gray-600 dark:text-gray-400" />
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

