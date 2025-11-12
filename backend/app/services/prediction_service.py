import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.lectura import Lectura
from app.config import settings


class PredictionService:
    """Servicio para generar predicciones de temperatura y humedad"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_historical_data(self, piso: int, hours: int = 4) -> pd.DataFrame:
        """Obtiene datos históricos para un piso"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        readings = self.db.query(Lectura).filter(
            Lectura.piso == piso,
            Lectura.timestamp >= cutoff_time
        ).order_by(Lectura.timestamp.asc()).all()
        
        if not readings:
            return pd.DataFrame()
        
        data = {
            "timestamp": [r.timestamp for r in readings],
            "temp_c": [float(r.temp_c) for r in readings],
            "humedad_pct": [float(r.humedad_pct) for r in readings],
            "energia_kw": [float(r.energia_kw) for r in readings],
        }
        
        return pd.DataFrame(data)
    
    def predict_temperature(self, df: pd.DataFrame, horizon_minutes: int = 60) -> List[Dict[str, Any]]:
        """Predice temperatura usando promedio móvil simple"""
        if df.empty or len(df) < 2:
            # Si no hay datos, retornar predicción basada en último valor
            last_temp = 25.0  # Valor por defecto
            predictions = []
            base_time = datetime.utcnow()
            for i in range(horizon_minutes):
                pred_time = base_time + timedelta(minutes=i+1)
                predictions.append({
                    "timestamp": pred_time.isoformat(),
                    "value": last_temp,
                    "confidence_interval": [last_temp - 1.0, last_temp + 1.0]
                })
            return predictions
        
        # Usar promedio móvil de las últimas 5 lecturas
        window_size = min(5, len(df))
        last_temps = df["temp_c"].tail(window_size).values
        avg_temp = np.mean(last_temps)
        std_temp = np.std(last_temps) if len(last_temps) > 1 else 1.0
        
        # Calcular tendencia
        if len(df) >= 2:
            trend = (df["temp_c"].iloc[-1] - df["temp_c"].iloc[-2]) / 2.0
        else:
            trend = 0.0
        
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(horizon_minutes):
            pred_time = base_time + timedelta(minutes=i+1)
            # Predicción con ligera tendencia
            pred_value = avg_temp + (trend * (i + 1) / 60.0)
            confidence_range = std_temp * 1.5
            
            predictions.append({
                "timestamp": pred_time.isoformat(),
                "value": round(pred_value, 2),
                "confidence_interval": [
                    round(pred_value - confidence_range, 2),
                    round(pred_value + confidence_range, 2)
                ]
            })
        
        return predictions
    
    def predict_humidity(self, df: pd.DataFrame, horizon_minutes: int = 60) -> List[Dict[str, Any]]:
        """Predice humedad usando promedio móvil simple"""
        if df.empty or len(df) < 2:
            last_humidity = 60.0  # Valor por defecto
            predictions = []
            base_time = datetime.utcnow()
            for i in range(horizon_minutes):
                pred_time = base_time + timedelta(minutes=i+1)
                predictions.append({
                    "timestamp": pred_time.isoformat(),
                    "value": last_humidity,
                    "confidence_interval": [last_humidity - 5.0, last_humidity + 5.0]
                })
            return predictions
        
        window_size = min(5, len(df))
        last_humidity = df["humedad_pct"].tail(window_size).values
        avg_humidity = np.mean(last_humidity)
        std_humidity = np.std(last_humidity) if len(last_humidity) > 1 else 5.0
        
        if len(df) >= 2:
            trend = (df["humedad_pct"].iloc[-1] - df["humedad_pct"].iloc[-2]) / 2.0
        else:
            trend = 0.0
        
        predictions = []
        base_time = datetime.utcnow()
        
        for i in range(horizon_minutes):
            pred_time = base_time + timedelta(minutes=i+1)
            pred_value = avg_humidity + (trend * (i + 1) / 60.0)
            # Limitar entre 0 y 100
            pred_value = max(0, min(100, pred_value))
            confidence_range = std_humidity * 1.5
            
            predictions.append({
                "timestamp": pred_time.isoformat(),
                "value": round(pred_value, 2),
                "confidence_interval": [
                    round(max(0, pred_value - confidence_range), 2),
                    round(min(100, pred_value + confidence_range), 2)
                ]
            })
        
        return predictions
    
    def calculate_thermal_risk(self, temp_pred: float, energia_actual: float) -> str:
        """Calcula riesgo térmico combinado"""
        if temp_pred >= 30.0 or energia_actual >= 25.0:
            return "alto"
        elif temp_pred >= 28.0 or energia_actual >= 20.0:
            return "medio"
        elif temp_pred >= 26.0 or energia_actual >= 15.0:
            return "bajo"
        else:
            return "normal"
    
    def generate_predictions(self, piso: int, horizon_minutes: int = 60) -> Dict[str, Any]:
        """Genera todas las predicciones para un piso"""
        df = self.get_historical_data(piso, hours=settings.PREDICTION_WINDOW_HOURS)
        
        temp_predictions = self.predict_temperature(df, horizon_minutes)
        humidity_predictions = self.predict_humidity(df, horizon_minutes)
        
        # Calcular riesgo térmico basado en última lectura
        if not df.empty:
            last_energia = float(df["energia_kw"].iloc[-1])
            first_temp_pred = temp_predictions[0]["value"] if temp_predictions else 25.0
        else:
            last_energia = 12.0
            first_temp_pred = 25.0
        
        riesgo_termico = self.calculate_thermal_risk(first_temp_pred, last_energia)
        
        return {
            "temperatura": temp_predictions,
            "humedad": humidity_predictions,
            "riesgo_termico": riesgo_termico
        }

