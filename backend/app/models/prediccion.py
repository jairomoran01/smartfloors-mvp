from sqlalchemy import Column, Integer, String, Numeric, DateTime, CheckConstraint
from sqlalchemy.sql import func
from app.database import Base


class Prediccion(Base):
    __tablename__ = "predicciones"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp_generacion = Column(DateTime(timezone=True), nullable=False)
    timestamp_prediccion = Column(DateTime(timezone=True), nullable=False, index=True)
    piso = Column(Integer, nullable=False, index=True)
    variable = Column(String(50), nullable=False)
    valor_predicho = Column(Numeric(8, 2), nullable=False)
    intervalo_confianza_min = Column(Numeric(8, 2))
    intervalo_confianza_max = Column(Numeric(8, 2))
    modelo = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint("piso IN (1, 2, 3)", name="check_piso"),
    )

