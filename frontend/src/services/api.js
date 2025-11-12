import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Dashboard
export const getDashboardSummary = () => 
  api.get('/api/v1/dashboard/summary').then(res => res.data);

// Lecturas
export const getReadings = (params = {}) => 
  api.get('/api/v1/readings', { params }).then(res => res.data);

export const getFloorCurrent = (piso) => 
  api.get(`/api/v1/readings/floors/${piso}/current`).then(res => res.data);

// Alertas
export const getAlerts = (params = {}) => 
  api.get('/api/v1/alerts', { params }).then(res => res.data);

export const acknowledgeAlert = (alertId) => 
  api.post(`/api/v1/alerts/${alertId}/acknowledge`).then(res => res.data);

// Predicciones
export const getPredictions = (piso, horizon = 60) => 
  api.get(`/api/v1/predictions/${piso}`, { params: { horizon } }).then(res => res.data);

// Generación de Datos
export const generateSampleData = (config = {}) => 
  api.post('/api/v1/data/generate', {
    count: config.count || 30,
    interval_minutes: config.interval_minutes || 1,
    scenario: config.scenario || 'normal',
    start_time: config.start_time || undefined
  }).then(res => res.data);

export default api;

