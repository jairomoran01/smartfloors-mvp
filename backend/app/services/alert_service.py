from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.alerta import Alerta
from app.models.lectura import Lectura
from app.models.umbral import Umbral
from app.services.ai_service import AIService


class AlertService:
    """Servicio para gestionar alertas"""
    
    def __init__(self, db: Session):
        self.db = db
        self.ai_service = AIService()
    
    def get_thresholds(self, variable: str) -> List[Umbral]:
        """Obtiene umbrales activos para una variable"""
        return self.db.query(Umbral).filter(
            Umbral.variable == variable,
            Umbral.activo == True
        ).all()
    
    def check_threshold(self, value: float, threshold: Umbral) -> bool:
        """Verifica si un valor está dentro del rango del umbral (debe generar alerta)"""
        # Si tiene valor_min y valor_max: el valor debe estar dentro del rango [min, max]
        if threshold.valor_min is not None and threshold.valor_max is not None:
            return threshold.valor_min <= value <= threshold.valor_max
        # Si solo tiene valor_min: el valor debe ser >= valor_min
        elif threshold.valor_min is not None:
            return value >= threshold.valor_min
        # Si solo tiene valor_max: el valor debe ser <= valor_max
        elif threshold.valor_max is not None:
            return value <= threshold.valor_max
        # Si no tiene límites, no debería generar alerta
        return False
    
    def get_threshold_level(self, value: float, thresholds: List[Umbral]) -> Optional[Umbral]:
        """Obtiene el nivel de umbral que se excede (prioriza crítico > medio > informativa)"""
        # Ordenar por nivel de severidad
        level_order = {"critica": 3, "media": 2, "informativa": 1}
        sorted_thresholds = sorted(
            thresholds,
            key=lambda t: level_order.get(t.nivel.split("_")[0], 0),
            reverse=True
        )
        
        for threshold in sorted_thresholds:
            if self.check_threshold(value, threshold):
                return threshold
        
        return None
    
    def check_reading_alerts(self, lectura: Lectura) -> List[Alerta]:
        """Verifica y genera alertas para una lectura"""
        alerts = []
        
        # Verificar temperatura
        temp_thresholds = self.get_thresholds("temperatura")
        temp_threshold = self.get_threshold_level(float(lectura.temp_c), temp_thresholds)
        if temp_threshold:
            alert = self.create_alert(
                lectura=lectura,
                variable="temperatura",
                nivel=temp_threshold.nivel.split("_")[0],
                valor_actual=float(lectura.temp_c),
                umbral=float(temp_threshold.valor_max or temp_threshold.valor_min or 0)
            )
            if alert:
                alerts.append(alert)
        
        # Verificar humedad
        humedad_thresholds = self.get_thresholds("humedad")
        humedad_threshold = self.get_threshold_level(float(lectura.humedad_pct), humedad_thresholds)
        if humedad_threshold:
            alert = self.create_alert(
                lectura=lectura,
                variable="humedad",
                nivel=humedad_threshold.nivel.split("_")[0],
                valor_actual=float(lectura.humedad_pct),
                umbral=float(humedad_threshold.valor_max or humedad_threshold.valor_min or 0)
            )
            if alert:
                alerts.append(alert)
        
        # Verificar energía
        energia_thresholds = self.get_thresholds("energia")
        energia_threshold = self.get_threshold_level(float(lectura.energia_kw), energia_thresholds)
        if energia_threshold:
            alert = self.create_alert(
                lectura=lectura,
                variable="energia",
                nivel=energia_threshold.nivel.split("_")[0],
                valor_actual=float(lectura.energia_kw),
                umbral=float(energia_threshold.valor_max or energia_threshold.valor_min or 0)
            )
            if alert:
                alerts.append(alert)
        
        return alerts
    
    def create_alert(
        self,
        lectura: Lectura,
        variable: str,
        nivel: str,
        valor_actual: float,
        umbral: float
    ) -> Optional[Alerta]:
        """Crea una nueva alerta con recomendación de IA"""
        # Verificar si ya existe una alerta activa similar
        existing = self.db.query(Alerta).filter(
            Alerta.piso == lectura.piso,
            Alerta.variable == variable,
            Alerta.nivel == nivel,
            Alerta.estado == "activa"
        ).first()
        
        if existing:
            # Actualizar timestamp de alerta existente
            existing.timestamp = lectura.timestamp
            existing.valor_actual = valor_actual
            self.db.commit()
            return existing
        
        # Generar recomendación con IA
        recomendacion, explicacion = self.ai_service.generate_alert_recommendation(
            piso=lectura.piso,
            variable=variable,
            nivel=nivel,
            valor_actual=valor_actual,
            umbral=umbral,
            temp_c=float(lectura.temp_c),
            humedad_pct=float(lectura.humedad_pct),
            energia_kw=float(lectura.energia_kw)
        )
        
        alert = Alerta(
            timestamp=lectura.timestamp,
            piso=lectura.piso,
            variable=variable,
            nivel=nivel,
            valor_actual=valor_actual,
            umbral=umbral,
            recomendacion=recomendacion,
            explicacion=explicacion,
            estado="activa"
        )
        
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        
        return alert
    
    def get_alerts(
        self,
        piso: Optional[int] = None,
        nivel: Optional[str] = None,
        estado: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> tuple[List[Alerta], int]:
        """Obtiene alertas con filtros"""
        query = self.db.query(Alerta)
        
        if piso:
            query = query.filter(Alerta.piso == piso)
        if nivel:
            query = query.filter(Alerta.nivel == nivel)
        if estado:
            query = query.filter(Alerta.estado == estado)
        
        total = query.count()
        alerts = query.order_by(Alerta.timestamp.desc()).offset(offset).limit(limit).all()
        
        return alerts, total
    
    def acknowledge_alert(self, alert_id: str) -> Optional[Alerta]:
        """Reconoce una alerta"""
        alert = self.db.query(Alerta).filter(Alerta.id == alert_id).first()
        if not alert:
            return None
        
        alert.estado = "reconocida"
        alert.acknowledged_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(alert)
        
        return alert

