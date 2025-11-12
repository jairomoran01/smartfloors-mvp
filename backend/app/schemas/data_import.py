from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DataImportRequest(BaseModel):
    """Esquema para importar datos desde JSON"""
    readings: List[dict] = Field(..., description="Lista de lecturas en formato JSON")
    
    class Config:
        json_schema_extra = {
            "example": {
                "readings": [
                    {
                        "timestamp": "2025-11-12T10:00:00Z",
                        "edificio": "A",
                        "piso": 1,
                        "temp_c": 24.5,
                        "humedad_pct": 60.0,
                        "energia_kw": 12.5
                    }
                ]
            }
        }


class DataImportResponse(BaseModel):
    """Respuesta de importación de datos"""
    imported: int = Field(..., description="Número de lecturas importadas exitosamente")
    errors: int = Field(..., description="Número de errores")
    error_details: List[str] = Field(default_factory=list, description="Detalles de errores")
    created_ids: List[int] = Field(default_factory=list, description="IDs de lecturas creadas")


class GenerateDataRequest(BaseModel):
    """Esquema para generar datos de ejemplo"""
    count: int = Field(default=30, ge=1, le=1000, description="Número de lecturas a generar")
    start_time: Optional[datetime] = Field(None, description="Tiempo inicial (por defecto: ahora - count minutos)")
    interval_minutes: int = Field(default=1, ge=1, le=60, description="Intervalo entre lecturas en minutos")
    scenario: str = Field(default="normal", pattern="^(normal|stress|mixed)$", description="Escenario de datos")


class GenerateDataResponse(BaseModel):
    """Respuesta de generación de datos"""
    generated: int = Field(..., description="Número de lecturas generadas")
    start_time: datetime = Field(..., description="Tiempo inicial de generación")
    end_time: datetime = Field(..., description="Tiempo final de generación")
    created_ids: List[int] = Field(default_factory=list, description="IDs de lecturas creadas")

