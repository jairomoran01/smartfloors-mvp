import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.lectura import Lectura
from app.services.alert_service import AlertService


class DataGeneratorService:
    """Servicio para generar datos de ejemplo"""
    
    def __init__(self, db: Session):
        self.db = db
        self.alert_service = AlertService(db)
    
    def generate_sample_data(
        self,
        count: int = 30,
        start_time: datetime = None,
        interval_minutes: int = 1,
        scenario: str = "normal"
    ) -> List[int]:
        """Genera datos de ejemplo para los 3 pisos"""
        if start_time is None:
            # Por defecto, empezar desde hace 'count' minutos
            start_time = datetime.utcnow() - timedelta(minutes=count * interval_minutes)
        
        created_ids = []
        
        # Valores base por piso (óptimos)
        base_values = {
            1: {"temp": 24.0, "humedad": 55.0, "energia": 12.0},
            2: {"temp": 24.5, "humedad": 58.0, "energia": 13.5},
            3: {"temp": 23.5, "humedad": 52.0, "energia": 11.5}
        }
        
        for i in range(count):
            current_time = start_time + timedelta(minutes=i * interval_minutes)
            
            for piso in [1, 2, 3]:
                base = base_values[piso]
                
                # Generar valores según escenario
                if scenario == "normal":
                    # Variaciones normales alrededor de valores óptimos
                    temp = base["temp"] + random.uniform(-1.5, 1.5)
                    humedad = base["humedad"] + random.uniform(-5, 5)
                    energia = base["energia"] + random.uniform(-2, 2)
                    
                elif scenario == "stress":
                    # Condiciones de estrés (temperatura alta, consumo alto)
                    temp = base["temp"] + random.uniform(3, 6)
                    humedad = base["humedad"] + random.uniform(-8, 8)
                    energia = base["energia"] + random.uniform(5, 10)
                    
                else:  # mixed
                    # Mezcla de condiciones normales y de estrés
                    if i % 3 == 0:  # Cada tercera lectura es de estrés
                        temp = base["temp"] + random.uniform(2, 5)
                        humedad = base["humedad"] + random.uniform(-10, 10)
                        energia = base["energia"] + random.uniform(3, 8)
                    else:
                        temp = base["temp"] + random.uniform(-1, 2)
                        humedad = base["humedad"] + random.uniform(-5, 5)
                        energia = base["energia"] + random.uniform(-1, 3)
                
                # Limitar valores a rangos razonables
                temp = max(18, min(35, temp))
                humedad = max(20, min(85, humedad))
                energia = max(5, min(50, energia))
                
                # Crear lectura
                lectura = Lectura(
                    timestamp=current_time,
                    edificio="A",
                    piso=piso,
                    temp_c=round(temp, 2),
                    humedad_pct=round(humedad, 2),
                    energia_kw=round(energia, 2)
                )
                
                try:
                    self.db.add(lectura)
                    self.db.commit()
                    self.db.refresh(lectura)
                    created_ids.append(lectura.id)
                    
                    # Verificar alertas
                    self.alert_service.check_reading_alerts(lectura)
                    
                except Exception as e:
                    self.db.rollback()
                    print(f"Error creating reading for piso {piso} at {current_time}: {e}")
        
        return created_ids
    
    def import_from_json(self, readings_data: List[Dict[str, Any]]) -> tuple[int, int, List[str], List[int]]:
        """Importa lecturas desde una lista de diccionarios JSON"""
        imported = 0
        errors = 0
        error_details = []
        created_ids = []
        
        for idx, reading_data in enumerate(readings_data):
            try:
                # Validar y convertir datos
                timestamp_str = reading_data.get("timestamp")
                if isinstance(timestamp_str, str):
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                elif isinstance(timestamp_str, datetime):
                    timestamp = timestamp_str
                else:
                    raise ValueError("timestamp debe ser string ISO o datetime")
                
                lectura = Lectura(
                    timestamp=timestamp,
                    edificio=reading_data.get("edificio", "A").upper(),
                    piso=int(reading_data.get("piso", 1)),
                    temp_c=float(reading_data.get("temp_c", 0)),
                    humedad_pct=float(reading_data.get("humedad_pct", 0)),
                    energia_kw=float(reading_data.get("energia_kw", 0))
                )
                
                # Validar piso
                if lectura.piso not in [1, 2, 3]:
                    raise ValueError(f"Piso debe ser 1, 2 o 3, recibido: {lectura.piso}")
                
                self.db.add(lectura)
                self.db.commit()
                self.db.refresh(lectura)
                created_ids.append(lectura.id)
                imported += 1
                
                # Verificar alertas
                self.alert_service.check_reading_alerts(lectura)
                
            except Exception as e:
                self.db.rollback()
                errors += 1
                error_details.append(f"Lectura {idx + 1}: {str(e)}")
        
        return imported, errors, error_details, created_ids

