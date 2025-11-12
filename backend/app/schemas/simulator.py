from pydantic import BaseModel, Field
from typing import Literal
from uuid import UUID


class SimulatorStart(BaseModel):
    duration_minutes: int = Field(default=120, ge=1, le=1440)
    interval_seconds: int = Field(default=60, ge=10, le=3600)
    scenario: Literal["normal", "stress", "anomaly"] = Field(default="normal")


class SimulatorResponse(BaseModel):
    simulator_id: UUID
    status: str
    message: str

