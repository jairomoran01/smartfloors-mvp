from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.database import get_db
from app.models.lectura import Lectura
from app.schemas.lectura import (
    LecturaCreate,
    LecturaResponse,
    LecturaBatch,
    LecturaListResponse
)
from app.schemas.dashboard import FloorCurrentResponse
from app.services.alert_service import AlertService

router = APIRouter()


@router.post("", response_model=LecturaResponse, status_code=201)
async def create_reading(
    reading: LecturaCreate,
    db: Session = Depends(get_db)
):
    """Crea una nueva lectura de sensor"""
    try:
        db_reading = Lectura(**reading.model_dump())
        db.add(db_reading)
        db.commit()
        db.refresh(db_reading)
        
        # Verificar alertas
        alert_service = AlertService(db)
        alert_service.check_reading_alerts(db_reading)
        
        return db_reading
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error creating reading: {str(e)}")


@router.post("/batch", response_model=dict, status_code=201)
async def create_readings_batch(
    batch: LecturaBatch,
    db: Session = Depends(get_db)
):
    """Crea múltiples lecturas en lote"""
    created = []
    errors = []
    
    alert_service = AlertService(db)
    
    for reading_data in batch.readings:
        try:
            db_reading = Lectura(**reading_data.model_dump())
            db.add(db_reading)
            db.commit()
            db.refresh(db_reading)
            created.append(db_reading.id)
            
            # Verificar alertas
            alert_service.check_reading_alerts(db_reading)
        except Exception as e:
            db.rollback()
            errors.append(f"Reading {reading_data.timestamp}: {str(e)}")
    
    return {
        "created": len(created),
        "errors": len(errors),
        "created_ids": created,
        "error_details": errors
    }


@router.get("", response_model=LecturaListResponse)
async def get_readings(
    piso: Optional[int] = Query(None, ge=1, le=3),
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Obtiene lecturas con filtros"""
    query = db.query(Lectura)
    
    if piso:
        query = query.filter(Lectura.piso == piso)
    if start:
        query = query.filter(Lectura.timestamp >= start)
    if end:
        query = query.filter(Lectura.timestamp <= end)
    
    total = query.count()
    readings = query.order_by(Lectura.timestamp.desc()).offset(offset).limit(limit).all()
    
    return {
        "data": readings,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.get("/floors/{piso}/current", response_model=FloorCurrentResponse)
async def get_floor_current(
    piso: int,
    db: Session = Depends(get_db)
):
    """Obtiene la lectura más reciente de un piso"""
    if piso not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Piso debe ser 1, 2 o 3")
    
    reading = db.query(Lectura).filter(
        Lectura.piso == piso
    ).order_by(Lectura.timestamp.desc()).first()
    
    if not reading:
        raise HTTPException(status_code=404, detail=f"No hay lecturas para el piso {piso}")
    
    # Determinar status basado en valores
    status = "OK"
    if float(reading.temp_c) > 28 or float(reading.energia_kw) > 20:
        status = "ALERTA"
    
    return {
        "piso": reading.piso,
        "temp_C": float(reading.temp_c),
        "humedad_pct": float(reading.humedad_pct),
        "energia_kW": float(reading.energia_kw),
        "timestamp": reading.timestamp,
        "status": status
    }

