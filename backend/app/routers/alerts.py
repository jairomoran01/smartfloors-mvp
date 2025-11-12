from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID
from app.database import get_db
from app.schemas.alerta import (
    AlertaResponse,
    AlertaListResponse,
    AlertaAcknowledgeResponse
)
from app.services.alert_service import AlertService
from datetime import datetime
import csv
from fastapi.responses import StreamingResponse
from io import StringIO

router = APIRouter()


@router.get("", response_model=AlertaListResponse)
async def get_alerts(
    piso: Optional[int] = Query(None, ge=1, le=3),
    nivel: Optional[str] = Query(None, pattern="^(informativa|media|critica)$"),
    estado: Optional[str] = Query(None, pattern="^(activa|reconocida|resuelta)$"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Obtiene alertas con filtros"""
    alert_service = AlertService(db)
    alerts, total = alert_service.get_alerts(
        piso=piso,
        nivel=nivel,
        estado=estado,
        limit=limit,
        offset=offset
    )
    
    return {
        "alerts": alerts,
        "total": total,
        "limit": limit,
        "offset": offset
    }


@router.post("/{alert_id}/acknowledge", response_model=AlertaAcknowledgeResponse)
async def acknowledge_alert(
    alert_id: UUID,
    db: Session = Depends(get_db)
):
    """Reconoce una alerta"""
    alert_service = AlertService(db)
    alert = alert_service.acknowledge_alert(str(alert_id))
    
    if not alert:
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    
    return {
        "message": "Alerta reconocida exitosamente",
        "alert_id": alert.id,
        "acknowledged_at": alert.acknowledged_at
    }


@router.get("/export")
async def export_alerts(
    piso: Optional[int] = Query(None, ge=1, le=3),
    nivel: Optional[str] = Query(None, pattern="^(informativa|media|critica)$"),
    estado: Optional[str] = Query(None, pattern="^(activa|reconocida|resuelta)$"),
    format: str = Query("csv", pattern="^(csv|json)$"),
    db: Session = Depends(get_db)
):
    """Exporta alertas en formato CSV o JSON"""
    alert_service = AlertService(db)
    alerts, total = alert_service.get_alerts(
        piso=piso,
        nivel=nivel,
        estado=estado,
        limit=10000,  # Límite alto para exportación
        offset=0
    )
    
    if format == "csv":
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            "ID", "Timestamp", "Piso", "Variable", "Nivel",
            "Valor Actual", "Umbral", "Recomendación", "Explicación", "Estado"
        ])
        
        # Data
        for alert in alerts:
            writer.writerow([
                str(alert.id),
                alert.timestamp.isoformat(),
                alert.piso,
                alert.variable,
                alert.nivel,
                alert.valor_actual,
                alert.umbral,
                alert.recomendacion,
                alert.explicacion or "",
                alert.estado
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=alertas.csv"}
        )
    else:
        # JSON format
        from fastapi.responses import JSONResponse
        return JSONResponse(content={
            "alerts": [
                {
                    "id": str(alert.id),
                    "timestamp": alert.timestamp.isoformat(),
                    "piso": alert.piso,
                    "variable": alert.variable,
                    "nivel": alert.nivel,
                    "valor_actual": alert.valor_actual,
                    "umbral": alert.umbral,
                    "recomendacion": alert.recomendacion,
                    "explicacion": alert.explicacion,
                    "estado": alert.estado
                }
                for alert in alerts
            ],
            "total": total
        })

