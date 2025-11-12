from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.database import get_db
from app.schemas.data_import import (
    DataImportRequest,
    DataImportResponse,
    GenerateDataRequest,
    GenerateDataResponse
)
from app.services.data_generator_service import DataGeneratorService

router = APIRouter()


@router.post("/import", response_model=DataImportResponse, status_code=201)
async def import_data(
    request: DataImportRequest,
    db: Session = Depends(get_db)
):
    """Importa datos desde un archivo JSON"""
    if not request.readings:
        raise HTTPException(status_code=400, detail="La lista de lecturas no puede estar vacía")
    
    generator_service = DataGeneratorService(db)
    
    try:
        imported, errors, error_details, created_ids = generator_service.import_from_json(
            request.readings
        )
        
        return DataImportResponse(
            imported=imported,
            errors=errors,
            error_details=error_details,
            created_ids=created_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing data: {str(e)}")


@router.post("/generate", response_model=GenerateDataResponse, status_code=201)
async def generate_sample_data(
    request: GenerateDataRequest,
    db: Session = Depends(get_db)
):
    """Genera datos de ejemplo para pruebas"""
    generator_service = DataGeneratorService(db)
    
    try:
        start_time = request.start_time or (datetime.utcnow() - timedelta(minutes=request.count * request.interval_minutes))
        
        created_ids = generator_service.generate_sample_data(
            count=request.count,
            start_time=start_time,
            interval_minutes=request.interval_minutes,
            scenario=request.scenario
        )
        
        end_time = start_time + timedelta(minutes=(request.count - 1) * request.interval_minutes)
        
        return GenerateDataResponse(
            generated=len(created_ids),
            start_time=start_time,
            end_time=end_time,
            created_ids=created_ids
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating data: {str(e)}")


@router.get("/export-template")
async def get_import_template():
    """Retorna un template JSON para importar datos"""
    template = {
        "readings": [
            {
                "timestamp": "2025-11-12T10:00:00Z",
                "edificio": "A",
                "piso": 1,
                "temp_c": 24.5,
                "humedad_pct": 60.0,
                "energia_kw": 12.5
            },
            {
                "timestamp": "2025-11-12T10:01:00Z",
                "edificio": "A",
                "piso": 1,
                "temp_c": 24.6,
                "humedad_pct": 60.2,
                "energia_kw": 12.6
            }
        ]
    }
    
    from fastapi.responses import JSONResponse
    return JSONResponse(content=template)

