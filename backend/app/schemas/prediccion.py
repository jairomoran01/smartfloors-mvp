from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional, Dict, Any


class PrediccionPoint(BaseModel):
    timestamp: datetime
    value: float
    confidence_interval: List[float]


class PrediccionResponse(BaseModel):
    piso: int
    predictions: Dict[str, Any]
    generated_at: datetime


class PrediccionRequest(BaseModel):
    horizon: int = Field(default=60, ge=1, le=240, description="Horizonte de predicción en minutos")

