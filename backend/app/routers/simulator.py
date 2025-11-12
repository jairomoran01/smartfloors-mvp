from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.schemas.simulator import SimulatorStart, SimulatorStop, SimulatorResponse
from app.services.simulator_service import SimulatorService

router = APIRouter()


@router.post("/start", response_model=SimulatorResponse)
async def start_simulator(
    config: SimulatorStart,
    db: Session = Depends(get_db)
):
    """Inicia el simulador de datos"""
    simulator_service = SimulatorService(db)
    
    try:
        simulator_id = simulator_service.start_simulator(
            duration_minutes=config.duration_minutes,
            interval_seconds=config.interval_seconds,
            scenario=config.scenario
        )
        
        return SimulatorResponse(
            simulator_id=simulator_id,
            status="running",
            message=f"Simulador iniciado con escenario '{config.scenario}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting simulator: {str(e)}")


@router.post("/stop", response_model=dict)
async def stop_simulator(
    request: SimulatorStop,
    db: Session = Depends(get_db)
):
    """Detiene el simulador"""
    simulator_service = SimulatorService(db)
    
    stopped = simulator_service.stop_simulator(request.simulator_id)
    
    if not stopped:
        raise HTTPException(status_code=404, detail="Simulador no encontrado")
    
    return {
        "message": "Simulador detenido exitosamente",
        "simulator_id": str(request.simulator_id)
    }


@router.get("/status/{simulator_id}", response_model=dict)
async def get_simulator_status(
    simulator_id: UUID,
    db: Session = Depends(get_db)
):
    """Obtiene el estado del simulador"""
    simulator_service = SimulatorService(db)
    status = simulator_service.get_simulator_status(simulator_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Simulador no encontrado")
    
    return status

