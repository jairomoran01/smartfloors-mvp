from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import List, Optional


class LecturaCreate(BaseModel):
    timestamp: datetime
    edificio: str = Field(default="A", max_length=10)
    piso: int = Field(..., ge=1, le=3)
    temp_c: float = Field(..., ge=-50, le=50)
    humedad_pct: float = Field(..., ge=0, le=100)
    energia_kw: float = Field(..., ge=0, le=1000)
    
    @field_validator("edificio")
    @classmethod
    def validate_edificio(cls, v):
        return v.upper()


class LecturaResponse(BaseModel):
    id: int
    timestamp: datetime
    edificio: str
    piso: int
    temp_c: float
    humedad_pct: float
    energia_kw: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class LecturaBatch(BaseModel):
    readings: List[LecturaCreate]


class LecturaFilter(BaseModel):
    piso: Optional[int] = Field(None, ge=1, le=3)
    start: Optional[datetime] = None
    end: Optional[datetime] = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


class LecturaListResponse(BaseModel):
    data: List[LecturaResponse]
    total: int
    limit: int
    offset: int

