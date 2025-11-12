from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.prediccion import PrediccionResponse, PrediccionRequest
from app.services.prediction_service import PredictionService
from datetime import datetime

router = APIRouter()


@router.get("/{piso}", response_model=PrediccionResponse)
async def get_predictions(
    piso: int,
    horizon: int = Query(60, ge=1, le=240, description="Horizonte de predicción en minutos"),
    db: Session = Depends(get_db)
):
    """Obtiene predicciones para un piso"""
    if piso not in [1, 2, 3]:
        raise HTTPException(status_code=400, detail="Piso debe ser 1, 2 o 3")
    
    prediction_service = PredictionService(db)
    predictions = prediction_service.generate_predictions(piso, horizon)
    
    return {
        "piso": piso,
        "predictions": predictions,
        "generated_at": datetime.utcnow()
    }

