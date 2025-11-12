import { useQuery } from '@tanstack/react-query';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { getPredictions } from '../services/api';
import { format, addMinutes } from 'date-fns';
import { Maximize2, TrendingUp } from 'lucide-react';
import { useState } from 'react';
import FullScreenModal from './FullScreenModal';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

export default function PredictionChart({ piso, variable, label, unit, color }) {
  const [isFullScreen, setIsFullScreen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['predictions', piso, variable],
    queryFn: () => getPredictions(piso, 60), // 60 minutos de predicción
    refetchInterval: 60000, // Actualizar cada minuto
  });

  const predictions = data?.predictions?.[variable] || [];
  
  // Ordenar por timestamp ascendente
  const sortedPredictions = [...predictions].sort((a, b) => 
    new Date(a.timestamp) - new Date(b.timestamp)
  );

  // Función para crear gradiente
  const createGradient = (ctx, chartArea) => {
    if (!chartArea) {
      return null;
    }
    
    // Extraer RGB del color (formato: "rgb(r, g, b)")
    const rgbMatch = color.match(/\d+/g);
    if (!rgbMatch || rgbMatch.length < 3) {
      return color + '20'; // Fallback si no se puede parsear
    }
    
    const [r, g, b] = rgbMatch;
    const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
    
    // Gradiente de transparente arriba a color con opacidad abajo
    gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0.1)`);
    gradient.addColorStop(0.5, `rgba(${r}, ${g}, ${b}, 0.3)`);
    gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0.5)`);
    
    return gradient;
  };

  // Función para crear gradiente del intervalo de confianza
  const createConfidenceGradient = (ctx, chartArea) => {
    if (!chartArea) {
      return null;
    }
    
    const rgbMatch = color.match(/\d+/g);
    if (!rgbMatch || rgbMatch.length < 3) {
      return color + '10';
    }
    
    const [r, g, b] = rgbMatch;
    const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom);
    
    // Gradiente más sutil para el intervalo de confianza
    gradient.addColorStop(0, `rgba(${r}, ${g}, ${b}, 0.05)`);
    gradient.addColorStop(1, `rgba(${r}, ${g}, ${b}, 0.15)`);
    
    return gradient;
  };
  
  const chartData = {
    labels: sortedPredictions.map(p => format(new Date(p.timestamp), 'HH:mm')),
    datasets: [
      {
        label: `${label} - Predicción`,
        data: sortedPredictions.map(p => parseFloat(p.value)),
        borderColor: color,
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          return createGradient(ctx, chartArea);
        },
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 3,
        pointHoverRadius: 5,
        borderDash: [5, 5], // Línea punteada para predicciones
      },
      {
        label: `${label} - Intervalo Superior`,
        data: sortedPredictions.map(p => parseFloat(p.confidence_interval?.[1] || p.value)),
        borderColor: color + '80',
        backgroundColor: 'transparent',
        borderWidth: 1,
        pointRadius: 0,
        borderDash: [2, 2],
        fill: false,
      },
      {
        label: `${label} - Intervalo Inferior`,
        data: sortedPredictions.map(p => parseFloat(p.confidence_interval?.[0] || p.value)),
        borderColor: color + '80',
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          return createConfidenceGradient(ctx, chartArea);
        },
        borderWidth: 1,
        pointRadius: 0,
        borderDash: [2, 2],
        fill: '-1', // Rellenar entre este dataset y el anterior
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      onComplete: () => {
        // Forzar actualización del gradiente después de la animación
      },
    },
    plugins: {
      legend: {
        display: true,
        position: 'top',
      },
      tooltip: {
        mode: 'index',
        intersect: false,
        callbacks: {
          afterLabel: (context) => {
            const index = context.dataIndex;
            const pred = sortedPredictions[index];
            if (pred?.confidence_interval) {
              return `Confianza: [${pred.confidence_interval[0].toFixed(1)}, ${pred.confidence_interval[1].toFixed(1)}]`;
            }
            return '';
          },
        },
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.1)',
        },
      },
      x: {
        grid: {
          display: false,
        },
      },
    },
  };

  const chartContent = (
    <div className="relative h-full">
      {isLoading ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      ) : predictions.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-gray-500 dark:text-gray-400">
          No hay datos suficientes para generar predicciones
        </div>
      ) : (
        <Line data={chartData} options={options} />
      )}
    </div>
  );

  return (
    <>
      <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm hover:shadow transition-shadow">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <h3 className="text-base font-semibold text-gray-900 dark:text-white">
              Predicción {label}
            </h3>
            <span className="text-xs px-1.5 py-0.5 bg-purple-50 dark:bg-purple-900/20 text-purple-700 dark:text-purple-300 rounded border border-purple-200 dark:border-purple-800 font-medium">
              +60 min
            </span>
          </div>
          <button
            onClick={() => setIsFullScreen(true)}
            className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            title="Pantalla completa"
          >
            <Maximize2 className="w-4 h-4 text-gray-500 dark:text-gray-400" />
          </button>
        </div>
        <div className="h-56">{chartContent}</div>
        {predictions.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between text-xs">
              <span className="text-gray-500 dark:text-gray-400">
                Última predicción: {format(new Date(sortedPredictions[sortedPredictions.length - 1]?.timestamp), 'HH:mm')}
              </span>
                      <span className="font-semibold text-gray-700 dark:text-gray-300 font-numeric">
                        {sortedPredictions[sortedPredictions.length - 1]?.value.toFixed(1)} {unit}
                      </span>
            </div>
          </div>
        )}
      </div>

      {isFullScreen && (
        <FullScreenModal
          title={`Predicción ${label} - Piso ${piso}`}
          onClose={() => setIsFullScreen(false)}
        >
          <div className="h-[80vh]">{chartContent}</div>
        </FullScreenModal>
      )}
    </>
  );
}

