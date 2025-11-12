from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.schemas.alerta import AlertaResponse


class MetricasPiso(BaseModel):
    temp_avg: float
    temp_max: float
    temp_min: float
    humedad_avg: float
    energia_avg: float
    energia_total: float


class PisoSummary(BaseModel):
    piso: int
    estado: str
    resumen: str
    metricas: MetricasPiso
    alertas_activas: int
    ultima_lectura: Optional[datetime]


class DashboardSummary(BaseModel):
    pisos: List[PisoSummary]
    alertas_recientes: List[AlertaResponse]
    timestamp: datetime


class FloorCurrentResponse(BaseModel):
    piso: int
    temp_C: float
    humedad_pct: float
    energia_kW: float
    timestamp: datetime
    status: str

