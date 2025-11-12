import threading
import time
import random
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from sqlalchemy.orm import Session
from app.models.lectura import Lectura
from app.services.alert_service import AlertService
from app.database import SessionLocal


class SimulatorService:
    """Servicio para simular datos de sensores"""
    
    def __init__(self, db: Session):
        self.db = db
        self.running_simulators: Dict[UUID, Dict[str, Any]] = {}
        self.alert_service = AlertService(db)
    
    def start_simulator(
        self,
        duration_minutes: int,
        interval_seconds: int,
        scenario: str = "normal"
    ) -> UUID:
        """Inicia un simulador"""
        simulator_id = uuid4()
        
        self.running_simulators[simulator_id] = {
            "duration_minutes": duration_minutes,
            "interval_seconds": interval_seconds,
            "scenario": scenario,
            "start_time": datetime.utcnow(),
            "running": True
        }
        
        # Iniciar thread para el simulador
        thread = threading.Thread(
            target=self._run_simulator,
            args=(simulator_id,),
            daemon=True
        )
        thread.start()
        
        return simulator_id
    
    def stop_simulator(self, simulator_id: UUID) -> bool:
        """Detiene un simulador"""
        if simulator_id in self.running_simulators:
            self.running_simulators[simulator_id]["running"] = False
            return True
        return False
    
    def get_simulator_status(self, simulator_id: UUID) -> Optional[Dict[str, Any]]:
        """Obtiene estado de un simulador"""
        return self.running_simulators.get(simulator_id)
    
    def _run_simulator(self, simulator_id: UUID):
        """Ejecuta el simulador en un thread separado"""
        # Crear nueva sesión de DB para el thread
        db = SessionLocal()
        alert_service = AlertService(db)
        
        try:
            config = self.running_simulators[simulator_id]
            scenario = config["scenario"]
            interval = config["interval_seconds"]
            end_time = config["start_time"] + timedelta(minutes=config["duration_minutes"])
            
            # Obtener última lectura para cada piso como base
            base_readings = {}
            for piso in [1, 2, 3]:
                last_reading = db.query(Lectura).filter(
                    Lectura.piso == piso
                ).order_by(Lectura.timestamp.desc()).first()
                
                if last_reading:
                    base_readings[piso] = {
                        "temp": float(last_reading.temp_c),
                        "humedad": float(last_reading.humedad_pct),
                        "energia": float(last_reading.energia_kw)
                    }
                else:
                    # Valores iniciales por defecto
                    base_readings[piso] = {
                        "temp": 24.0 + random.uniform(-1, 1),
                        "humedad": 55.0 + random.uniform(-5, 5),
                        "energia": 12.0 + random.uniform(-2, 2)
                    }
            
            iteration = 0
            
            while config["running"] and datetime.utcnow() < end_time:
                current_time = datetime.utcnow()
                
                for piso in [1, 2, 3]:
                    base = base_readings[piso]
                    
                    # Generar valores según escenario
                    if scenario == "normal":
                        temp = base["temp"] + random.uniform(-0.5, 0.5)
                        humedad = base["humedad"] + random.uniform(-2, 2)
                        energia = base["energia"] + random.uniform(-0.5, 0.5)
                    elif scenario == "stress":
                        # Simular condiciones de estrés (temperatura alta, consumo alto)
                        temp = base["temp"] + random.uniform(2, 4)
                        humedad = base["humedad"] + random.uniform(-5, 5)
                        energia = base["energia"] + random.uniform(3, 6)
                    else:  # anomaly
                        # Simular anomalías aleatorias
                        temp = base["temp"] + random.uniform(-3, 5)
                        humedad = base["humedad"] + random.uniform(-10, 10)
                        energia = base["energia"] + random.uniform(-2, 8)
                    
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
                        db.add(lectura)
                        db.commit()
                        db.refresh(lectura)
                        
                        # Verificar alertas
                        alert_service.check_reading_alerts(lectura)
                        
                        # Actualizar base para siguiente iteración
                        base_readings[piso] = {
                            "temp": temp,
                            "humedad": humedad,
                            "energia": energia
                        }
                    except Exception as e:
                        db.rollback()
                        print(f"Error creating reading: {e}")
                
                iteration += 1
                time.sleep(interval)
            
            # Marcar como completado
            if simulator_id in self.running_simulators:
                self.running_simulators[simulator_id]["running"] = False
                self.running_simulators[simulator_id]["completed"] = True
        finally:
            db.close()

