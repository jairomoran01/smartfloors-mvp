from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.database import get_db
from app.models.lectura import Lectura
from app.models.alerta import Alerta
from app.schemas.dashboard import DashboardSummary, PisoSummary, MetricasPiso
from app.schemas.alerta import AlertaResponse

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Obtiene resumen del dashboard"""
    pisos_summary = []
    
    for piso in [1, 2, 3]:
        # Obtener métricas de las últimas 4 horas
        cutoff_time = datetime.utcnow() - timedelta(hours=4)
        
        metrics = db.query(
            func.avg(Lectura.temp_c).label("temp_avg"),
            func.max(Lectura.temp_c).label("temp_max"),
            func.min(Lectura.temp_c).label("temp_min"),
            func.avg(Lectura.humedad_pct).label("humedad_avg"),
            func.avg(Lectura.energia_kw).label("energia_avg"),
            func.sum(Lectura.energia_kw).label("energia_total")
        ).filter(
            Lectura.piso == piso,
            Lectura.timestamp >= cutoff_time
        ).first()
        
        # Última lectura
        last_reading = db.query(Lectura).filter(
            Lectura.piso == piso
        ).order_by(Lectura.timestamp.desc()).first()
        
        # Alertas activas
        active_alerts = db.query(Alerta).filter(
            Alerta.piso == piso,
            Alerta.estado == "activa"
        ).count()
        
        # Determinar estado
        estado = "OK"
        if metrics and metrics.temp_avg:
            if float(metrics.temp_avg) > 30 or active_alerts > 0:
                estado = "CRITICA"
            elif float(metrics.temp_avg) > 28 or active_alerts > 0:
                estado = "MEDIA"
            elif float(metrics.temp_avg) > 26:
                estado = "INFORMATIVA"
        
        resumen = "Condiciones normales"
        if estado != "OK":
            resumen = f"Requiere atención - {active_alerts} alerta(s) activa(s)"
        
        metricas = MetricasPiso(
            temp_avg=float(metrics.temp_avg) if metrics and metrics.temp_avg else 0.0,
            temp_max=float(metrics.temp_max) if metrics and metrics.temp_max else 0.0,
            temp_min=float(metrics.temp_min) if metrics and metrics.temp_min else 0.0,
            humedad_avg=float(metrics.humedad_avg) if metrics and metrics.humedad_avg else 0.0,
            energia_avg=float(metrics.energia_avg) if metrics and metrics.energia_avg else 0.0,
            energia_total=float(metrics.energia_total) if metrics and metrics.energia_total else 0.0
        )
        
        pisos_summary.append(PisoSummary(
            piso=piso,
            estado=estado,
            resumen=resumen,
            metricas=metricas,
            alertas_activas=active_alerts,
            ultima_lectura=last_reading.timestamp if last_reading else None
        ))
    
    # Alertas recientes (últimas 10)
    recent_alerts = db.query(Alerta).order_by(
        Alerta.timestamp.desc()
    ).limit(10).all()
    
    return DashboardSummary(
        pisos=pisos_summary,
        alertas_recientes=recent_alerts,
        timestamp=datetime.utcnow()
    )

