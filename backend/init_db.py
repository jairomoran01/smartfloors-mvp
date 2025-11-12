"""
Script para inicializar la base de datos con datos iniciales
"""
from app.database import SessionLocal, engine, Base
from app.models import Lectura, Alerta, Prediccion, Umbral, Suscripcion
from sqlalchemy import text

# Crear todas las tablas
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Verificar si ya existen umbrales
    existing_thresholds = db.query(Umbral).count()
    
    if existing_thresholds == 0:
        print("Inicializando umbrales...")
        
        # Insertar umbrales según especificaciones
        umbrales_data = [
            # Temperatura
            # OK: <26°C (óptima: 24°C) - no se define umbral, es el estado normal
            {"variable": "temperatura", "nivel": "informativa", "valor_min": 26.0, "valor_max": 27.9, "descripcion": "Temperatura ligeramente elevada"},
            {"variable": "temperatura", "nivel": "media", "valor_min": 28.0, "valor_max": 29.4, "descripcion": "Temperatura alta, requiere atención"},
            {"variable": "temperatura", "nivel": "critica", "valor_min": 29.5, "valor_max": None, "descripcion": "Temperatura crítica, acción inmediata"},
            
            # Humedad
            # OK: 25-70% (óptima: 50-60%) - no se define umbral, es el estado normal
            {"variable": "humedad", "nivel": "informativa_baja", "valor_min": None, "valor_max": 24.9, "descripcion": "Humedad baja"},
            {"variable": "humedad", "nivel": "informativa_alta", "valor_min": 70.1, "valor_max": None, "descripcion": "Humedad alta"},
            {"variable": "humedad", "nivel": "media_baja", "valor_min": None, "valor_max": 21.9, "descripcion": "Humedad muy baja"},
            {"variable": "humedad", "nivel": "media_alta", "valor_min": 75.1, "valor_max": None, "descripcion": "Humedad muy alta"},
            {"variable": "humedad", "nivel": "critica_baja", "valor_min": None, "valor_max": 19.9, "descripcion": "Humedad críticamente baja"},
            {"variable": "humedad", "nivel": "critica_alta", "valor_min": 80.1, "valor_max": None, "descripcion": "Humedad críticamente alta"},
            
            # Energía
            # OK: <15kW - no se define umbral, es el estado normal
            {"variable": "energia", "nivel": "informativa", "valor_min": 15.0, "valor_max": 19.9, "descripcion": "Consumo elevado"},
            {"variable": "energia", "nivel": "media", "valor_min": 20.0, "valor_max": 24.9, "descripcion": "Consumo alto"},
            {"variable": "energia", "nivel": "critica", "valor_min": 25.0, "valor_max": None, "descripcion": "Consumo crítico"},
        ]
        
        for umbral_data in umbrales_data:
            umbral = Umbral(**umbral_data)
            db.add(umbral)
        
        db.commit()
        print(f"✅ {len(umbrales_data)} umbrales creados")
    else:
        print(f"✅ Ya existen {existing_thresholds} umbrales en la base de datos")
    
    # Crear índices adicionales si no existen
    print("Verificando índices...")
    indices_sql = [
        "CREATE INDEX IF NOT EXISTS idx_lecturas_timestamp ON lecturas(timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_lecturas_piso_timestamp ON lecturas(piso, timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_lecturas_edificio_piso ON lecturas(edificio, piso);",
        "CREATE INDEX IF NOT EXISTS idx_alertas_timestamp ON alertas(timestamp DESC);",
        "CREATE INDEX IF NOT EXISTS idx_alertas_piso_estado ON alertas(piso, estado);",
        "CREATE INDEX IF NOT EXISTS idx_alertas_nivel ON alertas(nivel);",
        "CREATE INDEX IF NOT EXISTS idx_predicciones_piso_timestamp ON predicciones(piso, timestamp_prediccion);",
    ]
    
    for sql in indices_sql:
        try:
            db.execute(text(sql))
            db.commit()
        except Exception as e:
            print(f"⚠️  Índice ya existe o error: {e}")
    
    print("✅ Base de datos inicializada correctamente")
    
except Exception as e:
    print(f"❌ Error inicializando base de datos: {e}")
    db.rollback()
finally:
    db.close()

