from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class AlertaResponse(BaseModel):
    id: UUID
    timestamp: datetime
    piso: int
    variable: str
    nivel: str
    valor_actual: Optional[float]
    umbral: Optional[float]
    recomendacion: str
    explicacion: Optional[str]
    estado: str
    created_at: datetime
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AlertaFilter(BaseModel):
    piso: Optional[int] = Field(None, ge=1, le=3)
    nivel: Optional[str] = Field(None, pattern="^(informativa|media|critica)$")
    estado: Optional[str] = Field(None, pattern="^(activa|reconocida|resuelta)$")
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class AlertaListResponse(BaseModel):
    alerts: List[AlertaResponse]
    total: int
    limit: int
    offset: int


class AlertaAcknowledgeResponse(BaseModel):
    message: str
    alert_id: UUID
    acknowledged_at: datetime

