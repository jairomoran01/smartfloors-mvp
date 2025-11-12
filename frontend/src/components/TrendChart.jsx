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
import { getReadings } from '../services/api';
import { format, subHours } from 'date-fns';
import { Maximize2 } from 'lucide-react';
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

export default function TrendChart({ piso, variable, label, unit, color }) {
  const [isFullScreen, setIsFullScreen] = useState(false);

  const { data, isLoading } = useQuery({
    queryKey: ['readings', piso, variable],
    queryFn: () => getReadings({
      piso,
      start: subHours(new Date(), 4).toISOString(),
      limit: 240,
    }),
    refetchInterval: 30000,
  });

  const readings = data?.data || [];
  
  // Invertir el array para que el más antiguo esté a la izquierda y el más reciente a la derecha
  // Los datos vienen ordenados DESC del backend, necesitamos ASC para el gráfico
  const sortedReadings = [...readings].sort((a, b) => 
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
  
  const chartData = {
    labels: sortedReadings.map(r => format(new Date(r.timestamp), 'HH:mm')),
    datasets: [
      {
        label: `${label} (${unit})`,
        data: sortedReadings.map(r => {
          if (variable === 'temp') return parseFloat(r.temp_c);
          if (variable === 'humedad') return parseFloat(r.humedad_pct);
          if (variable === 'energia') return parseFloat(r.energia_kw);
          return 0;
        }),
        borderColor: color,
        backgroundColor: (context) => {
          const chart = context.chart;
          const { ctx, chartArea } = chart;
          return createGradient(ctx, chartArea);
        },
        fill: true,
        tension: 0.4,
        borderWidth: 2,
        pointRadius: 2,
        pointHoverRadius: 4,
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
      },
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
          drawBorder: false,
        },
        ticks: {
          font: {
            size: 11,
          },
          color: 'rgba(107, 114, 128, 0.8)',
        },
      },
      x: {
        grid: {
          display: false,
        },
        ticks: {
          font: {
            size: 11,
          },
          color: 'rgba(107, 114, 128, 0.8)',
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
              {label}
            </h3>
            <span className="text-xs px-1.5 py-0.5 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
              {unit}
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
      </div>

      {isFullScreen && (
        <FullScreenModal
          title={label}
          onClose={() => setIsFullScreen(false)}
        >
          <div className="h-[80vh]">{chartContent}</div>
        </FullScreenModal>
      )}
    </>
  );
}

